from base import *
from utils.logger import *
from utils.processes import ProcessHandler
from utils.auto_update import Update
from zurg.download import get_latest_release, download_and_unzip_release, get_architecture

class ZurgUpdate(Update, ProcessHandler):
    def __init__(self):
        Update.__init__(self)
        ProcessHandler.__init__(self, self.logger)

    def terminate_zurg_instance(self, process_name, config_dir, key_type):
        regex_pattern = re.compile(rf'{re.escape(config_dir)}/zurg.*--preload', re.IGNORECASE)
        found_process = False
        self.logger.debug(f"Attempting to terminate {process_name} w/ {key_type} process")

        for proc in psutil.process_iter():
            try:
                cmdline = ' '.join(proc.cmdline())
                self.logger.debug(f"Checking process: PID={proc.pid}, Command Line='{cmdline}'")
                if regex_pattern.search(cmdline):
                    found_process = True
                    self.process = proc
                    self.stop_process(process_name, key_type)
                    self.logger.debug(f"Terminated {process_name} w/ {key_type} process: PID={proc.pid}, Command Line='{cmdline}'")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        if not found_process:
            self.logger.debug(f"No matching {process_name} w/ {key_type} processes found")
        
    def start_process(self, process_name, config_dir=None):
        directories_to_check = ["/zurg/RD", "/zurg/AD"]

        for dir_to_check in directories_to_check:
            zurg_executable = os.path.join(dir_to_check, 'zurg')
            if os.path.exists(zurg_executable):
                if dir_to_check == "/zurg/RD":
                    key_type = "RealDebrid"
                elif dir_to_check == "/zurg/AD":
                    key_type = "AllDebrid"
                command = [zurg_executable]
                super().start_process(process_name, dir_to_check, command, key_type)    
                
    def update_check(self, process_name):
        self.logger.info(f"Checking for available {process_name} updates")
        
        try:
            if GHTOKEN:
                repo_owner = 'debridmediamanager'
                repo_name = 'zurg'
            else:
                repo_owner = 'debridmediamanager'
                repo_name = 'zurg-testing'

            current_version = os.getenv('ZURG_CURRENT_VERSION')

            nightly = False

            if ZURGVERSION:
                if "nightly" in ZURGVERSION.lower():
                    self.logger.info(f"ZURG_VERSION is set to nightly build. Checking for updates.")
                    latest_release, error = get_latest_release(repo_owner, repo_name, nightly=True)
                    if error:
                        self.logger.error(f"Failed to fetch the latest nightly {process_name} release: {error}")
                        return False                    
                else:
                    self.logger.info(f"ZURG_VERSION is set to: {ZURGVERSION}. Automatic updates will not be applied!")
                    return False
            else:
                latest_release, error = get_latest_release(repo_owner, repo_name)
                if error:
                    self.logger.error(f"Failed to fetch the latest {process_name} release: {error}")
                    return False


            self.logger.info(f"{process_name} current version: {current_version}")
            self.logger.debug(f"{process_name} latest available version: {latest_release}")

            if current_version == latest_release:
                self.logger.info(f"{process_name} is already up to date.")
                return False
            else:
                self.logger.info(f"A new version of {process_name} is available. Applying updates.")
                architecture = get_architecture()
                success = download_and_unzip_release(repo_owner, repo_name, latest_release, architecture)
                if not success:
                    raise Exception(f"Failed to download and extract the release for {process_name}.")

                directories_to_check = ["/zurg/RD", "/zurg/AD"]
                zurg_presence = {dir_to_check: os.path.exists(os.path.join(dir_to_check, 'zurg')) for dir_to_check in directories_to_check}

                for dir_to_check in directories_to_check:
                    if zurg_presence[dir_to_check]:
                        key_type = "RealDebrid" if dir_to_check == "/zurg/RD" else "AllDebrid"
                        zurg_app_base = '/zurg/zurg'
                        zurg_executable_path = os.path.join(dir_to_check, 'zurg')
                        self.stop_process(process_name, key_type)
                        shutil.copy(zurg_app_base, zurg_executable_path)
                        self.start_process('Zurg', dir_to_check)
                        return True

        except Exception as e:
            self.logger.error(f"An error occurred in update_check for {process_name}: {e}")
            return False