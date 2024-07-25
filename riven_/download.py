from email import header
from base import *
from utils.logger import *
from utils.download import Downloader

logger = get_logger()
downloader = Downloader()

def get_branch(repo_owner, repo_name, branch, target_dir, exclude_dirs):
    try:    
        headers = {}
        headers['Accept'] = 'application/octet-stream'
        branch_url, zip_folder_name = downloader.get_branch(repo_owner, repo_name, branch, headers)
        if not branch_url:
            return False, f"Failed to get the {branch} branch for {repo_name}"
        elif branch_url and zip_folder_name:
            success, error = downloader.download_and_extract(branch_url, target_dir, zip_folder_name=zip_folder_name, headers=headers, exclude_dirs=exclude_dirs)
            if not success:
                logger.error(f"Failed to download the {branch} branch for {repo_name}: {error}")
                return False, error
            else:
                return True, None
    except Exception as e:
        logger.error(f"Error in download and extraction: {e}")
        return False, str(e)    

def get_latest_release(repo_owner, repo_name):
    return downloader.get_latest_release(repo_owner, repo_name)

def download_and_unzip_release(repo_owner, repo_name, release_version, target_dir, exclude_dirs=None):
    try:
        headers = {}         
        release_info, error = downloader.fetch_github_release_info(repo_owner, repo_name, release_version, headers)        
        if error:
            logger.error(error)
            return False        
        download_url, asset_id = downloader.find_asset_download_url(release_info)        
        if not download_url:
            return False        
        #headers['Accept'] = 'application/octet-stream'
        headers = headers or {"Accept": "application/vnd.github.v3+json"}
        logger.debug(f"Requesting {repo_name} release {release_version} from: {download_url}")
        zip_folder_name = f'{repo_owner}-{repo_name}*'
        success, error = downloader.download_and_extract(download_url, target_dir, zip_folder_name=zip_folder_name, headers=headers, exclude_dirs=exclude_dirs)
        if success:
            return True, None
        else:
            logger.error(f"Error in download and extraction: {error}")
            return False
    except Exception as e:
        logger.error(f"Error in download and extraction: {e}")
        return False, str(e)
    
def version_check(repo_owner, repo_name, release_version):
    try:
              
        if ZURGVERSION:
            release_version = ZURGVERSION if ZURGVERSION.startswith('v') else 'v' + ZURGVERSION
            logger.info("Using release version from environment variable: %s", release_version)
        else:      
            release_version, error = get_latest_release(repo_owner, repo_name)
            if error:
                logger.error(error)
                raise Exception("Failed to get the latest release version.")
        if not download_and_unzip_release(repo_owner, repo_name, release_version):
            raise Exception("Failed to download and extract the release.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        exit(1)