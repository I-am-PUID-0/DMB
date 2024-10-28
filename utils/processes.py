from base import *
from utils.logger import SubprocessLogger
import shlex
from concurrent.futures import ThreadPoolExecutor, as_completed


class ProcessHandler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ProcessHandler, cls).__new__(cls)
            cls._instance.init_attributes(*args, **kwargs)
            signal.signal(signal.SIGTERM, cls._instance.shutdown)
            signal.signal(signal.SIGINT, cls._instance.shutdown)
        return cls._instance

    def init_attributes(self, logger):
        self.logger = logger
        self.processes = {}
        self.process_names = {}
        self.subprocess_loggers = {}
        self.stdout = ""
        self.stderr = ""
        self.returncode = None
        self.shutting_down = False

    def start_process(
        self,
        process_name,
        config_dir,
        command,
        key_type=None,
        suppress_logging=False,
        env=None,
    ):
        try:

            def preexec_fn():
                os.setgid(group_id)
                os.setuid(user_id)

            process_description = (
                f"{process_name} w/ {key_type}" if key_type else process_name
            )
            self.logger.info(f"Starting {process_description} process")

            if isinstance(command, str):
                command = shlex.split(command)

            process_env = os.environ.copy()
            if env:
                process_env.update(env)

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                cwd=config_dir,
                universal_newlines=True,
                bufsize=1,
                preexec_fn=(
                    preexec_fn
                    if process_name
                    not in [
                        "rclone",
                        "poetry_install",
                        "install_poetry",
                        "poetry_env_setup",
                        "PostgreSQL_init",
                        "npm_install",
                        "node_build",
                        "python_env_setup",
                        "install_requirements",
                        "setup_env_and_install",
                        "dotnet_env_restore",
                        "dotnet_publish_api",
                        "dotnet_publish_scraper",
                    ]
                    else None
                ),
                env=process_env,
            )

            if not suppress_logging:
                self.subprocess_logger = SubprocessLogger(
                    self.logger, f"{process_description}"
                )
                self.subprocess_logger.start_logging_stdout(process)
                self.subprocess_logger.start_monitoring_stderr(
                    process, key_type, process_name
                )

            self.logger.info(f"{process_name} process started with PID: {process.pid}")
            self.processes[process.pid] = {
                "name": process_name,
                "description": process_description,
                "process_obj": process,
            }
            self.process_names[process_name] = process
            return process

        except Exception as e:
            self.logger.error(
                f"Error running subprocess for {process_description}: {e}"
            )
            return None

    def reap_zombies(self, signum, frame):
        while True:
            try:
                pid, _ = os.waitpid(-1, os.WNOHANG)
                if pid == 0:
                    break
                process_info = self.processes.pop(pid, {"description": "Unknown"})
                process_name = process_info.get("name")
                if process_name in self.process_names:
                    del self.process_names[process_name]
                self.logger.debug(
                    f"Reaped zombie process with PID: {pid}, "
                    f"Description: {process_info.get('description', 'Unknown')}"
                )
            except ChildProcessError:
                break

    def wait(self, process_name):
        if self.shutting_down:
            self.logger.debug(f"Skipping wait for {process_name} due to shutdown mode.")
            return
        process = self.process_names.get(process_name)
        if process:
            try:
                process.wait()
                self.returncode = process.returncode
                if process.stdout:
                    self.stdout = process.stdout.read().strip()
                if process.stderr:
                    self.stderr = process.stderr.read().strip()
            except Exception as e:
                self.logger.error(
                    f"Error while waiting for process {process_name}: {e}"
                )
            finally:
                if self.subprocess_loggers.get(process_name):
                    self.subprocess_loggers[process_name].stop_logging_stdout()
                    self.subprocess_loggers[process_name].stop_monitoring_stderr()
                del self.process_names[process_name]
                del self.processes[process.pid]
        else:
            self.logger.error(f"No process found with the name {process_name}.")

    def stop_process(self, process_name, key_type=None):
        try:
            process_description = (
                f"{process_name} w/ {key_type}" if key_type else process_name
            )
            self.logger.info(f"Initiating shutdown for {process_description}")

            process = self.process_names.get(process_name)
            if process:
                self.logger.debug(f"Process {process_name} found: {process}")
                process.terminate()
                max_attempts = 1 if process_name == "riven_backend" else 3
                attempt = 0
                while attempt < max_attempts:
                    self.logger.debug(
                        f"Waiting for {process_description} to terminate (attempt {attempt + 1})..."
                    )
                    try:
                        process.wait(timeout=10)
                        if process.poll() is None:
                            self.logger.info(
                                f"{process_description} process terminated gracefully."
                            )
                            break
                    except subprocess.TimeoutExpired:
                        self.logger.warning(
                            f"{process_description} process did not terminate within 10 seconds on attempt {attempt + 1}."
                        )
                    attempt += 1
                    time.sleep(5)
                if process.poll() is None:
                    self.logger.warning(
                        f"{process_description} process did not terminate, forcing shutdown."
                    )
                    process.kill()
                    process.wait()
                    self.logger.info(
                        f"{process_description} process forcefully terminated."
                    )
                if self.subprocess_loggers.get(process_name):
                    self.subprocess_loggers[process_name].stop_logging_stdout()
                    self.subprocess_loggers[process_name].stop_monitoring_stderr()
                    del self.subprocess_loggers[process_name]
                    self.logger.debug(f"Stopped logging for {process_description}")
                self.process_names.pop(process_name, None)
                process_info = self.processes.pop(process.pid, None)
                if process_info:
                    self.logger.debug(
                        f"Removed {process_description} with PID {process.pid} from tracking."
                    )
                self.logger.info(f"{process_description} shutdown completed.")
            else:
                self.logger.warning(
                    f"{process_description} was not found or has already been stopped."
                )
        except Exception as e:
            self.logger.error(
                f"Error occurred while stopping {process_description}: {e}"
            )

    def shutdown(self, signum=None, frame=None, exit_code=0):
        self.shutting_down = True
        self.logger.info("Shutdown signal received. Cleaning up...")
        processes_to_stop = [
            "riven_frontend",
            "riven_backend",
            "Zilean",
            "PostgreSQL",
            "Zurg",
            "rclone",
            "pgAdmin",
            "pgAgent",
        ]

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.stop_process, process_name): process_name
                for process_name in processes_to_stop
            }

            for future in as_completed(futures):
                process_name = futures[future]
                try:
                    future.result()
                    self.logger.info(f"{process_name} has been stopped successfully.")
                except Exception as e:
                    self.logger.error(f"Error stopping {process_name}: {e}")
        time.sleep(5)
        self.unmount_all()
        self.logger.info("Shutdown complete.")
        sys.exit(exit_code)

    def unmount_all(self):
        for mount_point in os.listdir(RCLONEDIR):
            full_path = os.path.join(RCLONEDIR, mount_point)
            if os.path.ismount(full_path):
                self.logger.info(f"Unmounting {full_path}...")
                umount = subprocess.run(
                    ["umount", full_path], capture_output=True, text=True
                )
                if umount.returncode == 0:
                    self.logger.info(f"Successfully unmounted {full_path}")
                else:
                    self.logger.error(
                        f"Failed to unmount {full_path}: {umount.stderr.strip()}"
                    )
