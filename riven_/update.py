from ast import Try
from base import *
from utils.logger import *
from utils.processes import ProcessHandler
from utils.auto_update import Update
from .download import get_latest_release

class RivenUpdate(Update, ProcessHandler):
    def __init__(self):
        Update.__init__(self)
        ProcessHandler.__init__(self, self.logger)
        self.frontend_process = None
        self.backend_process = None

    def update_check(self, process_name, branch):
        self.logger.info("Checking for available Riven updates")

        try:
            version_path = f"./riven/{process_name}/version.txt"
            with open(version_path, 'r') as f:
                current_version = f.read().strip()
                self.logger.info(f"Currently installed [v{current_version}]")

            if process_name == 'Riven_frontend':
                version_url = f"https://raw.githubusercontent.com/rivenmedia/riven-frontend/{branch}/version.txt"
            else:
                version_url = f"https://raw.githubusercontent.com/rivenmedia/riven/{branch}/version.txt"

            response = requests.get(version_url, timeout=5)
            response.raise_for_status()
            latest_version = response.text.strip()

            self.logger.info(f"Latest available version [v{latest_version}]")

            if current_version != latest_version:
                self.logger.info(f"New version available [v{latest_version}]. Updating...")
                success, error = get_latest_release(process_name, branch, f"./riven/{process_name}")
                if not success:
                    self.logger.error(f"Failed to download update for {process_name}: {error}")
                else:
                    self.logger.info(f"Automatic update installed for {process_name} [v{latest_version}]")
                    self.logger.info("Restarting Riven")
                    if process_name == 'Riven_frontend' and self.frontend_process:
                        self.stop_process(process_name, None)
                    elif process_name == 'Riven_backend' and self.backend_process:
                        self.stop_process(process_name, None)
                    self.start_process(process_name)
            else:
                self.logger.info("Automatic update not required for Riven")
        except Exception as e:
            self.logger.error(f"Automatic update failed for {process_name}: {e}")
            
    def setup_poetry_environment(self, config_dir):
        try:
            self.logger.info(f"Setting up Poetry environment in {config_dir}")
            result = subprocess.run(
                ["poetry", "install", "--no-root", "--without", "dev"],
                cwd=config_dir,
                capture_output=True,
                text=True
            )
            if result.stdout:
                self.logger.debug(f"Poetry install stdout: {result.stdout}")
            if result.stderr:
                self.logger.debug(f"Poetry install stderr: {result.stderr}")
            if result.returncode != 0:
                self.logger.error(f"Error setting up Poetry environment: {result.stderr}")
                return None
            result = subprocess.run(
                ["poetry", "env", "info", "-p"],
                cwd=config_dir,
                capture_output=True,
                text=True
            )
            venv_path = result.stdout.strip()
            if not venv_path or not os.path.exists(venv_path):
                self.logger.error(f"Poetry environment setup failed, virtual environment not found at {venv_path}")
                return None
            return venv_path
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error setting up Poetry environment: {e}")
            return None
        
    def setup_npm_build(self, config_dir):
        try:
            self.logger.info("Setting up Riven frontend")
            result = subprocess.run(["npm", "install"], cwd=config_dir, check=True, capture_output=True, text=True)
            self.logger.debug(f"npm install output: {result.stdout}")
            self.logger.debug(f"npm install errors: {result.stderr}")
        
            result = subprocess.run(["npm", "run", "build"], cwd=config_dir, check=True, capture_output=True, text=True)
            self.logger.debug(f"npm run build output: {result.stdout}")
            self.logger.debug(f"npm run build errors: {result.stderr}")
            self.logger.info("npm install complete")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error setting up npm environment: {e}")
            return None

    def start_process(self, process_name, config_dir=None):
        
        if process_name == 'Riven_frontend':
            command = ["node", "build"]
            config_dir = "./riven/frontend"
            self.setup_npm_build(config_dir)
            self.frontend_process = ProcessHandler.start_process(self, process_name, config_dir, command, None)
            
        elif process_name == 'Riven_backend':
            config_dir = "./riven/backend"
            directory = f"/data/{RCLONEMN}/__all__"
            while not os.path.exists(directory):
                self.logger.info(f"Waiting for symlink directory {directory} to become available before starting Riven")
                time.sleep(10)            
            venv_path = self.setup_poetry_environment(config_dir)            
            if not venv_path:
                self.logger.error("Failed to set up Poetry environment for Riven_backend")
                return
            riven_python = os.path.join(venv_path, "bin", "python")
            command = [riven_python, "src/main.py"]
            self.backend_process = ProcessHandler.start_process(self, process_name, config_dir, command, None)
            from .settings import load_settings
            load_settings()