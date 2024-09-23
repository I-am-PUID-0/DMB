from platform import release
from venv import logger
from base import *
from utils.logger import *
from utils.auto_update import Update
from .setup import riven_setup, setup_poetry_environment, setup_npm_build

class RivenUpdate(Update):
    def __init__(self, process_handler):
        super().__init__(process_handler)

    def auto_update(self, process_name, enable_update):
        self.logger.debug(f"RivenUpdate: auto_update called for {process_name}")
        super().auto_update(process_name, enable_update)

    def update_check(self, process_name):
        self.logger.info(f"Checking for available {process_name} updates")

        try:
            if process_name == 'riven_frontend':
                version_path = "./riven/frontend/version.txt"
            else:
                version_path = "./riven/backend/pyproject.toml"

            current_version = self.get_current_version(version_path, process_name)
            if current_version is None:
                self.logger.error(f"Failed to get the current version for {process_name}")
                return

            self.logger.info(f"Currently installed [v{current_version}] for {process_name}")

            if process_name == 'riven_frontend':
                if RFBRANCH:
                    branch = RFBRANCH.lower()
                    version_url = f"https://raw.githubusercontent.com/rivenmedia/riven-frontend/{branch}/version.txt"
                else:
                    version_url = "https://raw.githubusercontent.com/rivenmedia/riven-frontend/main/version.txt"
            else:
                if RBBRANCH:
                    branch = RBBRANCH.lower()
                    version_url = f"https://raw.githubusercontent.com/rivenmedia/riven/{branch}/pyproject.toml"
                else:
                    version_url = "https://raw.githubusercontent.com/rivenmedia/riven/main/pyproject.toml"

            response = requests.get(version_url, timeout=5)
            response.raise_for_status()
            latest_version = self.get_latest_version(response.text, process_name)

            self.logger.info(f"Latest available version [v{latest_version}] for {process_name}")

            if current_version != latest_version:
                self.logger.info(f"New version available [v{latest_version}] for {process_name}. Updating...")
                release_version = f"v{latest_version}"
                self.logger.debug(f"Calling riven_setup for {process_name}")
                result = riven_setup(self.process_handler, process_name, branch='main', release_version=release_version, running_process=True)
                self.logger.debug(f"riven_setup result for {process_name}: {result}")

                if result is None:
                    self.logger.error(f"riven_setup returned None for {process_name}")
                    return

                success, error = result

                if not success:
                    self.logger.error(f"Failed to download update for {process_name}: {error}")
                else:
                    if process_name == 'riven_frontend':
                        self.stop_process(process_name, None)
                    elif process_name == 'riven_backend':
                        self.stop_process(process_name, None)
                    self.logger.info(f"Automatic update installed for {process_name} [v{latest_version}]")                        
                    self.logger.info(f"Restarting {process_name}")
                    self.start_process(process_name)
                    return True
            else:
                self.logger.info(f"Automatic update not required for {process_name}")
                return False   
        except Exception as e:
            self.logger.error(f"Automatic update failed for {process_name}: {e}")
            return False

    def get_current_version(self, version_path, process_name):
        try:
            with open(version_path, 'r') as f:
                if process_name == 'riven_frontend':
                    return f.read().strip()
                elif process_name == 'riven_backend':
                    for line in f:
                        if line.startswith("version = "):
                            return line.split("=")[1].strip().replace("\"", "")
            return None
        except Exception as e:
            self.logger.error(f"Error reading current version for {process_name} from {version_path}: {e}")
            return None

    def get_latest_version(self, version_data, process_name):
        try:
            if process_name == 'riven_frontend':
                return version_data.strip()
            elif process_name == 'riven_backend':
                for line in version_data.splitlines():
                    if line.startswith("version = "):
                        return line.split("=")[1].strip().replace("\"", "")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing latest version for {process_name}: {e}")
            return None

    def start_process(self, process_name, config_dir=None, suppress_logging=False):
        if process_name == 'riven_frontend':
            if str(FRONTENDLOGS).lower() == 'off':
                suppress_logging = True
                self.logger.info(f"Suppressing {process_name} logging")
            env = os.environ.copy()
            env["DIALECT"] = "postgres"
            command = ["node", "build"]
            config_dir = "/riven/frontend"
            self.process_handler.start_process(process_name, config_dir, command, None, suppress_logging=suppress_logging, env=env)

        elif process_name == 'riven_backend':
            if str(BACKENDLOGS).lower() == 'off':
                suppress_logging = True
                self.logger.info(f"Suppressing {process_name} logging")
            config_dir = "/riven/backend"
            directory = f"{RCLONEDIR}/{RCLONEMN}/__all__"
            while not os.path.exists(directory):
                self.logger.info(f"Waiting for symlink directory {directory} to become available before starting {process_name}")
                time.sleep(10)
            env_file_path = os.path.join(config_dir, "src", ".env")
            load_dotenv(env_file_path)
            venv_path, poetry_executable = setup_poetry_environment(self.process_handler, config_dir)
            if not venv_path or not poetry_executable:
                self.logger.error(f"Failed to set up Poetry environment for {process_name}")
                return
            riven_python = os.path.join(venv_path, "bin", "python")
            command = [riven_python, "src/main.py"]
            env = os.environ.copy()
            env["PATH"] = f"{venv_path}/bin:" + env["PATH"]
            env["POETRY_VIRTUALENVS_PATH"] = f"{config_dir}/.cache/pypoetry/virtualenvs"
            env["POETRY_CACHE_DIR"] = f"{config_dir}/.cache/pypoetry"
            self.process_handler.start_process(process_name, config_dir, command, None, suppress_logging=suppress_logging, env=env)
            from .settings import load_settings
            load_settings()

    def stop_process(self, process_name, key_type=None):
        self.process_handler.stop_process(process_name, key_type=key_type)