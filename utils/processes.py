from base import *
from utils.logger import SubprocessLogger
import shlex


class ProcessHandler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ProcessHandler, cls).__new__(cls)
            cls._instance.init_attributes(*args, **kwargs)
            signal.signal(signal.SIGCHLD, cls._instance.reap_zombies)
        return cls._instance

    def init_attributes(self, logger):
        self.logger = logger
        self.processes = {}
        self.subprocess_loggers = {}
        self.stdout = ""
        self.stderr = ""
        self.returncode = None

    def __init__(self, logger):
        pass

    def reap_zombies(self, signum, frame):
        while True:
            try:
                pid, _ = os.waitpid(-1, os.WNOHANG)
                if pid == 0:
                    break
                self.logger.info(f"Reaped zombie process with PID: {pid}")
            except ChildProcessError:
                break

    def start_process(self, process_name, config_dir, command, key_type=None, suppress_logging=False, env=None):
        try:
            try:
                pwd.getpwuid(user_id)
            except KeyError:
                self.logger.error(f"UID {user_id} does not exist. Process will not start.")
                return None

            try:
                grp.getgrgid(group_id)
            except KeyError:
                self.logger.error(f"GID {group_id} does not exist. Process will not start.")
                return None

            def preexec_fn():
                os.setgid(group_id)
                os.setuid(user_id)

            if key_type is not None:
                self.logger.info(f"Starting {process_name} w/ {key_type} subprocess")
                process_description = f"{process_name} w/ {key_type}"
            else:
                self.logger.info(f"Starting {process_name} subprocess")
                process_description = f"{process_name}"

            if isinstance(command, str):
                command = shlex.split(command)

            process_env = os.environ.copy()
            if env:
                process_env.update(env)

            if process_name in ["rclone", "poetry_install", "install_poetry", "poetry_env_setup", "PostgreSQL_init", "npm_install", "node_build", "python_env_setup", "install_requirements", "setup_env_and_install", "dotnet_env_restore", "dotnet_publish_api", "dotnet_publish_scraper"]:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True,
                    cwd=config_dir,
                    universal_newlines=True,
                    bufsize=1,
                    env=process_env
                )
            else:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True,
                    cwd=config_dir,
                    universal_newlines=True,
                    bufsize=1,
                    preexec_fn=preexec_fn,
                    env=process_env
                )

            if not suppress_logging:
                self.subprocess_logger = SubprocessLogger(self.logger, f"{process_description}")
                self.subprocess_logger.start_logging_stdout(process)
                self.subprocess_logger.start_monitoring_stderr(process, key_type, process_name)

            self.logger.info(f"{process_name} process started with PID: {process.pid}")
            self.processes[process_name] = process
            return process

        except Exception as e:
            self.logger.error(f"Error running subprocess for {process_description}: {e}")
            return None

    def wait(self, process_name):
        process = self.processes.get(process_name)
        if process:
            try:
                self.stdout, self.stderr = process.communicate()
                self.returncode = process.returncode
                self.stdout = self.stdout.strip() if self.stdout else ""
                self.stderr = self.stderr.strip() if self.stderr else ""
            except Exception as e:
                self.logger.error(f"Error while waiting for process {process_name}: {e}")
            finally:
                if self.subprocess_loggers.get(process_name):
                    self.subprocess_loggers[process_name].stop_logging_stdout()
                    self.subprocess_loggers[process_name].stop_monitoring_stderr()
                del self.processes[process_name]
        else:
            self.logger.error(f"No process found with the name {process_name}.")

    def stop_process(self, process_name, key_type=None):
        try:
            process_description = f"{process_name} w/ {key_type}" if key_type else process_name
            self.logger.info(f"Stopping {process_description}")

            process = self.processes.get(process_name)
            if process:
                process.terminate()
                try:
                    process.wait(timeout=10)
                    self.logger.info(f"{process_description} process terminated gracefully.")
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"{process_description} process did not terminate gracefully, forcing stop.")
                    process.kill()
                    process.wait()
                    self.logger.info(f"{process_description} process killed forcefully.")
            
                if self.subprocess_loggers.get(process_name):
                    self.subprocess_loggers[process_name].stop_logging_stdout()
                    self.subprocess_loggers[process_name].stop_monitoring_stderr()
                    del self.subprocess_loggers[process_name]
            
                del self.processes[process_name]
            else:
                self.logger.warning(f"{process_description} process not found or already stopped.")
        except Exception as e:
            self.logger.error(f"Error stopping subprocess for {process_description}: {e}")
