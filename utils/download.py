from urllib import response
from base import *
from utils.logger import *


class Downloader:
    def __init__(self):
        self.logger = get_logger()

    def get_latest_release(self, repo_owner, repo_name):
        try:    
            self.logger.info(f"Fetching latest {repo_name} release.")
            headers = {}
            if GHTOKEN:
                headers['Authorization'] = f'token {GHTOKEN}'
            api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code != 200:
                self.logger.error("Unable to access the repository API. Status code: %s", response.status_code)
                return None, "Error: Unable to access the repository API."
            latest_release = response.json()
            version_tag = latest_release['tag_name']
            self.logger.info(f"{repo_name} latest release: %s", version_tag)
            return version_tag, None
        except Exception as e:
            return None, str(e)

    def get_branch(self, repo_owner, repo_name, branch, headers):
        zip_folder_name = f'{repo_name}-{branch.replace("/", "-")}'
        branch_url = f"https://github.com/{repo_owner}/{repo_name}/archive/refs/heads/{branch}.zip"
        self.logger.debug(f"Requesting {repo_name} release from {branch_url}")
        response = requests.get(branch_url, headers=headers, timeout=10)
        if response.status_code != 200:
            self.logger.error(f"Failed to get branch {branch} from {repo_name}. Status code: {response.status_code}")
            return None, f"Failed to get branch {branch} from {repo_name}. Status code: {response.status_code}"                                                                                
        return branch_url, zip_folder_name

    def fetch_github_release_info(self, repo_owner, repo_name, release_version, headers):
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{release_version}"
        self.logger.info(f"Fetching release information from {api_url}")
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code != 200:
            self.logger.error("Failed to get release assets. Status code: %s", response.status_code)
            return None, f"Failed to get release assets. Status code: {response.status_code}"
        return response.json(), None

    def find_asset_download_url(self, release_info, architecture=None):
        assets = release_info.get('assets', [])     
        for asset in assets:
            if architecture and architecture in asset['name']:
                self.logger.debug(f"Assets found: {assets}")
                self.logger.debug(f"Download URL: {asset['browser_download_url']}")
                return asset['browser_download_url'], asset['id']
        if assets:
            self.logger.warning("No matching asset found for architecture: %s. Falling back to the first available asset.", architecture)
            self.logger.debug(f"Assets found: {assets}")
            self.logger.debug(f"Download URL: {asset['browser_download_url']}")
            return assets[0]['browser_download_url'], assets[0]['id']
        zipball_url = release_info.get('zipball_url')
        tarball_url = release_info.get('tarball_url')
        if zipball_url:
            self.logger.info("No assets found. Using zipball_url.")
            return zipball_url, None
        if tarball_url:
            self.logger.info("No assets found. Using tarball_url.")
            return tarball_url, None

        self.logger.error("No assets or zipball/tarball URL found for the release.")
        return None, None

    def download_and_extract(self, url, target_dir, zip_folder_name=None, headers=None, exclude_dirs=None):
        try:
            self.logger.info(f"Downloading from {url}")
            headers = headers or {"Accept": "application/vnd.github.v3+json"}
            with requests.get(url, headers=headers, timeout=10) as r:
                if r.status_code == 200:
                    self.logger.debug(f"{zip_folder_name} download successful. Content size: {len(r.content)} bytes")
                    try:
                        z = zipfile.ZipFile(io.BytesIO(r.content))
                        self.logger.debug(f"Extracting {zip_folder_name} to {target_dir}")
                    
                        for file_info in z.infolist():
                            self.logger.debug(f"Processing {file_info.filename}")
                            if file_info.is_dir():
                               # self.logger.debug(f"Skipping directory {file_info.filename}")
                                continue
                        
                            if zip_folder_name:
                                if fnmatch.fnmatch(file_info.filename, zip_folder_name + '*'):
                                   # self.logger.debug(f"Found matching filename: {file_info.filename}")
                                    parts = file_info.filename.split('/', 1)
                                    if len(parts) > 1:
                                        inner_path = parts[1]
                                       # self.logger.debug(f"Extracting with parts[1] {inner_path}")
                                    else:
                                        inner_path = parts[0]
                                       # self.logger.debug(f"Extracting with parts[0] {inner_path}")
                                    fpath = os.path.join(target_dir, inner_path)
                                   # self.logger.debug(f"Extracting {file_info.filename} to {fpath}")
                                elif len(z.infolist()) == 1:
                                    fpath = os.path.join(target_dir, file_info.filename)
                                   # self.logger.debug(f"Extracting single root file {file_info.filename} to {fpath}")
                                else:
                                   # self.logger.debug(f"Skipping file {file_info.filename}")
                                    continue
                            else:
                                fpath = os.path.join(target_dir, file_info.filename)
                               # self.logger.debug(f"Extracting {file_info.filename} to {fpath}")

                            if exclude_dirs and any(exclude_dir in file_info.filename for exclude_dir in exclude_dirs):
                               # self.logger.debug(f"Skipping file in excluded dir {exclude_dirs}: {file_info.filename}")
                                continue

                            try:
                                os.makedirs(os.path.dirname(fpath), exist_ok=True)
                                with open(fpath, 'wb') as dst, z.open(file_info, 'r') as src:
                                    shutil.copyfileobj(src, dst)
                               # self.logger.debug(f"Extracted {file_info.filename} to {fpath}")
                            except IndexError as ie:
                                self.logger.error(f"IndexError while processing {file_info.filename}: {ie}")
                                continue
                            except Exception as e:
                                self.logger.error(f"Error while extracting {file_info.filename}: {e}")
                                continue

                        self.logger.info(f"Successfully downloaded {zip_folder_name} and extracted to {target_dir}")
                        return True, None
                    except zipfile.BadZipFile as e:
                        self.logger.error(f"Failed to create ZipFile object: {e}")
                        return False, str(e)
                else:
                    return False, f"Failed to download. Status code: {r.status_code}"
        except Exception as e:
            self.logger.error(f"Error in download and extraction: {e}")
            return False, str(e)

    def set_permissions(self, file_path, mode):
        try:
            os.chmod(file_path, mode)
            self.logger.info(f"Set permissions for {file_path} to {oct(mode)}")
        except Exception as e:
            self.logger.error(f"Failed to set permissions for {file_path}: {e}")

    def get_architecture(self):
        try:
            arch_map = {
                ('AMD64', 'Windows'): 'windows-amd64',
                ('AMD64', 'Linux'): 'linux-amd64',
                ('AMD64', 'Darwin'): 'darwin-amd64',
                ('x86_64', 'Linux'): 'linux-amd64',  
                ('x86_64', 'Darwin'): 'darwin-amd64', 
                ('arm64', 'Linux'): 'linux-arm64',
                ('arm64', 'Darwin'): 'darwin-arm64',
                ('aarch64', 'Linux'): 'linux-arm64',  
                ('mips64', 'Linux'): 'linux-mips64',
                ('mips64le', 'Linux'): 'linux-mips64le',
                ('ppc64le', 'Linux'): 'linux-ppc64le',
                ('riscv64', 'Linux'): 'linux-riscv64',
                ('s390x', 'Linux'): 'linux-s390x',
            }
            system_arch = platform.machine()
            system_os = platform.system()
            self.logger.debug("System Architecture: %s, Operating System: %s", system_arch, system_os)
            return arch_map.get((system_arch, system_os), 'unknown')
        except Exception as e:
            self.logger.error(f"Error determining system architecture: {e}")
            return 'unknown'

