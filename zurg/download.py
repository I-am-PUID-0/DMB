from base import *
from utils.global_logger import logger
from utils.download import Downloader


downloader = Downloader()


class CustomVersion:
    def __init__(self, main_version, hotfix=0, subversion=""):
        self.main_version = main_version
        self.hotfix = hotfix
        self.subversion = subversion

    def __lt__(self, other):
        if self.main_version != other.main_version:
            return self.main_version < other.main_version
        if self.hotfix != other.hotfix:
            return self.hotfix < other.hotfix
        if not self.subversion and other.subversion:
            return True
        if self.subversion and not other.subversion:
            return False
        return self.subversion < other.subversion

    def __eq__(self, other):
        return (self.main_version, self.hotfix, self.subversion) == (
            other.main_version,
            other.hotfix,
            self.subversion,
        )

    def __str__(self):
        version_str = f"v{self.main_version}"
        if self.hotfix > 0:
            version_str += f"-hotfix.{self.hotfix}"
        if self.subversion:
            version_str += f"-{self.subversion}"
        return version_str


def parse_custom_version(version_str):
    try:
        main_version_part, *hotfix_part = version_str.lstrip("v").split("-hotfix.")
        main_version = parse_version(main_version_part)
        hotfix_number = 0
        subversion = ""
        if hotfix_part:
            hotfix_and_subversion = hotfix_part[0].split("-", 1)
            hotfix_number = (
                int(hotfix_and_subversion[0])
                if hotfix_and_subversion[0].isdigit()
                else 0
            )
            if len(hotfix_and_subversion) > 1:
                subversion = hotfix_and_subversion[1]
        return CustomVersion(main_version, hotfix_number, subversion)
    except Exception as e:
        logger.error(f"Error parsing version string '{version_str}': {e}")
        return None


def get_latest_release(repo_owner, repo_name, nightly=False):
    return downloader.get_latest_release(repo_owner, repo_name, nightly=nightly)


def get_architecture():
    return downloader.get_architecture()


def download_and_unzip_release(repo_owner, repo_name, release_version, architecture):
    try:
        headers = {}
        if GHTOKEN:
            headers["Authorization"] = f"token {GHTOKEN}"
        release_info, error = downloader.fetch_github_release_info(
            repo_owner, repo_name, release_version, headers
        )
        if error:
            logger.error(error)
            return False
        download_url, asset_id = downloader.find_asset_download_url(
            release_info, architecture
        )
        if not download_url:
            return False
        download_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/assets/{asset_id}"
        headers["Accept"] = "application/octet-stream"
        logger.debug(
            f"Requesting {repo_name} release {release_version} from: {download_url}"
        )
        zip_folder_name = f"zurg-{release_version}-{architecture}"
        success, error = downloader.download_and_extract(
            download_url, "zurg", zip_folder_name=zip_folder_name, headers=headers
        )
        if success:
            downloader.set_permissions(os.path.join("zurg", "zurg"), 0o755)
            os.environ["ZURG_CURRENT_VERSION"] = release_version
            return True
        else:
            logger.error(f"Error in download and extraction: {error}")
            return False
    except Exception as e:
        logger.error(f"Error in download and extraction: {e}")
        return False


def version_check():
    try:
        architecture = get_architecture()
        os.environ["CURRENT_ARCHITECTURE"] = architecture
        if GHTOKEN:
            repo_owner = "debridmediamanager"
            repo_name = "zurg"
        else:
            repo_owner = "debridmediamanager"
            repo_name = "zurg-testing"

        nightly = False

        if ZURGVERSION:
            if "nightly" in ZURGVERSION.lower():
                release_version = ZURGVERSION
                logger.info("Using nightly release version from environment variable")
                nightly = True
            else:
                release_version = (
                    ZURGVERSION if ZURGVERSION.startswith("v") else "v" + ZURGVERSION
                )
                logger.info(
                    "Using release version from environment variable: %s",
                    release_version,
                )
        else:
            release_version, error = get_latest_release(repo_owner, repo_name)
            if error:
                logger.error(error)
                raise Exception("Failed to get the latest release version.")

        if nightly:
            release_version, error = get_latest_release(
                repo_owner, repo_name, nightly=True
            )
            if error:
                logger.error(error)
                raise Exception("Failed to get the latest nightly release version.")

        if not download_and_unzip_release(
            repo_owner, repo_name, release_version, architecture
        ):
            raise Exception("Failed to download and extract the release.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        exit(1)
