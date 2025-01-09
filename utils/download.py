from base import *
from utils.global_logger import logger
from utils.config_loader import CONFIG_MANAGER


class Downloader:
    def __init__(self):
        self.logger = logger

    def get_headers(self):
        headers = {}
        if CONFIG_MANAGER.get("dmb").get("github_token"):
            headers["Authorization"] = (
                f"token {CONFIG_MANAGER.get('dmb').get('github_token')}"
            )
        else:
            headers = {"Accept": "application/vnd.github.v3+json"}
        return headers

    def handle_rate_limits(self, response):
        if response.status_code in [403, 429]:
            if "Retry-After" in response.headers:
                retry_after = int(response.headers["Retry-After"])
                self.logger.warning(
                    f"Rate limit exceeded. Retrying after {retry_after} seconds."
                )
                time.sleep(retry_after)
            elif "X-RateLimit-Reset" in response.headers:
                reset_time = int(response.headers["X-RateLimit-Reset"])
                current_time = time.time()
                sleep_time = max(0, reset_time - current_time)
                self.logger.warning(
                    f"Rate limit exceeded. Retrying after {sleep_time} seconds."
                )
                time.sleep(sleep_time)
            else:
                self.logger.warning("Rate limit exceeded. Retrying after 60 seconds.")
                time.sleep(60)
            return True
        return False

    def fetch_with_retries(self, url, headers, max_retries=5):
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    return response
                if not self.handle_rate_limits(response):
                    logger.info(f"Response status code: {response.status_code}")
                self.logger.info(
                    f"Retry attempt {attempt + 1} after rate limit handling."
                )
            except requests.RequestException as e:
                self.logger.error(f"Request error: {e}")
                time.sleep(2**attempt)
        self.logger.error(f"Failed to fetch {url} after {attempt + 1} attempts.")
        return None

    def download_release_version(
        self,
        process_name,
        key,
        repo_owner,
        repo_name,
        release_version,
        target_dir,
        zip_folder_name=None,
        exclude_dirs=None,
    ):
        try:
            headers = self.get_headers()
            if release_version.lower() == "latest":
                release_version, error = self.get_latest_release(
                    repo_owner, repo_name, nightly=False
                )
                if error:
                    logger.error(error)
                    return False, error

            if key == "zurg":
                architecture = self.get_architecture()
                if CONFIG_MANAGER.get("dmb").get("github_token"):
                    # repo_name = "zurg"
                    if release_version == "nightly":
                        release_version, error = self.get_latest_release(
                            repo_owner, repo_name, nightly=True
                        )
                        if error:
                            logger.error(error)
                            return False, error

            else:
                architecture = None

            release_info, error = self.fetch_github_release_info(
                repo_owner, repo_name, release_version, headers=None
            )
            if error:
                logger.error(error)
                return False, error

            if zip_folder_name is None:
                zip_folder_name = f"{repo_owner}-{repo_name}*"

            download_url, asset_id = self.find_asset_download_url(
                release_info, architecture
            )
            if not download_url:
                return False, error

            if asset_id:
                headers = self.get_headers()
                headers["Accept"] = "application/octet-stream"
                download_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/assets/{asset_id}"

            logger.debug(
                f"Requesting {repo_name} release {release_version} from: {download_url}"
            )

            success, error = self.download_and_extract(
                download_url,
                target_dir,
                zip_folder_name,
                headers=headers,
                exclude_dirs=exclude_dirs,
            )
            if not success:
                logger.error(
                    f"Failed to download the {release_version} for {process_name}: {error}"
                )
                return False, error
            logger.info(
                f"Successfully downloaded the {release_version} for {process_name}"
            )
            return True, None
        except Exception as e:
            logger.error(f"Error in download release version: {e}")
            return False, str(e)

    def get_latest_release(self, repo_owner, repo_name, nightly=False):
        self.logger.debug(f"Fetching latest {repo_name} release.")
        headers = self.get_headers()
        if nightly:
            api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases"
        else:
            api_url = (
                f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
            )
        response = self.fetch_with_retries(api_url, headers)
        if response and response.status_code == 200:
            releases = response.json()
            if nightly:
                nightly_releases = [
                    release for release in releases if "nightly" in release["tag_name"]
                ]
                if nightly_releases:
                    latest_nightly = max(nightly_releases, key=lambda x: x["tag_name"])
                    return latest_nightly["tag_name"], None
                return None, "No nightly releases found."

            else:
                latest_release = response.json()
                version_tag = latest_release["tag_name"]
                self.logger.debug(f"{repo_name} latest release: {version_tag}")
                return version_tag, None

        else:
            return None, f"Error: Unable to access the {repo_name} repository API."

    def get_branch(self, repo_owner, repo_name, branch, headers=None):
        headers = self.get_headers()
        zip_folder_name = f'{repo_name}-{branch.replace("/", "-").replace("--", "-")}'
        branch_url = f"https://github.com/{repo_owner}/{repo_name}/archive/refs/heads/{branch}.zip"
        self.logger.debug(f"Requesting {repo_name} release from {branch_url}")
        response = self.fetch_with_retries(branch_url, headers)

        if response and response.status_code == 200:
            return branch_url, zip_folder_name

        else:
            return None, f"Failed to get branch {branch} from {repo_name}."

    def fetch_github_release_info(
        self, repo_owner, repo_name, release_version, headers=None
    ):
        headers = self.get_headers()
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{release_version}"
        self.logger.debug(f"Fetching release information from {api_url}")
        response = self.fetch_with_retries(api_url, headers)

        if response and response.status_code == 200:
            return response.json(), None

        else:
            return None, f"Failed to get {repo_name} release assets."

    def find_asset_download_url(self, release_info, architecture=None):
        assets = release_info.get("assets", [])
        for asset in assets:
            if architecture and architecture in asset["name"]:
                self.logger.debug(
                    f"Assets ID found: {asset['id']} for architecture: {architecture}"
                )
                self.logger.debug(
                    f"Browser Download URL: {asset['browser_download_url']}"
                )
                return asset["browser_download_url"], asset["id"]

        if assets:
            self.logger.warning(
                "No matching asset found for architecture: %s. Falling back to the first available asset.",
                architecture,
            )
            self.logger.debug(f"Download URL: {asset['browser_download_url']}")
            return assets[0]["browser_download_url"], assets[0]["id"]

        zipball_url = release_info.get("zipball_url")
        tarball_url = release_info.get("tarball_url")

        if zipball_url:
            self.logger.debug("No assets found. Using zipball_url.")
            return zipball_url, None

        if tarball_url:
            self.logger.debug("No assets found. Using tarball_url.")
            return tarball_url, None

        self.logger.error("No assets or zipball/tarball URL found for the release.")
        return None, None

    def download_and_extract(
        self, url, target_dir, zip_folder_name=None, headers=None, exclude_dirs=None
    ):
        try:
            self.logger.debug(f"Downloading from {url}")
            headers = headers or self.get_headers()
            response = self.fetch_with_retries(url, headers)
            if response and response.status_code == 200:
                self.logger.debug(
                    f"{zip_folder_name} download successful. Content size: {len(response.content)} bytes"
                )
                try:
                    z = zipfile.ZipFile(io.BytesIO(response.content))
                    self.logger.debug(f"Extracting {zip_folder_name} to {target_dir}")
                    for file_info in z.infolist():
                        # self.logger.debug(f"Processing {file_info.filename}")
                        if file_info.is_dir():
                            continue
                        if zip_folder_name:
                            if fnmatch.fnmatch(
                                file_info.filename, zip_folder_name + "*"
                            ):
                                parts = file_info.filename.split("/", 1)
                                inner_path = parts[1] if len(parts) > 1 else parts[0]
                                fpath = os.path.join(target_dir, inner_path)
                            elif len(z.infolist()) == 1:
                                fpath = os.path.join(target_dir, file_info.filename)
                            else:
                                continue
                        else:
                            fpath = os.path.join(target_dir, file_info.filename)
                        if exclude_dirs and any(
                            exclude_dir in file_info.filename
                            for exclude_dir in exclude_dirs
                        ):
                            continue
                        try:
                            os.makedirs(os.path.dirname(fpath), exist_ok=True)
                            with open(fpath, "wb") as dst, z.open(
                                file_info, "r"
                            ) as src:
                                shutil.copyfileobj(src, dst)
                        except Exception as e:
                            self.logger.error(
                                f"Error while extracting {file_info.filename}: {e}"
                            )
                    self.logger.debug(
                        f"Successfully downloaded {zip_folder_name} and extracted to {target_dir}"
                    )
                    return True, None
                except zipfile.BadZipFile as e:
                    self.logger.error(f"Failed to create ZipFile object: {e}")
                    return False, str(e)
            else:
                return False, "Failed to download."
        except Exception as e:
            self.logger.error(f"Error in download and extraction: {e}")
            return False, str(e)

    def set_permissions(self, file_path, mode):
        try:
            os.chmod(file_path, mode)
            self.logger.debug(f"Set permissions for {file_path} to {oct(mode)}")
        except Exception as e:
            self.logger.error(f"Failed to set permissions for {file_path}: {e}")

    def get_architecture(self):
        try:
            arch_map = {
                ("AMD64", "Windows"): "windows-amd64",
                ("AMD64", "Linux"): "linux-amd64",
                ("AMD64", "Darwin"): "darwin-amd64",
                ("x86_64", "Linux"): "linux-amd64",
                ("x86_64", "Darwin"): "darwin-amd64",
                ("arm64", "Linux"): "linux-arm64",
                ("arm64", "Darwin"): "darwin-arm64",
                ("aarch64", "Linux"): "linux-arm64",
                ("mips64", "Linux"): "linux-mips64",
                ("mips64le", "Linux"): "linux-mips64le",
                ("ppc64le", "Linux"): "linux-ppc64le",
                ("riscv64", "Linux"): "linux-riscv64",
                ("s390x", "Linux"): "linux-s390x",
            }
            system_arch = platform.machine()
            system_os = platform.system()
            self.logger.debug(
                "System Architecture: %s, Operating System: %s", system_arch, system_os
            )
            return arch_map.get((system_arch, system_os), "unknown")
        except Exception as e:
            self.logger.error(f"Error determining system architecture: {e}")
            return "unknown"
