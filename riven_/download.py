from base import *
from utils.logger import *
from utils.download import download_and_extract


logger = get_logger()

def get_latest_release():
    branch = RBRANCH or 'main'
    zip_folder_name = f'riven-{branch.replace("/", "-")}'
    target = './riven'
    branch_url = f"https://github.com/rivenmedia/riven/archive/refs/heads/{branch}.zip"
    logger.debug(f"Requesting Riven release from {branch_url}")
    exclude_dirs = ['data/']
    success, error = download_and_extract(branch_url, target, zip_folder_name, exclude_dirs=exclude_dirs)
    if success:
        return True, None
    else:
        logger.error(f"Error downloading latest riven release: {error}")
        return False, error