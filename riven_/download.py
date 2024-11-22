from base import *
from utils.global_logger import logger
from utils.download import Downloader

downloader = Downloader()


def get_headers():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GHTOKEN:
        headers["Authorization"] = f"token {GHTOKEN}"
    return headers


def get_branch(repo_owner, repo_name, branch, target_dir, exclude_dirs):
    try:
        headers = get_headers()
        branch_url, zip_folder_name = downloader.get_branch(
            repo_owner, repo_name, branch, headers
        )
        if not branch_url:
            return False, f"Failed to get the {branch} branch for {repo_name}"
        elif branch_url and zip_folder_name:
            success, error = downloader.download_and_extract(
                branch_url,
                target_dir,
                zip_folder_name=zip_folder_name,
                headers=headers,
                exclude_dirs=exclude_dirs,
            )
            if not success:
                logger.error(
                    f"Failed to download the {branch} branch for {repo_name}: {error}"
                )
                return False, error
            else:
                return True, None
    except Exception as e:
        logger.error(f"Error in download and extraction: {e}")
        return False, str(e)


def get_latest_release(repo_owner, repo_name):
    return downloader.get_latest_release(repo_owner, repo_name)


def download_and_unzip_release(
    repo_owner, repo_name, release_version, target_dir, exclude_dirs=None
):
    try:
        headers = get_headers()
        release_info, error = downloader.fetch_github_release_info(
            repo_owner, repo_name, release_version, headers
        )
        if error:
            logger.error(error)
            return False, error
        download_url, asset_id = downloader.find_asset_download_url(release_info)
        if not download_url:
            return False, error
        logger.debug(
            f"Requesting {repo_name} release {release_version} from: {download_url}"
        )
        zip_folder_name = f"{repo_owner}-{repo_name}*"
        success, error = downloader.download_and_extract(
            download_url,
            target_dir,
            zip_folder_name=zip_folder_name,
            headers=headers,
            exclude_dirs=exclude_dirs,
        )
        if success:
            return True, None
        else:
            return False, error
    except Exception as e:
        logger.error(f"Error in download and extraction: {e}")
        return False, str(e)


def version_check(version_path=None, process_name=None):
    try:
        if process_name == "riven_frontend":
            version_path = "./riven/frontend/version.txt"
        else:
            version_path = "./riven/backend/pyproject.toml"

        with open(version_path, "r") as f:
            if process_name == "riven_frontend":
                return f"v{f.read().strip()}", None
            elif process_name == "riven_backend":
                for line in f:
                    if line.startswith("version = "):
                        return line.split("=")[1].strip().replace('"', ""), None
        return None, "Version not found"
    except Exception as e:
        logger.error(
            f"Error reading current version for {process_name} from {version_path}: {e}"
        )
        return None, str(e)


def compare_versions(process_name, repo_owner, repo_name):
    try:
        from .download import get_latest_release

        latest_release_version, error = get_latest_release(repo_owner, repo_name)
        if not latest_release_version:
            logger.error(
                f"Failed to get the latest release for {process_name}: {error}"
            )
            return False, error

        from .download import version_check

        current_version, error = version_check(
            version_path=None, process_name=process_name
        )
        if not current_version:
            logger.error(
                f"Failed to get the current version for {process_name}: {error}"
            )
            return False, error
        if current_version == latest_release_version:
            return True, None
    except Exception as e:
        logger.error(f"Exception during version comparison {process_name}: {e}")
        return False, str(e)
