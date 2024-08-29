from base import *
from utils.logger import SubprocessLogger


class ProcessHandler:
    def __init__(self, logger):
        self.logger = logger
        self.process = None
        self.subprocess_logger = None
        self.stdout = ""
        self.stderr = ""
        self.returncode = None

    def start_process(self, process_name, config_dir, command, key_type=None, suppress_logging=False):
        try:
#            user_id = int(os.getenv('PUID', 1001))
#            group_id = int(os.getenv('PGID', 1001))

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
                
            if process_name in ["rclone", "poetry_install", "poetry_env_setup", "PostgreSQL", "PostgreSQL_init"]:
                self.process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True,
                    cwd=config_dir,
                    universal_newlines=True,
                    bufsize=1
                )
            else:
                self.process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True,
                    cwd=config_dir,
                    universal_newlines=True,
                    bufsize=1,
                    preexec_fn=preexec_fn 
                )
                
            if not suppress_logging:
                self.subprocess_logger = SubprocessLogger(self.logger, f"{process_description}")
                self.subprocess_logger.start_logging_stdout(self.process)
                self.subprocess_logger.start_monitoring_stderr(self.process, key_type, process_name)
            return self.process
        except Exception as e:
            self.logger.error(f"Error running subprocess for {process_description}: {e}")
            return None

    def wait(self):
        if self.process:
            self.stdout, self.stderr = self.process.communicate()
            self.returncode = self.process.returncode
            self.stdout = self.stdout.strip() if self.stdout else ""
            self.stderr = self.stderr.strip() if self.stderr else ""           
            if self.subprocess_logger:
                self.subprocess_logger.stop_logging_stdout()
                self.subprocess_logger.stop_monitoring_stderr()

    def stop_process(self, process_name, key_type=None):
        try:
            if key_type:
                self.logger.info(f"Stopping {process_name} w/ {key_type}")
                process_description = f"{process_name} w/ {key_type}"
            else:
                self.logger.info(f"Stopping {process_name}")
                process_description = f"{process_name}"
            if self.process:
                self.process.kill()
                if self.subprocess_logger:
                    self.subprocess_logger.stop_logging_stdout()
                    self.subprocess_logger.stop_monitoring_stderr()
        except Exception as e:
            self.logger.error(f"Error stopping subprocess for {process_description}: {e}")