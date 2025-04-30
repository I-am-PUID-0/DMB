from utils.global_logger import logger
from utils.download import Downloader
from utils.config_loader import CONFIG_MANAGER
import subprocess, json, re


class Versions:
    def __init__(self):
        self.logger = logger
        self.downloader = Downloader()

    def version_check(
        self, process_name=None, instance_name=None, key=None, version_path=None
    ):
        try:
            if key == "dmb_api_service":
                version_path = "/pyproject.toml"
                is_file = True
            if key == "dmb_frontend":
                version_path = "/dmb/frontend/package.json"
                is_file = True
            elif key == "riven_frontend":
                version_path = "/riven/frontend/version.txt"
                is_file = True
            elif key == "cli_debrid":
                version_path = "/cli_debrid/version.txt"
                is_file = True
            elif key == "cli_battery":
                version_path = "/cli_debrid/cli_battery/version.txt"
                is_file = True
            elif key == "phalanx_db":
                version_path = "/phalanx_db/version.txt"
                is_file = True
            elif key == "riven_backend":
                version_path = "/riven/backend/pyproject.toml"
                is_file = True
            elif key == "zilean":
                version_path = "/zilean/version.txt"
                is_file = True
            elif key == "zurg":
                config = CONFIG_MANAGER.get_instance(instance_name, key)
                if not config:
                    raise ValueError(f"Configuration for {process_name} not found.")
                version_path = config.get("config_dir") + "/zurg"
                is_file = False
            elif key == "postgres":
                try:
                    result = subprocess.run(
                        ["psql", "--version"], capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        version = result.stdout.strip().split()[-1]
                        return version, None
                    return None, "psql not found or failed"
                except FileNotFoundError:
                    return None, "psql binary not found"
            elif key == "pgadmin":
                try:
                    import glob

                    version_files = glob.glob(
                        "/pgadmin/venv/lib/python*/site-packages/pgadmin4/version.py"
                    )
                    if version_files:
                        version_globals = {}
                        with open(version_files[0], "r") as f:
                            code = f.read()
                            exec(code, version_globals)
                        release = version_globals.get("APP_RELEASE")
                        revision = version_globals.get("APP_REVISION")
                        suffix = version_globals.get("APP_SUFFIX", "")
                        if release is not None and revision is not None:
                            version = f"{release}.{revision}"
                            if suffix:
                                version += f"-{suffix}"
                            return version, None
                    return None, "pgAdmin version info not found"
                except Exception as e:
                    return None, f"Error extracting pgAdmin version: {e}"
            elif key == "rclone":
                try:
                    result = subprocess.run(
                        ["rclone", "--version"], capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        version_line = result.stdout.strip().splitlines()[0]
                        version = version_line.split()[1]
                        return version, None
                    else:
                        return None, "rclone --version failed"
                except FileNotFoundError:
                    return None, "rclone binary not found"
                except Exception as e:
                    return None, f"Error reading rclone version: {e}"
            elif key == "plex_debrid":
                version_path = "/plex_debrid/ui/ui_settings.py"
                is_file = True

            if is_file:
                try:
                    with open(version_path, "r") as f:
                        if key == "dmb_frontend":
                            try:
                                data = json.load(f)
                                version = f'v{data["version"]}'
                            except (json.JSONDecodeError, KeyError) as e:
                                version = None
                        elif (
                            key == "riven_frontend"
                            or key == "cli_debrid"
                            or key == "cli_battery"
                            or key == "phalanx_db"
                        ):
                            version = f"v{f.read().strip()}"
                        elif (
                            key == "riven_backend"
                            or key == "dmb_api_service"
                            or key == "plex_debrid"
                        ):
                            for line in f:
                                if line.startswith("version = "):
                                    version_raw = (
                                        line.split("=")[1].strip().strip('"').strip("'")
                                    )
                                    match = re.search(r"v?\d+(\.\d+)*", version_raw)
                                    version = match.group(0) if match else ""
                                    break
                            else:
                                version = None
                        elif key == "zilean":
                            version = f.read().strip()
                        if version:
                            return version, None
                        else:
                            return None, "Version not found"
                except FileNotFoundError:
                    return None, f"Version file not found: {version_path}"
            if not is_file:
                try:
                    result = subprocess.run(
                        [version_path, "version"], capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        version_info = result.stdout.strip()
                        version = version_info.split("\n")[-1].split(": ")[-1]
                        return version, None
                    else:
                        return None, "Version not found"
                except FileNotFoundError:
                    return None, f"Version file not found: {version_path}"
        except Exception as e:
            self.logger.error(
                f"Error reading current version for {process_name} from {version_path}: {e}"
            )
            return None, str(e)

    def version_write(self, process_name, key=None, version_path=None, version=None):
        try:
            if key == "dmb_frontend":
                version_path = "/dmb/frontend/package.json"
            elif key == "riven_frontend":
                version_path = "/riven/frontend/version.txt"
            elif key == "riven_backend":
                version_path = "/riven/backend/pyproject.toml"
            elif key == "zilean":
                version_path = "/zilean/version.txt"
            if key == "dmb_frontend":
                try:
                    with open(version_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    data["version"] = version.lstrip("v")

                    with open(version_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                        f.write("\n")
                except (json.JSONDecodeError, KeyError) as e:
                    return False, str(e)
            elif not key == "riven_backend":
                with open(version_path, "w") as f:
                    f.write(version)
            elif key == "riven_backend":
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

    def compare_versions(
        self, process_name, repo_owner, repo_name, instance_name, key, nightly=False
    ):
        try:
            latest_release_version, error = self.downloader.get_latest_release(
                repo_owner, repo_name, nightly=nightly
            )
            if not latest_release_version:
                self.logger.error(
                    f"Failed to get the latest release for {process_name}: {error}"
                )
                raise Exception(error)
            current_version, error = self.version_check(
                process_name, instance_name, key
            )
            if not current_version:
                self.logger.error(
                    f"Failed to get the current version for {process_name}: {error}"
                )
                raise Exception(error)
            if current_version == latest_release_version:
                return False, {
                    "message": "No updates available",
                    "current_version": current_version,
                }
            else:
                return True, {
                    "message": "Update available",
                    "current_version": current_version,
                    "latest_version": latest_release_version,
                }
        except Exception as e:
            self.logger.error(
                f"Exception during version comparison {process_name}: {e}"
            )
            return False, str(e)
