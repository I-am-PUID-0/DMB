from base import *
from utils.logger import *
from update.auto_update import BaseUpdate


class RivenUpdate(BaseUpdate):
    def __init__(self):
        super().__init__()
        self.frontend_process = None
        self.backend_process = None

    def start_process(self, process_name, config_dir=None):
        directory = f"/data/{RCLONEMN}/__all__"         
        while not os.path.exists(directory):
            self.logger.info(f"Waiting for symlink directory {directory} to become available before starting Riven")
            time.sleep(10)       
        if process_name == 'Riven_frontend':
            command = ["node", "build"]
            config_dir = "./riven/frontend"
            self.logger.info(f"Starting {process_name}")
            self.frontend_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                cwd=config_dir,
                universal_newlines=True,
                bufsize=1
            )
            self.subprocess_logger = SubprocessLogger(self.logger, f"{process_name}")
            self.subprocess_logger.start_logging_stdout(self.frontend_process)
            self.subprocess_logger.start_monitoring_stderr(self.frontend_process, None, process_name)
        elif process_name == 'Riven_backend':
            command = ["poetry", "run", "python", "backend/main.py"]
            config_dir = "./riven"
            self.logger.info(f"Starting {process_name}")
            self.backend_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                cwd=config_dir,
                universal_newlines=True,
                bufsize=1
            )
            self.subprocess_logger = SubprocessLogger(self.logger, f"{process_name}")
            self.subprocess_logger.start_logging_stdout(self.backend_process)
            self.subprocess_logger.start_monitoring_stderr(self.backend_process, None, process_name)
        else:
            self.logger.error(f"Unknown process name: {process_name}")

    def update_check(self):
        self.logger.info("Checking for available Riven updates")

        try:
            with open('./riven/VERSION', 'r') as f:
                current_version = f.read().strip()
                self.logger.info(f"Currently installed [v{current_version}]")

            response = requests.get('https://raw.githubusercontent.com/rivenmedia/riven/main/VERSION', timeout=5)
            response.raise_for_status()
            latest_version = response.text.strip()

            self.logger.info(f"Latest available version [v{latest_version}]")

            if current_version != latest_version:                              
                from .download import get_latest_release
                download_release, error = get_latest_release()
                if not download_release:
                    self.logger.error(f"Failed to download update for Riven: {error}")
                else:
                    self.logger.info(f"Automatic update installed for Riven [v{latest_version}]")
                    self.logger.info("Restarting Riven")
                    if self.frontend_process:
                        self.frontend_process.kill()
                    if self.backend_process:
                        self.backend_process.kill()
                    self.start_process('Riven_frontend')
                    self.start_process('Riven_backend')
            else:
                self.logger.info("Automatic update not required for Riven")
        except Exception as e:
            self.logger.error(f"Automatic update failed for Riven: {e}")
