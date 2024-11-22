from platform import release
from sre_constants import SUCCESS
from venv import logger
from base import *
from utils.global_logger import logger
from utils.auto_update import Update
from utils.versions import Versions
from .setup import zilean_setup, setup_python_environment
from .download import get_latest_release, download_and_unzip_release


class ZileanUpdate(Update):
    def __init__(self, process_handler):
        super().__init__(process_handler)

    def auto_update(self, process_name, enable_update):
        self.logger.debug(f"ZileanUpdate: auto_update called for {process_name}")
        super().auto_update(process_name, enable_update)

    def update_check(self, process_name):
        self.logger.debug(f"ZileanUpdate: update_check called for {process_name}")
        self.logger.info(f"Checking for available {process_name} updates")
        zilean_versions = Versions()
        try:
            repo_owner = "iPromKnight"
            repo_name = "zilean"
            zilean_update_needed, zilean_update_info = zilean_versions.compare_versions(
                process_name, repo_owner, repo_name
            )
            if not zilean_update_needed:
                self.logger.info(
                    f"{zilean_update_info.get('message')} for {process_name}"
                )
            else:
                current_version = zilean_update_info.get("current_version")
                latest_version = zilean_update_info.get("latest_version")
                self.logger.info(
                    f"{zilean_update_info.get('message')} for {process_name}. "
                    f"Current version: {current_version}, updating to {latest_version}..."
                )
                release_version = latest_version
                self.stop_process(process_name, None)
                self.logger.debug(f"Calling zilean_setup for {process_name}")
                result = zilean_setup(
                    self.process_handler,
                    process_name,
                    branch="main",
                    release_version=release_version,
                    running_process=True,
                )
                self.logger.debug(f"zilean_setup result for {process_name}: {result}")

                if result is None:
                    self.logger.error(f"zilean_setup returned None for {process_name}")
                    return False

                success, error = result

                if not success:
                    self.logger.error(
                        f"Failed to download update for {process_name}: {error}"
                    )
                    return False
                self.logger.info(
                    f"Automatic update installed for {process_name} [{latest_version}]"
                )
                self.logger.info(f"Restarting {process_name}")
                self.start_process(process_name)
                zilean_version_write, zilean_version_write_message = (
                    zilean_versions.version_write(
                        process_name, version_path=None, version=release_version
                    )
                )
                if not zilean_version_write:
                    logger.error(
                        f"Failed to write version {release_version} for {process_name}: {zilean_version_write_message}"
                    )
                return True
            self.logger.debug(
                f"ZileanUpdate: update_check completed for {process_name}"
            )
        except Exception as e:
            self.logger.error(f"Automatic update failed for {process_name}: {e}")
            return False

    def start_process(self, process_name, config_dir=None, suppress_logging=False):
        if process_name == "Zilean":
            if str(ZILEANLOGS).lower() == "off":
                suppress_logging = True
                self.logger.info(f"Suppressing {process_name} logging")
            config_dir = "./zilean/app"
            command = ["./zilean-api"]
            venv_path = "/zilean/venv"
            python_lib_path = f"{venv_path}/lib"
            python_version = "3.11"
            libpython_path = f"{python_lib_path}/python{python_version}/site-packages"
            env_exports = {
                "DOTNET_RUNNING_IN_CONTAINER": "true",
                "DOTNET_gcServer": "1",
                "DOTNET_GCDynamicAdaptationMode": "1",
                "DOTNET_SYSTEM_GLOBALIZATION_INVARIANT": "true",
                "PYTHONUNBUFFERED": "1",
                "ASPNETCORE_URLS": "http://+:8182",
                "PYTHONPATH": libpython_path,
                "PATH": f"{venv_path}/bin:" + os.environ["PATH"],
                "ZILEAN_PYTHON_PYLIB": "/usr/local/lib/libpython3.11.so.1.0",
                "Zilean__Database__ConnectionString": f"Host=localhost;Port=5432;Database=zilean;Username={postgres_user};Password={postgres_password};Timeout=300;CommandTimeout=300;",
            }
            process_env = os.environ.copy()
            process_env.update(env_exports)
            self.process_handler.start_process(
                process_name,
                config_dir,
                command,
                None,
                suppress_logging=suppress_logging,
                env=process_env,
            )

    def stop_process(self, process_name, key_type=None):
        self.process_handler.stop_process(process_name, key_type=key_type)
