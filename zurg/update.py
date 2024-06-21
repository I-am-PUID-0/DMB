from base import *
from update.auto_update import BaseUpdate


class ZurgUpdate(BaseUpdate):
    def terminate_zurg_instance(self, config_dir, key_type):
        regex_pattern = re.compile(rf'{re.escape(config_dir)}/zurg.*--preload', re.IGNORECASE)
        found_process = False
        self.logger.debug(f"Attempting to terminate Zurg w/ {key_type} process")

        for proc in psutil.process_iter():
            try:
                cmdline = ' '.join(proc.cmdline())
                self.logger.debug(f"Checking process: PID={proc.pid}, Command Line='{cmdline}'")
                if regex_pattern.search(cmdline):
                    found_process = True
                    proc.kill()
                    self.logger.debug(f"Terminated Zurg process: PID={proc.pid}, Command Line='{cmdline}'")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        if not found_process:
            self.logger.debug(f"No matching Zurg w/ {key_type} processes found")
        
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
        
    def update_check(self):
        try:
            repo_owner = 'debridmediamanager'
            repo_name = 'zurg-testing'            

            if ZURGVERSION:
                self.logger.info(f"ZURG_VERSION is set to: {ZURGVERSION}. Automatic updates will not be applied!")
                return
            
            from .download import get_latest_release  
            current_version = os.getenv('ZURG_CURRENT_VERSION')
            latest_release, error = get_latest_release(repo_owner, repo_name)
            
            if error:
                self.logger.error(f"Failed to fetch the latest Zurg release: {error}")
                return
            
            self.logger.info(f"Zurg current version: {current_version}")
            self.logger.debug(f"Zurg latest available version: {latest_release}")
            
            if current_version == latest_release:
                self.logger.info("Zurg is already up to date.")
            else:
                self.logger.info("A new version of Zurg is available. Applying updates.")
                from .download import get_architecture
                architecture = get_architecture()
                from .download import download_and_unzip_release
                #base_url = 'https://github.com/debridmediamanager/zurg-testing/raw/main/releases'
                #os.environ['BASE_URL'] = base_url
                if not download_and_unzip_release(repo_owner, repo_name, latest_release, architecture):
                    raise Exception("Failed to download and extract the release.")                
                directories_to_check = ["/zurg/RD", "/zurg/AD"]
                zurg_presence = {dir_to_check: os.path.exists(os.path.join(dir_to_check, 'zurg')) for dir_to_check in directories_to_check}

                for dir_to_check in directories_to_check:
                    if zurg_presence[dir_to_check]:
                        key_type = "RealDebrid" if dir_to_check == "/zurg/RD" else "AllDebrid"
                        zurg_app_base = '/zurg/zurg'
                        zurg_executable_path = os.path.join(dir_to_check, 'zurg')
                        self.terminate_zurg_instance(dir_to_check, key_type)
                        shutil.copy(zurg_app_base, zurg_executable_path)
                        self.start_process('Zurg', dir_to_check)
                
        except Exception as e:
            self.logger.error(f"An error occurred in update_check: {e}")
