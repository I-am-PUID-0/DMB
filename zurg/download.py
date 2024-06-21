from base import *


logger = get_logger()

class CustomVersion:
    def __init__(self, main_version, hotfix=0, subversion=''):
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
        return (self.main_version, self.hotfix, self.subversion) == (other.main_version, other.hotfix, other.subversion)

    def __str__(self):
        version_str = f'v{self.main_version}'
        if self.hotfix > 0:
            version_str += f'-hotfix.{self.hotfix}'
        if self.subversion:
            version_str += f'-{self.subversion}'
        return version_str

def parse_custom_version(version_str):
    try:
        main_version_part, *hotfix_part = version_str.lstrip('v').split('-hotfix.')
        main_version = parse_version(main_version_part)
        hotfix_number = 0
        subversion = ''
        if hotfix_part:
            hotfix_and_subversion = hotfix_part[0].split('-', 1)
            hotfix_number = int(hotfix_and_subversion[0]) if hotfix_and_subversion[0].isdigit() else 0
            if len(hotfix_and_subversion) > 1:
                subversion = hotfix_and_subversion[1]
        return CustomVersion(main_version, hotfix_number, subversion)
    except Exception as e:
        logger.error(f"Error parsing version string '{version_str}': {e}")
        return None

def get_latest_release(repo_owner, repo_name):
    try:
        logger.info("Fetching latest Zurg release.")
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        response = requests.get(api_url, timeout=10)
        if response.status_code != 200:
            logger.error("Unable to access the repository API. Status code: %s", response.status_code)
            return None, "Error: Unable to access the repository API."
        latest_release = response.json()
        version_tag = latest_release['tag_name']
        logger.info("Zurg latest release: %s", version_tag)
        return version_tag, None
    except Exception as e:
        logger.error(f"Error fetching latest Zurg release: {e}")
        return None, str(e)

def get_architecture():
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
        logger.debug("System Architecture: %s, Operating System: %s", system_arch, system_os)
        return arch_map.get((system_arch, system_os), 'unknown')
    except Exception as e:
        logger.error(f"Error determining system architecture: {e}")
        return 'unknown'

def download_and_unzip_release(repo_owner, repo_name, release_version, architecture):
    try:
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{release_version}"
        response = requests.get(api_url, timeout=10)
        if response.status_code != 200:
            logger.error("Failed to get release assets. Status code: %s", response.status_code)
            return False
        assets = response.json().get('assets', [])
        download_url = ""
        for asset in assets:
            if architecture in asset['name']:
                download_url = asset['browser_download_url']
                break
        if not download_url:
            logger.error("No matching asset found for architecture: %s", architecture)
            return False        
        response = requests.get(download_url, timeout=10)
        logger.debug("Downloading from URL: %s", download_url)
        if response.status_code == 200:
            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
            zip_file.extractall('zurg')
            logger.info(f"Download and extraction of zurg-{release_version}-{architecture} successful.")
            extracted_files = os.listdir('zurg')
            logger.debug(f"Extracted files: {extracted_files}")           
            extracted_file_path = os.path.join('zurg', 'zurg')
            os.chmod(extracted_file_path, 0o755)
            logger.debug("Set 'zurg' file as executable.")
            os.environ['ZURG_CURRENT_VERSION'] = release_version
        else:
            logger.error("Unable to download the file. Status code: %s", response.status_code)
            return False
        return True
    except Exception as e:
        logger.error(f"Error in download and extraction: {e}")
        return False

def version_check():
    try:
        architecture = get_architecture()
        os.environ['CURRENT_ARCHITECTURE'] = architecture
        repo_owner = 'debridmediamanager'
        repo_name = 'zurg-testing'
        
        if ZURGVERSION:
            release_version = ZURGVERSION if ZURGVERSION.startswith('v') else 'v' + ZURGVERSION
            logger.info("Using release version from environment variable: %s", release_version)
        else:      
            release_version, error = get_latest_release(repo_owner, repo_name)
            if error:
                logger.error(error)
                raise Exception("Failed to get the latest release version.")
        if not download_and_unzip_release(repo_owner, repo_name, release_version, architecture):
            raise Exception("Failed to download and extract the release.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        exit(1)
