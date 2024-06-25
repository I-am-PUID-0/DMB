from re import DEBUG
from base import *


logger = get_logger()

try:
    if os.getenv('DMB_LOG_LEVEL') == DEBUG:
        os.environ['DEBUG'] = "true"
except Exception as e:
    logger.error(f"Error setting debug: {e}")
try:
    if os.getenv('RIVEN_LOG_LEVEL') == DEBUG:
        os.environ['DEBUG'] = "true"
except Exception as e:
    logger.error(f"Error setting debug: {e}")    
try: 
    if RDAPIKEY:
        os.environ['DOWNLOADERS_REAL_DEBRID_API_KEY'] = RDAPIKEY  
except Exception as e:
    logger.error(f"Error setting downloaders.real_debrid.api.key: {e}")
try:
    if PLEXADD:
        os.environ['PLEX_URL'] = PLEXADD
except Exception as e:
    logger.error(f"Error setting plex.url: {e}")
try: 
    if SEERRADD:
        os.environ['CONTENT_OVERSEERR_URL'] = SEERRADD
except Exception as e:
    logger.error(f"Error setting content.overseerr.url: {e}")
try:
    if SEERRAPIKEY:
        os.environ['CONTENT_OVERSEERR_API_KEY'] = SEERRAPIKEY
except Exception as e:
    logger.error(f"Error setting content.overseerr.api.key: {e}")
try:
    os.environ['SYMLINK_RCLONE_PATH'] = f"/data/{RCLONEMN}/__all__"
except Exception as e:
    logger.error(f"Error setting symlink.rclone.path: {e}")
try: 
    os.environ['SYMLINK_LIBRARY_PATH'] = "/mnt"
except Exception as e:
    logger.error(f"Error setting symlink.library.path: {e}")

def fetch_settings(url, max_retries=5, delay=5):
    time.sleep(delay)
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                logger.debug(f"Successfully fetched settings on attempt {attempt + 1}")
                return response.json()
            else:
                logger.error(f"Failed to fetch settings: {response.text}")
        except requests.ConnectionError as e:
            logger.error(f"Error fetching settings: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {delay} seconds... ({attempt + 1}/{max_retries})")
                time.sleep(delay)
            else:
                raise
    return None

def get_env_value(key, default=None):
    env_key = key.replace('.', '_').upper()
    value = os.getenv(env_key, default)
    logger.debug(f"Checking environment variable for key '{env_key}': '{value}'")
    return value

def update_settings(current_settings, updated_settings, prefix=''):
    for key, value in current_settings.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            nested_updated = {}
            update_settings(value, nested_updated, full_key)
            if nested_updated:
                updated_settings[key] = nested_updated
                if 'enabled' in value:
                    updated_settings[key]['enabled'] = True
                if 'enable' in value:
                    updated_settings[key]['enable'] = True
        else:
            env_value = get_env_value(full_key)
            if env_value is not None:
                try:
                    if env_value.lower() in ['true', 'false']:
                        env_value = env_value.lower() == 'true'
                    elif env_value.isdigit():
                        env_value = int(env_value)
                    else:
                        try:
                            env_value = float(env_value)
                        except ValueError:
                            pass  
                except ValueError:
                    logger.error(f"ValueError converting environment variable '{full_key}': {env_value}")
                    pass
                updated_settings[key] = env_value
                logger.debug(f"Setting '{full_key}' updated with value '{env_value}' from environment variable")
                if 'enabled' in current_settings:
                    updated_settings['enabled'] = True
                if 'enable' in current_settings:
                    updated_settings['enable'] = True

def load_settings():
    logger.info("Loading Riven settings")
    try:
        get_url = 'http://127.0.0.1:8080/settings/get/all'
        settings_response = fetch_settings(get_url)
        if not settings_response or not settings_response.get('success'):
            logger.error("Failed to fetch current settings")
            return
        current_settings = settings_response.get('data', {})
        updated_settings = {}
        update_settings(current_settings, updated_settings)
        payload = [{"key": f"{prefix}.{key}", "value": value} for prefix, subdict in updated_settings.items() for key, value in subdict.items() if value != {}]
        set_url = 'http://127.0.0.1:8080/settings/set'
        save_url = 'http://127.0.0.1:8080/settings/save'
        if not payload:
            logger.info("No settings to update.")
            return
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = requests.post(set_url, json=payload)
                if response.status_code == 200:
                    for item in payload:
                        logger.debug(f"Setting '{item['key']}' updated with value '{item['value']}'")
                    save_response = requests.post(save_url)
                    if save_response.status_code == 200:
                        logger.info('Settings saved successfully.')
                    else:
                        logger.error(f'Failed to save settings: {save_response.text}')
                    break
                else:
                    logger.error(f'Failed to set settings: {response.text}')
            except requests.ConnectionError as e:
                logger.error(f"Error loading Riven settings: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in 5 seconds... ({attempt + 1}/{max_retries})")
                    time.sleep(5)
                else:
                    raise

    except Exception as e:
        logger.error(f"Error loading Riven settings: {e}")
        raise

if __name__ == "__main__":
    load_settings()
