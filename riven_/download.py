from base import *

logger = get_logger()

def get_latest_release():
    try:
        target = './riven'
        with requests.get('https://github.com/rivenmedia/riven/archive/refs/heads/main.zip', timeout=10) as r:
            z = zipfile.ZipFile(io.BytesIO(r.content))
            for file_info in z.infolist():
                if file_info.is_dir() or not file_info.filename.startswith('riven-main/') or 'data/' in file_info.filename:
                    continue

                fpath = os.path.join(target, file_info.filename.split('/', 1)[1])
                os.makedirs(os.path.dirname(fpath), exist_ok=True)
                with open(fpath, 'wb') as dst, z.open(file_info, 'r') as src:
                    shutil.copyfileobj(src, dst)
        return True, None
    except Exception as e:
        logger.error(f"Error downloading latest riven release: {e}")
        return False, str(e)
