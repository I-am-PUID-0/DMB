from ast import Try
from os import error
from base import *
from utils.logger import *
from utils.processes import ProcessHandler
from utils.auto_update import Update
from .download import get_latest_release, get_branch, download_and_unzip_release
from .setup import riven_setup
from .settings import set_env_variables


class RivenUpdate(Update, ProcessHandler):
    def __init__(self):
        Update.__init__(self)
        ProcessHandler.__init__(self, self.logger)
        self.frontend_process = None
        self.backend_process = None

    def update_check(self, process_name):
        self.logger.info(f"Checking for available {process_name} updates")

        try:
            if process_name == 'Riven_frontend':
                version_path = "./riven/frontend/version.txt"
            else:
                version_path = "./riven/backend/pyproject.toml"

            current_version = self.get_current_version(version_path, process_name)
            if current_version is None:
                self.logger.error(f"Failed to get the current version for {process_name}")
                return

            self.logger.info(f"Currently installed [v{current_version}] for {process_name}")

            if process_name == 'Riven_frontend':
                if RFBRANCH:
                    branch = RFBRANCH.lower()
                    version_url = f"https://raw.githubusercontent.com/rivenmedia/riven-frontend/{RFBRANCH}/version.txt"
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
            
                self.logger.debug(f"Calling riven_setup for {process_name}")
                result = riven_setup(process_name)
                self.logger.debug(f"riven_setup result for {process_name}: {result}")
            
                if result is None:
                    self.logger.error(f"riven_setup returned None for {process_name}")
                    return

                success, error = result

                if not success:
                    self.logger.error(f"Failed to download update for {process_name}: {error}")
                else:
                    self.logger.info(f"Automatic update installed for {process_name} [v{latest_version}]")                    
                    if process_name == 'Riven_frontend' and self.frontend_process:
                        self.stop_process(process_name, None)
                    elif process_name == 'Riven_backend' and self.backend_process:                        
                        self.stop_process(process_name, None)
                    self.logger.info(f"Restarting {process_name}")    
                    self.start_process(process_name)
            else:
                self.logger.info(f"Automatic update not required for {process_name}")
        except Exception as e:
            self.logger.error(f"Automatic update failed for {process_name}: {e}")

    def get_current_version(self, version_path, process_name):
        try:
            with open(version_path, 'r') as f:
                if process_name == 'Riven_frontend':
                    return f.read().strip()
                elif process_name == 'Riven_backend':
                    for line in f:
                        if line.startswith("version = "):
                            return line.split("=")[1].strip().replace("\"", "")
            return None
        except Exception as e:
            self.logger.error(f"Error reading current version for {process_name} from {version_path}: {e}")
            return None

    def get_latest_version(self, version_data, process_name):
        try:
            if process_name == 'Riven_frontend':
                return version_data.strip()
            elif process_name == 'Riven_backend':
                for line in version_data.splitlines():
                    if line.startswith("version = "):
                        return line.split("=")[1].strip().replace("\"", "")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing latest version for {process_name}: {e}")
            return None

    def start_process(self, process_name, config_dir=None):
        if process_name == 'Riven_frontend':
            command = ["node", "build"]
            config_dir = "./riven/frontend"
            if not self.setup_npm_build(config_dir):
                self.logger.error(f"Failed to set up NPM build for {process_name}")
                return
            self.frontend_process = ProcessHandler.start_process(self, process_name, config_dir, command, None)
        elif process_name == 'Riven_backend':
            config_dir = "./riven/backend"
            directory = f"/data/{RCLONEMN}/__all__"
            while not os.path.exists(directory):
                self.logger.info(f"Waiting for symlink directory {directory} to become available before starting {process_name}")
                time.sleep(10)
            venv_path = self.setup_poetry_environment(config_dir)
            if not venv_path:
                self.logger.error(f"Failed to set up Poetry environment for {process_name}")
                return
            riven_python = os.path.join(venv_path, "bin", "python")
            command = [riven_python, "src/main.py"]
            self.backend_process = ProcessHandler.start_process(self, process_name, config_dir, command, None)
            from .settings import load_settings
            load_settings()

    def setup_poetry_environment(self, config_dir):
        try:
            self.logger.info(f"Setting up Poetry environment in {config_dir}")

            poetry_install_process = ProcessHandler(self.logger)
            poetry_install_process.start_process("poetry_install", config_dir, ["poetry", "install", "--no-root", "--without", "dev"])
            poetry_install_process.wait()

            if poetry_install_process.returncode != 0:
                self.logger.error(f"Error setting up Poetry environment: {poetry_install_process.stderr}")
                return False

            poetry_env_process = ProcessHandler(self.logger)
            poetry_env_process.start_process("poetry_env_setup", config_dir, ["poetry", "env", "info", "-p"])
            poetry_env_process.wait()

            if poetry_env_process.returncode != 0:
                self.logger.error(f"Error getting Poetry environment info: {poetry_env_process.stderr}")
                return False

            venv_path = '/venv'

            if not venv_path or not os.path.exists(venv_path):
                self.logger.error(f"Poetry environment setup failed, virtual environment not found at {venv_path}")
                return False
            else:
                self.logger.info("Poetry environment setup complete")
            return venv_path
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error setting up Poetry environment: {e}")
            return False

    def setup_npm_build(self, config_dir):
        try:
            self.logger.info("Setting up Riven_frontend")

            vite_config_path = os.path.join(config_dir, 'vite.config.ts')
            with open(vite_config_path, 'r') as file:
                lines = file.readlines()

            build_section_exists = any('build:' in line for line in lines)
            if not build_section_exists:
                for i, line in enumerate(lines):
                    if line.strip().startswith('export default defineConfig({'):
                        lines.insert(i + 1, '    build: {\n        minify: false\n    },\n')
                        break

            with open(vite_config_path, 'w') as file:
                file.writelines(lines)

            self.logger.debug("vite.config.ts modified to disable minification")

            npm_install_process = ProcessHandler(self.logger)
            npm_install_process.start_process("npm_install", config_dir, ["npm", "install"])
            #npm_install_process.start_process("npm_install", config_dir, ["pnpm", "install"])
            npm_install_process.wait()

            if npm_install_process.returncode != 0:
                self.logger.error(f"Error during npm install: {npm_install_process.stderr}")
                return False

            node_build_process = ProcessHandler(self.logger)
            node_build_process.start_process("node_build", config_dir, ["node", "--max-old-space-size=2048", "./node_modules/.bin/vite", "build"])
            #node_build_process.start_process("node_build", config_dir, ["pnpm", "run", "build"])
            node_build_process.wait()

            if node_build_process.returncode != 0:
                self.logger.error(f"Error during node build: {node_build_process.stderr}")
                return False

            self.logger.info("npm install and build complete")            
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error setting up npm environment: {e}")
            return False
