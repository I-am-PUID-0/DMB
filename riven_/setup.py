from os import chmod
from base import *
from utils.logger import *


logger = get_logger()

def setup_poetry_environment(process_handler=None, config_dir='/riven/backend'):
    try:
        logger.info(f"Setting up Poetry environment in {config_dir}")

        venv_path = f"{config_dir}/venv"
        python_executable = os.path.abspath(f"{venv_path}/bin/python")
        poetry_executable = os.path.abspath(f"{venv_path}/bin/poetry")

        python_env_process = process_handler
        python_env_process.start_process("python_env_setup", config_dir, ["python", "-m", "venv", "venv"])
        python_env_process.wait("python_env_setup")
        if python_env_process.returncode != 0:
            logger.error(f"Error setting up Python environment: {python_env_process.stderr}")
            return False, None

        env = os.environ.copy()
        env["PATH"] = f"{venv_path}/bin:" + env["PATH"]
        env["POETRY_VIRTUALENVS_CREATE"] = "false"
        env["VIRTUAL_ENV"] = venv_path  

        python_env_process.start_process("install_poetry", config_dir, [python_executable, "-m", "pip", "install", "poetry"], None, False, env=env)
        python_env_process.wait("install_poetry")
        if python_env_process.returncode != 0:
            logger.error(f"Error installing Poetry: {python_env_process.stderr}")
            return False, None

        poetry_install_process = process_handler
        poetry_install_process.start_process("poetry_install", config_dir, [poetry_executable, "install", "--no-root", "--without", "dev"], None, False, env=env)
        poetry_install_process.wait("poetry_install")
        if poetry_install_process.returncode != 0:
            logger.error(f"Error setting up Poetry environment: {poetry_install_process.stderr}")
            return False, None

        logger.info(f"Poetry environment setup complete at {venv_path}")
        return venv_path, poetry_executable  
    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting up Poetry environment: {e}")
        return False, None

def setup_npm_build(process_handler=None, config_dir='/riven/frontend'):
    try:
        logger.info("Setting up riven_frontend")
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
        logger.debug("vite.config.ts modified to disable minification")

        about_page_path = os.path.join(config_dir, 'src', 'routes', 'settings', 'about', '+page.server.ts')
        with open(about_page_path, 'r') as file:
            about_page_lines = file.readlines()
        for i, line in enumerate(about_page_lines):
            if "versionFilePath: string = '/riven/version.txt';" in line:
                about_page_lines[i] = line.replace("/riven/version.txt", "/riven/frontend/version.txt")
                logger.debug(f"Modified versionFilePath in +page.server.ts to point to /riven/frontend/version.txt")
                break
        with open(about_page_path, 'w') as file:
            file.writelines(about_page_lines)

        npm_install_process = process_handler
        npm_install_process.start_process("npm_install", config_dir, ["pnpm", "install"])
        npm_install_process.wait("npm_install")
        if npm_install_process.returncode != 0:
            logger.error(f"Error during npm install: {npm_install_process.stderr}")
            return False

        node_build_process = process_handler
        if 'RFDIALECT' not in os.environ:
            os.environ['DIALECT'] = 'postgres'      
        node_build_process.start_process("node_build", config_dir, ["pnpm", "run", "build"])
        node_build_process.wait("node_build")
        if node_build_process.returncode != 0:
            logger.error(f"Error during node build: {node_build_process.stderr}")
            return False
        logger.info("npm install and build complete")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting up npm environment: {e}")
        return False

def riven_setup(process_handler, process_name, branch='main', release_version=None, running_process=False):
    logger.info(f"Configuring {process_name}")
    riven_dir = "/riven"
    backend_dir = os.path.join(riven_dir, "backend")
    frontend_dir = os.path.join(riven_dir, "frontend")
    exclude_dirs = None
    try:
        if process_name == 'riven_backend':
            repo_owner = 'rivenmedia'
            repo_name = 'riven'

            if RBVERSION is not None:
                logger.info(f"Using {branch} branch version {RBVERSION} for {process_name}")
                release_version = RBVERSION
                branch = 'main'
                from .download import download_and_unzip_release
                success, error = download_and_unzip_release(repo_owner, repo_name, release_version, backend_dir)
                if not success:
                    logger.error(f"Failed to download the {release_version} release in {branch} branch for {process_name}: {error}")
                    return False, error
                logger.info(f"Successfully downloaded the {release_version} release in {branch} branch for {process_name}")
                from utils.user_management import chown_recursive
                chown_recursive(riven_dir, user_id, group_id)

            elif RBBRANCH:
                logger.info(f"Using {RBBRANCH} branch for {process_name}")
                branch = RBBRANCH
                from .download import get_branch
                success, error = get_branch(repo_owner, repo_name, branch, backend_dir, exclude_dirs)
                if not success:
                    logger.error(f"Failed to download the {branch} branch for {process_name}: {error}")
                    return False, error
                logger.info(f"Successfully downloaded {branch} branch for {process_name}")
                from utils.user_management import chown_recursive
                chown_recursive(riven_dir, user_id, group_id)

            else:
                from .download import get_latest_release
                release_version, error = get_latest_release(repo_owner, repo_name)
                if not release_version:
                    logger.error(f"Failed to get the latest release for {process_name}: {error}")
                    return False, error
                from .download import download_and_unzip_release
                success, error = download_and_unzip_release(repo_owner, repo_name, release_version, backend_dir)
                if not success:
                    logger.error(f"Failed to download the latest release for {process_name}: {error}")
                    return False, error
                logger.info(f"Successfully downloaded the latest release for {process_name}")
                from utils.user_management import chown_recursive
                chown_recursive(riven_dir, user_id, group_id)

        if process_name == 'riven_frontend':
            if RFOWNER: 
                repo_owner = RFOWNER
            else: 
                repo_owner = 'rivenmedia'
            repo_name = 'riven-frontend'
            if RFVERSION is not None:
                branch = 'main'                
                logger.info(f"Using {branch} branch version {RFVERSION} for {process_name}")
                release_version = RFVERSION
                from .download import download_and_unzip_release
                success, error = download_and_unzip_release(repo_owner, repo_name, release_version, frontend_dir)
                if not success:
                    logger.error(f"Failed to download the {release_version} release in {branch} branch for {process_name}: {error}")
                    return False, error
                logger.info(f"Successfully downloaded the {release_version} release in {branch} branch for {process_name}")
                if not setup_npm_build(process_handler=process_handler):
                    logger.error(f"Failed to set up NPM build for {process_name}")
                    return False, f"Failed to set up NPM build for {process_name}" 
                from utils.user_management import chown_recursive
                chown_recursive(riven_dir, user_id, group_id)

            elif RFBRANCH:
                logger.info(f"Using {RFBRANCH} branch for {process_name}")
                branch = RFBRANCH
                from .download import get_branch
                success, error = get_branch(repo_owner, repo_name, branch, frontend_dir, exclude_dirs)
                if not success:
                    logger.error(f"Failed to download the {branch} branch for {process_name}: {error}")
                    return False, error
                logger.info(f"Successfully downloaded {branch} branch for {process_name}")
                if not setup_npm_build(process_handler=process_handler):
                    logger.error(f"Failed to set up NPM build for {process_name}")
                    return False, f"Failed to set up NPM build for {process_name}"   
                from utils.user_management import chown_recursive
                chown_recursive(riven_dir, user_id, group_id)
                
            else:
                if running_process:
                    from .download import download_and_unzip_release
                    success, error = download_and_unzip_release(repo_owner, repo_name, release_version, frontend_dir)
                    if not success:
                        logger.error(f"Failed to download the latest release for {process_name}: {error}")
                        return False, error
                    logger.info(f"Successfully downloaded the latest release for {process_name}")                    
                    if not setup_npm_build(process_handler=process_handler):
                        logger.error(f"Failed to set up NPM build for {process_name}")
                        return False, f"Failed to set up NPM build for {process_name}"   
                    from utils.user_management import chown_recursive
                    chown_recursive(riven_dir, user_id, group_id)
                else:    
                    from .download import get_latest_release
                    latest_release_version, error = get_latest_release(repo_owner, repo_name)
                    if not latest_release_version:
                        logger.error(f"Failed to get the latest release for {process_name}: {error}")
                        return False, error

                    from .download import version_check
                    current_version, error = version_check(version_path=None, process_name=process_name)
                    if not current_version:
                        logger.error(f"Failed to get the current version for {process_name}: {error}")
                        return False, error
                    logger.info(f"{process_name} current version: {current_version}")
                    if current_version == latest_release_version:
                        return True, None
             
#                else:
#                    from .download import download_and_unzip_release
#                    success, error = download_and_unzip_release(repo_owner, repo_name, latest_release_version, frontend_dir)
#                    if not success:
#                        logger.error(f"Failed to download the latest release for {process_name}: {error}")
#                        return False, error
#                    logger.info(f"Successfully downloaded the latest release for {process_name}")

        return True, None
    except Exception as e:
        logger.error(f"Exception during setup of {process_name}: {e}")
        return False, str(e)

if __name__ == "__main__":
    riven_setup()
