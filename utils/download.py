from base import *
from utils.logger import *


logger = get_logger()

def download_and_extract(url, target_dir, zip_folder_name=None, headers=None, exclude_dirs=None):
    try:
        logger.info(f"Downloading from {url}")
        with requests.get(url, headers=headers, timeout=10) as r:
            if r.status_code == 200:
                logger.debug(f"{zip_folder_name} download successful. Content size: {len(r.content)} bytes")
                try:
                    z = zipfile.ZipFile(io.BytesIO(r.content))
                    #logger.debug(f"Zip file contents: {z.namelist()}") # Break in case of emergency
                    for file_info in z.infolist():
                        #logger.debug(f"Processing file: {file_info.filename}") # Break in case of emergency
                        if file_info.is_dir():
                            #logger.debug(f"Skipping directory: {file_info.filename}") # Break in case of emergency
                            continue
                        if zip_folder_name and not file_info.filename.startswith(zip_folder_name):
                            logger.debug(f"File not in specified folder. Adjusting extraction: {file_info.filename}")
                            fpath = os.path.join(target_dir, file_info.filename)
                        else:
                            fpath = os.path.join(target_dir, file_info.filename.split('/', 1)[-1])
                        if exclude_dirs and any(exclude_dir in file_info.filename for exclude_dir in exclude_dirs):
                            logger.debug(f"Skipping file in excluded dir {exclude_dirs}: {file_info.filename}")
                            continue
                        try:
                            os.makedirs(os.path.dirname(fpath), exist_ok=True)
                            with open(fpath, 'wb') as dst, z.open(file_info, 'r') as src:
                                shutil.copyfileobj(src, dst)
                            #logger.debug(f"Extracted file to: {fpath}") # Break in case of emergency
                        except IndexError as ie:
                            logger.error(f"IndexError while processing {file_info.filename}: {ie}")
                            continue
                        except Exception as e:
                            logger.error(f"Error while extracting {file_info.filename}: {e}")
                            continue
                    logger.info(f"Successfully downloaded {zip_folder_name} and extracted to {target_dir}")
                    return True, None
                except zipfile.BadZipFile as e:
                    logger.error(f"Failed to create ZipFile object: {e}")
                    return False, str(e)
            else:
                logger.error(f"Failed to download. Status code: {r.status_code}")
                return False, f"Failed to download. Status code: {r.status_code}"
    except Exception as e:
        logger.error(f"Error in download and extraction: {e}")
        return False, str(e)

def set_permissions(file_path, mode):
    try:
        os.chmod(file_path, mode)
        logger.info(f"Set permissions for {file_path} to {oct(mode)}")
    except Exception as e:
        logger.error(f"Failed to set permissions for {file_path}: {e}")
