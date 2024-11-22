from email import message
from base import *
from utils.global_logger import logger
from utils.versions import Versions
from utils.user_management import chown_recursive


def setup_python_environment(process_handler=None, config_dir="/zilean"):
    try:

        def run_process(name, cmd, config_dir=config_dir):
            process_handler.start_process(name, config_dir, cmd)
            process_handler.wait(name)
            if process_handler.returncode != 0:
                logger.error(f"Error in {name}: {process_handler.stderr}")
                return False
            return True

        logger.info(f"Setting up Python environment in {config_dir}")
        venv_path = f"{config_dir}/venv"
        if not run_process("python_env_setup", ["python", "-m", "venv", "venv"]):
            return False
        activate_script = os.path.abspath(f"{venv_path}/bin/activate")
        requirements_file = os.path.abspath(f"{config_dir}/requirements.txt")
        if not os.path.exists(activate_script):
            logger.error(
                f"Virtual environment not found or {activate_script} is missing."
            )
            return False
        if not os.path.exists(requirements_file):
            logger.error(f"requirements.txt not found at {requirements_file}")
            return False
        install_cmd = f"""
            . {activate_script} && pip install -r {requirements_file}
        """
        if not run_process("install_requirements", ["/bin/sh", "-c", install_cmd]):
            return False
        logger.info("Python environment setup and requirements installation complete")
        return venv_path

    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting up Python environment: {e}")
        return False


def setup_dotnet_environment(process_handler=None, config_dir="./zilean"):
    try:
        logger.info(f"Setting up .NET environment in {config_dir}")

        dotnet_env_process = process_handler

        dotnet_env_process.start_process(
            "dotnet_env_restore", config_dir, ["dotnet", "restore"]
        )
        dotnet_env_process.wait("dotnet_env_restore")
        if dotnet_env_process.returncode != 0:
            logger.error(f"Error running dotnet restore: {dotnet_env_process.stderr}")
            return False

        dotnet_env_process.start_process(
            "dotnet_publish_api",
            config_dir,
            [
                "dotnet",
                "publish",
                "/zilean/src/Zilean.ApiService",
                "-c",
                "Release",
                "--no-restore",
                "-o",
                "/zilean/app/",
            ],
        )
        dotnet_env_process.wait("dotnet_publish_api")
        if dotnet_env_process.returncode != 0:
            logger.error(
                f"Error publishing Zilean.ApiService: {dotnet_env_process.stderr}"
            )
            return False

        project_path_primary = "/zilean/src/Zilean.Scraper"
        project_path_secondary = "/zilean/src/Zilean.DmmScraper"
        if os.path.exists(project_path_primary):
            scraper_project_path = project_path_primary
        elif os.path.exists(project_path_secondary):
            scraper_project_path = project_path_secondary
        else:
            raise FileNotFoundError(
                f"Neither {project_path_primary} nor {project_path_secondary} exists."
            )
        dotnet_env_process.start_process(
            "dotnet_publish_scraper",
            config_dir,
            [
                "dotnet",
                "publish",
                scraper_project_path,
                "-c",
                "Release",
                "--no-restore",
                "-o",
                "/zilean/app/",
            ],
        )
        dotnet_env_process.wait("dotnet_publish_scraper")
        if dotnet_env_process.returncode != 0:
            logger.error(
                f"Error publishing Zilean.DmmScraper: {dotnet_env_process.stderr}"
            )
            return False

        logger.info("Dotnet environment setup and publish complete")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Error during .NET environment setup: {e}")
        return False


def setup_environment(process_handler, process_name, zilean_dir, data_dir):
    if not setup_python_environment(
        process_handler=process_handler, config_dir=zilean_dir
    ):
        logger.error(f"Failed to set up Python environment for {process_name}")
        return False, f"Failed to set up Python environment for {process_name}"

    if not setup_dotnet_environment(
        process_handler=process_handler, config_dir=zilean_dir
    ):
        logger.error(f"Failed to set up .NET environment for {process_name}")
        return False, f"Failed to set up .NET environment for {process_name}"

    chown_recursive(data_dir, user_id, group_id)
    return True, None


def clear_directory(directory_path, exclude_dirs=None, retries=3, delay=2):
    if exclude_dirs is None:
        exclude_dirs = []
    exclude_dirs = [os.path.abspath(exclude_dir) for exclude_dir in exclude_dirs]
    logger.debug(f"Excluding directories: {exclude_dirs}")
    exclude_parents = {
        os.path.join(
            directory_path,
            os.path.relpath(exclude_dir, directory_path).split(os.sep)[0],
        )
        for exclude_dir in exclude_dirs
    }

    def clear_contents(path, exclusions):
        for item in os.listdir(path):
            item_path = os.path.abspath(os.path.join(path, item))
            if item_path in exclusions:
                logger.debug(f"Skipping excluded directory: {item_path}")
                continue
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

    if os.path.exists(directory_path):
        for attempt in range(retries):
            try:
                for item in os.listdir(directory_path):
                    item_path = os.path.abspath(os.path.join(directory_path, item))
                    if item_path in exclude_parents:
                        logger.debug(
                            f"Skipping directory in {directory_path}: {item_path}"
                        )
                        continue
                    if any(
                        os.path.commonpath([item_path, exclude_dir]) == exclude_dir
                        for exclude_dir in exclude_dirs
                    ):
                        continue
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                for parent_dir in exclude_parents:
                    if os.path.exists(parent_dir):
                        logger.debug(
                            f"Clearing contents of {parent_dir}, excluding {exclude_dirs}"
                        )
                        clear_contents(parent_dir, exclude_dirs)
                logger.debug(
                    f"Cleared contents of {directory_path}, excluding {exclude_dirs}"
                )
                break
            except OSError as e:
                if e.errno == 16:
                    logger.warning(f"Resource busy: {item_path}, retrying...")
                    time.sleep(delay)
                else:
                    raise
        else:
            logger.error(f"Failed to clear {directory_path} after {retries} retries.")
    else:
        logger.warning(f"Directory {directory_path} does not exist")


def zilean_setup(
    process_handler,
    process_name,
    branch="main",
    release_version=None,
    running_process=False,
):
    zilean_versions = Versions()
    logger.info(f"Configuring {process_name}")
    zilean_dir = "/zilean"
    config_dir = os.path.join(zilean_dir, "app")
    data_dir = os.path.join(config_dir, "data")
    venv_dir = os.path.join(zilean_dir, "venv")
    exclude_dirs = [os.path.abspath(data_dir)]
    try:
        if process_name == "Zilean":
            repo_owner = "iPromKnight"
            repo_name = "zilean"
            if ZILEANVERSION is not None:
                clear_directory(zilean_dir, exclude_dirs)
                logger.info(
                    f"Using {branch} branch version {ZILEANVERSION} for {process_name}"
                )
                release_version = ZILEANVERSION
                branch = "main"
                from .download import download_and_unzip_release

                success, error = download_and_unzip_release(
                    repo_owner, repo_name, release_version, zilean_dir
                )
                if not success:
                    logger.error(
                        f"Failed to download the {release_version} release in {branch} branch for {process_name}: {error}"
                    )
                    return False, error
                logger.info(
                    f"Successfully downloaded the {release_version} release in {branch} branch for {process_name}"
                )
                zilean_version_write, zilean_version_write_message = (
                    zilean_versions.version_write(
                        process_name, version_path=None, version=release_version
                    )
                )
                if not zilean_version_write:
                    logger.error(
                        f"Failed to write version {release_version} for {process_name}: {zilean_version_write_message}"
                    )
                if not setup_environment(
                    process_handler, process_name, zilean_dir, data_dir
                ):
                    logger.error(f"Failed to set up environment for {process_name}")
                    return False, f"Failed to set up environment for {process_name}"

            elif ZILEANBRANCH:
                clear_directory(zilean_dir, exclude_dirs)
                logger.info(f"Using {ZILEANBRANCH} branch for {process_name}")
                branch = ZILEANBRANCH
                from .download import get_branch

                success, error = get_branch(
                    repo_owner, repo_name, branch, zilean_dir, exclude_dirs
                )
                if not success:
                    logger.error(
                        f"Failed to download the {branch} branch for {process_name}: {error}"
                    )
                    return False, error
                logger.info(
                    f"Successfully downloaded {branch} branch for {process_name}"
                )
                if not setup_environment(
                    process_handler, process_name, zilean_dir, data_dir
                ):
                    logger.error(f"Failed to set up environment for {process_name}")
                    return False, f"Failed to set up environment for {process_name}"

            else:
                if running_process:
                    clear_directory(zilean_dir, exclude_dirs)
                    from .download import download_and_unzip_release

                    success, error = download_and_unzip_release(
                        repo_owner, repo_name, release_version, zilean_dir
                    )
                    if not success:
                        logger.error(
                            f"Failed to download the latest release for {process_name}: {error}"
                        )
                        return False, error
                    logger.info(
                        f"Successfully downloaded the latest release for {process_name}"
                    )
                    if not setup_environment(
                        process_handler, process_name, zilean_dir, data_dir
                    ):
                        logger.error(f"Failed to set up environment for {process_name}")
                        return False, f"Failed to set up environment for {process_name}"
                else:
                    if ZILEANUPDATE and ZILEANUPDATE.lower() == "true":
                        pass
                    else:
                        zilean_update_needed, zilean_update_info = (
                            zilean_versions.compare_versions(
                                process_name, repo_owner, repo_name
                            )
                        )
                        if not zilean_update_needed:
                            logger.info(
                                f"{zilean_update_info.get('message')} for {process_name}"
                            )
                        else:
                            current_version = zilean_update_info.get("current_version")
                            latest_version = zilean_update_info.get("latest_version")
                            logger.info(
                                f"{zilean_update_info.get('message')} for {process_name}. "
                                f"Current version: {current_version}, latest version: {latest_version}..."
                            )
        return True, None
    except Exception as e:
        logger.error(f"Exception during setup of {process_name}: {e}")
        return False, str(e)


if __name__ == "__main__":
    zilean_setup()
