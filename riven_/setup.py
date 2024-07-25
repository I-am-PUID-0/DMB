from base import *
from utils.logger import *


logger = get_logger()

def riven_setup(process_name, branch='main', release_version=None):
    logger.info(f"Configuring {process_name}")
    riven_dir = "./riven"
    backend_dir= os.path.join(riven_dir, "backend")
    frontend_dir = os.path.join(riven_dir, "frontend") 
    exclude_dirs = None
    if process_name == 'Riven_backend': 
        repo_owner='rivenmedia'
        repo_name='riven'
        
        if RBVERSION is not None:
            logger.info(f"Using {branch} branch version {RBVERSION} for {process_name}")
            release_version = RBVERSION
            from .download import download_and_unzip_release
            success, error = download_and_unzip_release(repo_owner, repo_name, release_version, backend_dir)
            if not success:
                logger.error(f"Failed to download the {release_version} release in {branch} branch for {process_name}: {error}")
                raise Exception(f"Failed to download the {release_version} release in {branch} branch for {process_name}: {error}")
            if success:
                logger.info(f"Sucessfully downloaded the {release_version} release in {branch} branch for {process_name}")
                
        elif RBBRANCH:
            logger.info(f"Using {RBBRANCH} branch for {process_name}")
            branch = RBBRANCH
            from .download import get_branch
            success, error = get_branch(repo_owner, repo_name, branch, backend_dir, exclude_dirs)
            if not success:
                logger.error(f"Failed to download the {branch} branch for {process_name}: {error}")
                raise Exception(f"Failed to download the {branch} branch for {process_name}: {error}")
            if success:             
                logger.info(f"Sucessfully downloaded {branch} branch for {process_name}")            
            
        else: 
            from .download import get_latest_release
            release_version, error = get_latest_release(repo_owner, repo_name)
            if not release_version:
                logger.error(f"Failed to get the latest release for {process_name}: {error}")
                raise Exception(f"Failed to get the latest release for {process_name}: {error}")
            from .download import download_and_unzip_release
            success, error = download_and_unzip_release(repo_owner, repo_name, release_version, backend_dir)            
            if not success:
                logger.error(f"Failed to download the latest release for {process_name}: {error}")
                raise Exception(f"Failed to download the latest release for {process_name}: {error}") 
            if success:
                logger.info(f"Sucessfully downloaded the latest release for {process_name}")
            
    if process_name == 'Riven_frontend': 
        repo_owner='rivenmedia'
        repo_name='riven-frontend'
        if RFVERSION is not None:
            logger.info(f"Using {branch} branch version {RFVERSION} for {process_name}")
            release_version = RFVERSION
            from .download import download_and_unzip_release
            success, error = download_and_unzip_release(repo_owner, repo_name, release_version, frontend_dir)
            if not success:
                logger.error(f"Failed to download the {release_version} release in {branch} branch for {process_name}: {error}")
                raise Exception(f"Failed to download the {release_version} release in {branch} branch for {process_name}: {error}")
            if success:
                logger.info(f"Sucessfully downloaded the {release_version} release in {branch} branch for {process_name}")
                
        elif RFBRANCH:
            logger.info(f"Using {RFBRANCH} branch for {process_name}")
            branch = RFBRANCH
            from .download import get_branch
            success, error = get_branch(repo_owner, repo_name, branch, frontend_dir, exclude_dirs)
            if not success:
                logger.error(f"Failed to download the {branch} branch for {process_name}: {error}")
                raise Exception(f"Failed to download the {branch} branch for {process_name}: {error}")
            if success:             
                logger.info(f"Sucessfully downloaded {branch} branch for {process_name}")            
            
        else: 
            from .download import get_latest_release
            release_version, error = get_latest_release(repo_owner, repo_name)
            if not release_version:
                logger.error(f"Failed to get the latest release for {process_name}: {error}")
                raise Exception(f"Failed to get the latest release for {process_name}: {error}")
            from .download import download_and_unzip_release
            success, error = download_and_unzip_release(repo_owner, repo_name, release_version, frontend_dir)            
            if not success:
                logger.error(f"Failed to download the latest release for {process_name}: {error}")
                raise Exception(f"Failed to download the latest release for {process_name}: {error}") 
            if success:
                logger.info(f"Sucessfully downloaded the latest release for {process_name}")
    
if __name__ == "__main__":
    riven_setup()
