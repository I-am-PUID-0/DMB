from os import chmod
from base import *
from utils.logger import *


logger = get_logger()

def setup_python_environment(process_handler=None, config_dir='/zilean'):
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
            logger.error(f"Virtual environment not found or {activate_script} is missing.")
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

def setup_dotnet_environment(process_handler=None, config_dir='./zilean'):
    try:
        logger.info(f"Setting up .NET environment in {config_dir}")

        dotnet_env_process = process_handler

        dotnet_env_process.start_process("dotnet_env_restore", config_dir, ["dotnet", "restore"])
        dotnet_env_process.wait("dotnet_env_restore")
        if dotnet_env_process.returncode != 0:
            logger.error(f"Error running dotnet restore: {dotnet_env_process.stderr}")
            return False

        dotnet_env_process.start_process("dotnet_publish_api", config_dir, [
            "dotnet", "publish", "/zilean/src/Zilean.ApiService", 
            "-c", "Release", "--no-restore", "-o", "/zilean/app/"])
        dotnet_env_process.wait("dotnet_publish_api")
        if dotnet_env_process.returncode != 0:
            logger.error(f"Error publishing Zilean.ApiService: {dotnet_env_process.stderr}")
            return False

        dotnet_env_process.start_process("dotnet_publish_scraper", config_dir, [
            "dotnet", "publish", "/zilean/src/Zilean.DmmScraper", 
            "-c", "Release", "--no-restore", "-o", "/zilean/app/"])
        dotnet_env_process.wait("dotnet_publish_scraper")
        if dotnet_env_process.returncode != 0:
            logger.error(f"Error publishing Zilean.DmmScraper: {dotnet_env_process.stderr}")
            return False

        logger.info("Dotnet environment setup and publish complete")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Error during .NET environment setup: {e}")
        return False

def zilean_setup(process_handler, process_name, branch='main', release_version=None, running_process=False):
    logger.info(f"Configuring {process_name}")
    zilean_dir = "./zilean"
    app_dir = os.path.join(zilean_dir, "app")
    data_dir = os.path.join(app_dir, "data")
    venv_dir = os.path.join(zilean_dir, "venv")
    exclude_dirs = None
    try:
        if process_name == 'Zilean':
            repo_owner = 'iPromKnight'
            repo_name = 'zilean'

            if ZILEANVERSION is not None:
                logger.info(f"Using {branch} branch version {ZILEANVERSION} for {process_name}")
                release_version = ZILEANVERSION
                branch = 'main'
                from .download import download_and_unzip_release
                success, error = download_and_unzip_release(repo_owner, repo_name, release_version, zilean_dir)
                if not success:
                    logger.error(f"Failed to download the {release_version} release in {branch} branch for {process_name}: {error}")
                    return False, error
                logger.info(f"Successfully downloaded the {release_version} release in {branch} branch for {process_name}")
                os.environ['ZILEAN_CURRENT_VERSION'] = release_version
                if not setup_python_environment(process_handler=process_handler, config_dir=zilean_dir):
                    logger.error(f"Failed to set up Python environment for {process_name}")
                    return False, f"Failed to set up Python environment for {process_name}"
                if not setup_dotnet_environment(process_handler=process_handler, config_dir=zilean_dir):
                    logger.error(f"Failed to set up .NET environment for {process_name}")
                    return False, f"Failed to set up .NET environment for {process_name}"
                from utils.user_management import chown_recursive
                chown_recursive(data_dir, user_id, group_id)

            elif ZILEANBRANCH:
                logger.info(f"Using {ZILEANBRANCH} branch for {process_name}")
                branch = ZILEANBRANCH
                from .download import get_branch
                success, error = get_branch(repo_owner, repo_name, branch, zilean_dir, exclude_dirs)
                if not success:
                    logger.error(f"Failed to download the {branch} branch for {process_name}: {error}")
                    return False, error
                logger.info(f"Successfully downloaded {branch} branch for {process_name}")
                if not setup_python_environment(process_handler=process_handler, config_dir=zilean_dir):
                    logger.error(f"Failed to set up Python environment for {process_name}")
                    return False, f"Failed to set up Python environment for {process_name}"
                if not setup_dotnet_environment(process_handler=process_handler, config_dir=zilean_dir):
                    logger.error(f"Failed to set up .NET environment for {process_name}")
                    return False, f"Failed to set up .NET environment for {process_name}"
                from utils.user_management import chown_recursive
                chown_recursive(data_dir, user_id, group_id)

            else:
                if running_process:
                    from .download import download_and_unzip_release
                    success, error = download_and_unzip_release(repo_owner, repo_name, release_version, zilean_dir)
                    if not success:
                        logger.error(f"Failed to download the latest release for {process_name}: {error}")
                        return False, error
                    logger.info(f"Successfully downloaded the latest release for {process_name}") 
                    os.environ['ZILEAN_CURRENT_VERSION'] = release_version
                    if not setup_dotnet_environment(process_handler=process_handler):
                        logger.error(f"Failed to set up .NET environment for {process_name}")
                        return False, f"Failed to set up .NET environment for {process_name}"   
                    from utils.user_management import chown_recursive
                    chown_recursive(data_dir, user_id, group_id)
                else:    
                    from .download import get_latest_release
                    release_version, error = get_latest_release(repo_owner, repo_name)
                    if not release_version:
                        logger.error(f"Failed to get the latest release for {process_name}: {error}")
                        return False, error
                    os.environ['ZILEAN_CURRENT_VERSION'] = release_version
                    from .download import download_and_unzip_release
                    success, error = download_and_unzip_release(repo_owner, repo_name, release_version, zilean_dir)
                    if not success:
                        logger.error(f"Failed to download the latest release for {process_name}: {error}")
                        return False, error
                    logger.info(f"Successfully downloaded the latest release for {process_name}")
                    if not setup_python_environment(process_handler=process_handler, config_dir=zilean_dir):
                        logger.error(f"Failed to set up Python environment for {process_name}")
                        return False, f"Failed to set up Python environment for {process_name}"
                    if not setup_dotnet_environment(process_handler=process_handler, config_dir=zilean_dir):
                        logger.error(f"Failed to set up .NET environment for {process_name}")
                        return False, f"Failed to set up .NET environment for {process_name}"
                    from utils.user_management import chown_recursive
                    chown_recursive(data_dir, user_id, group_id)

        return True, None
    except Exception as e:
        logger.error(f"Exception during setup of {process_name}: {e}")
        return False, str(e)

if __name__ == "__main__":
    zilean_setup()
