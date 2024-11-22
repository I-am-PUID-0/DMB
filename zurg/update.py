from base import *
from utils.auto_update import Update
from zurg.download import (
    get_latest_release,
    download_and_unzip_release,
    get_architecture,
)


class ZurgUpdate(Update):
    def __init__(self, process_handler):
        super().__init__(process_handler)

    def auto_update(self, process_name, enable_update):
        self.logger.debug(f"ZurgUpdate: auto_update called for {process_name}")
        super().auto_update(process_name, enable_update)

    def start_process(self, process_name, config_dir=None, suppress_logging=False):
        if str(ZURGLOGLEVEL).lower() == "off":
            suppress_logging = True
            self.logger.info(f"Suppressing {process_name} logging")
        directories_to_check = ["/zurg/RD", "/zurg/AD"]

        for dir_to_check in directories_to_check:
            zurg_executable = os.path.join(dir_to_check, "zurg")
            if os.path.exists(zurg_executable):
                if dir_to_check == "/zurg/RD":
                    key_type = "RealDebrid"
                elif dir_to_check == "/zurg/AD":
                    key_type = "AllDebrid"
                command = [zurg_executable]
                self.process_handler.start_process(
                    process_name,
                    dir_to_check,
                    command,
                    key_type,
                    suppress_logging=suppress_logging,
                )

    def stop_process(self, process_name, key_type=None):
        self.process_handler.stop_process(process_name, key_type=key_type)

    def update_check(self, process_name):
        self.logger.info(f"Checking for available {process_name} updates")

        try:
            if GHTOKEN:
                repo_owner = "debridmediamanager"
                repo_name = "zurg"
            else:
                repo_owner = "debridmediamanager"
                repo_name = "zurg-testing"

            current_version = os.getenv("ZURG_CURRENT_VERSION")

            nightly = False

            if ZURGVERSION:
                if "nightly" in ZURGVERSION.lower():
                    self.logger.info(
                        f"ZURG_VERSION is set to nightly build. Checking for updates."
                    )
                    latest_release, error = get_latest_release(
                        repo_owner, repo_name, nightly=True
                    )
                    if error:
                        self.logger.error(
                            f"Failed to fetch the latest nightly {process_name} release: {error}"
                        )
                        return False
                else:
                    self.logger.info(
                        f"ZURG_VERSION is set to: {ZURGVERSION}. Automatic updates will not be applied!"
                    )
                    return False
            else:
                latest_release, error = get_latest_release(repo_owner, repo_name)
                if error:
                    self.logger.error(
                        f"Failed to fetch the latest {process_name} release: {error}"
                    )
                    return False

            self.logger.info(f"{process_name} current version: {current_version}")
            self.logger.debug(
                f"{process_name} latest available version: {latest_release}"
            )

            if current_version == latest_release:
                self.logger.info(f"{process_name} is already up to date.")
                return False
            else:
                self.logger.info(
                    f"A new version of {process_name} is available. Applying updates."
                )
                architecture = get_architecture()
                success = download_and_unzip_release(
                    repo_owner, repo_name, latest_release, architecture
                )
                if not success:
                    raise Exception(
                        f"Failed to download and extract the release for {process_name}."
                    )

                directories_to_check = ["/zurg/RD", "/zurg/AD"]
                zurg_presence = {
                    dir_to_check: os.path.exists(os.path.join(dir_to_check, "zurg"))
                    for dir_to_check in directories_to_check
                }

                for dir_to_check in directories_to_check:
                    if zurg_presence[dir_to_check]:
                        key_type = (
                            "RealDebrid" if dir_to_check == "/zurg/RD" else "AllDebrid"
                        )
                        zurg_app_base = "/zurg/zurg"
                        zurg_executable_path = os.path.join(dir_to_check, "zurg")
                        self.stop_process(process_name, key_type)
                        shutil.copy(zurg_app_base, zurg_executable_path)
                        self.start_process("Zurg", dir_to_check)
                        return True

        except Exception as e:
            self.logger.error(
                f"An error occurred in update_check for {process_name}: {e}"
            )
            return False
