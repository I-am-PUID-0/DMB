from base import *
from utils.logger import *


logger = get_logger()

def set_debug_level(env_var_name):
    try:
        log_level = os.getenv(env_var_name)
        logger.debug(f"Retrieved log_level: {log_level} for {env_var_name}")
        if log_level in ['DEBUG', '2']:
            os.environ['DEBUG'] = "true"
        else:
            os.environ['DEBUG'] = "false"
        logger.debug(f"{env_var_name} set to {log_level}") 
    except Exception as e:
        logger.error(f"Error setting debug for {env_var_name}: {e}")
        

def set_env_variable(key, value):
    try:
        if value:
            os.environ[key] = value
            logger.debug(f"Successfully set {key}")
    except Exception as e:
        logger.error(f"Error setting {key}: {e}")
env_vars = {
    'DOWNLOADERS_REAL_DEBRID_API_KEY': RDAPIKEY,
    'PLEX_URL': PLEXADD,
    'CONTENT_OVERSEERR_URL': SEERRADD,
    'CONTENT_OVERSEERR_API_KEY': SEERRAPIKEY,
    'SYMLINK_RCLONE_PATH': f"/data/{RCLONEMN}/__all__",
    'SYMLINK_LIBRARY_PATH': "/mnt"
}


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
    for key, value in env_vars.items():
        set_env_variable(key, value)
    #set_debug_level('RIVEN_LOG_LEVEL') # An error occurred in the Riven setup: 'bool' object has no attribute 'items'
    #set_debug_level('DMB_LOG_LEVEL') # An error occurred in the Riven setup: 'bool' object has no attribute 'items'
       
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