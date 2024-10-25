from base import *
from utils.logger import *
from utils.download import Downloader


class Versions:
    def __init__(self):
        self.logger = get_logger()
        self.downloader = Downloader()

    def version_check(self, process_name=None, version_path=None):
        try:
            if process_name == "riven_frontend":
                version_path = "./riven/frontend/version.txt"
            elif process_name == "riven_backend":
                version_path = "./riven/backend/pyproject.toml"
            elif process_name == "Zilean":
                version_path = "./zilean/version.txt"

            with open(version_path, "r") as f:
                if process_name == "riven_frontend":
                    version = f"v{f.read().strip()}"
                elif process_name == "riven_backend":
                    for line in f:
                        if line.startswith("version = "):
                            version = line.split("=")[1].strip().replace('"', "")
                            break
                    else:
                        version = None
                elif process_name == "Zilean":
                    version = f.read().strip()
                if version:
                    return version, None
                else:
                    return None, "Version not found"
        except Exception as e:
            self.logger.error(
                f"Error reading current version for {process_name} from {version_path}: {e}"
            )
            return None, str(e)


    def version_write(self, process_name=None, version_path=None, version=None):
        try:
            if process_name == "riven_frontend":
                version_path = "./riven/frontend/version.txt"
            elif process_name == "riven_backend":
                version_path = "./riven/backend/pyproject.toml"
            elif process_name == "Zilean":
                version_path = "./zilean/version.txt"
            if not process_name == "riven_backend":
                with open(version_path, "w") as f:
                    f.write(version)
            elif process_name == "riven_backend":
                with open(version_path, "r") as file:
                    lines = file.readlines()
                with open(version_path, "w") as f:
                    for line in lines:
                        if line.startswith("version = "):
                            f.write(f'version = "{version}"\n')
                        else:
                            f.write(line)
            return True, None
        except FileNotFoundError:
            self.logger.error(f"Version file not found: {version_path}")
            return False, f"Version file not found: {version_path}"
        except Exception as e:
            self.logger.error(
                f"Error writing current version for {process_name} to {version_path}: {e}"
            )
            return False, str(e)


    def compare_versions(self, process_name, repo_owner, repo_name):
        try:
            latest_release_version, error = self.downloader.get_latest_release(repo_owner, repo_name)
            if not latest_release_version:
                self.logger.error(
                    f"Failed to get the latest release for {process_name}: {error}"
                )
                raise Exception(error)
            current_version, error = self.version_check(process_name)
            if not current_version:
                self.logger.error(
                    f"Failed to get the current version for {process_name}: {error}"
                )
                raise Exception(error)
            if current_version == latest_release_version:
                return False, {
                    "message": "No updates available",
                    "current_version": current_version
                    }
            else:
                return True, {
                    "message": "Update available",
                    "current_version": current_version,
                    "latest_version": latest_release_version
                }
        except Exception as e:
            self.logger.error(f"Exception during version comparison {process_name}: {e}")
            return False, str(e)
