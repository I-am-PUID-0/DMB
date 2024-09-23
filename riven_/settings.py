from base import *
from utils.logger import *
import psycopg2
from psycopg2 import sql

logger = get_logger()

SENSITIVE_KEY_PATTERN = re.compile(r'API|TOKEN|URL|HOST|PASSWORD|KEY|SECRET|USERNAME', re.IGNORECASE)

def obfuscate_value(key, value, visible_chars=4):
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, bool):
        return str(value)
    if not value or not SENSITIVE_KEY_PATTERN.search(key) or value is None:
        return value
    return value[:visible_chars] + '*' * (len(value) - visible_chars)


def set_env_variables():
    def set_env_variable(key, value, default=None):
        try:
            if value is not None:
                os.environ[key] = value
            elif default is not None and key not in os.environ:
                os.environ[key] = default
            if key in os.environ:
                obfuscated_value = obfuscate_value(key, os.environ[key])
                logger.debug(f"Successfully set {key} to {obfuscated_value}")
            else:
                logger.debug(f"{key} not set because no value or default was provided")
        except Exception as e:
            logger.error(f"Error setting {key}: {e}")

    if ZILEAN is not None and ZILEAN.lower() == 'true':
        set_env_variable('SCRAPING_ZILEAN_URL', None, 'http://localhost:8182')

    env_vars = {
        'DOWNLOADERS_REAL_DEBRID_API_KEY': RDAPIKEY,
        'UPDATERS_PLEX_URL': PLEXADD,
        'UPDATERS_PLEX_TOKEN': PLEXTOKEN,
        'CONTENT_OVERSEERR_URL': SEERRADD,
        'CONTENT_OVERSEERR_API_KEY': SEERRAPIKEY,
        'SYMLINK_RCLONE_PATH': SYMLINKRCLONEPATH,
        'SYMLINK_LIBRARY_PATH': SYMLINKLIBRARYPATH,
        'BACKEND_URL': RIVENBACKENDURL,
        'DIALECT': RFDIALECT,
        'DATABASE_URL': RIVENDATABASEURL,
        'DATABASE_HOST': RIVENDATABASEHOST
    }

    default_env_vars = {
        'SYMLINK_RCLONE_PATH': f'{RCLONEDIR}/{RCLONEMN}/__all__',
        'SYMLINK_LIBRARY_PATH': '/mnt',
        'DATABASE_HOST': f'postgresql+psycopg2://{postgres_user}:{postgres_password}@{db_host}/{postgres_db}',
        'DATABASE_URL': f'postgres://{postgres_user}:{postgres_password}@{db_host}/{postgres_db}',
        'BACKEND_URL': 'http://127.0.0.1:8080',
        'DIALECT': 'postgres'
    }

    for key, value in env_vars.items():
        set_env_variable(key, value, default_env_vars.get(key))

def fetch_settings(url, max_retries=10, delay=5):
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries} to fetch settings from {url}")
            response = requests.get(url)
            if response.status_code == 200:
                try:
                    data = response.json()  
                    if isinstance(data, dict): 
                        logger.info(f"Successfully fetched settings on attempt {attempt + 1}")
                        return data
                    else:
                        logger.error(f"Unexpected JSON format: {data}")
                except ValueError as e:
                    logger.error(f"Error parsing JSON response: {e}")
            else:
                logger.error(f"Failed to fetch settings: Status code {response.status_code}, Response: {response.text}")       
        except requests.ConnectionError as e:
            logger.error(f"Error fetching settings: {e}")        
        if attempt < max_retries - 1:
            logger.info(f"Retrying in {delay} seconds... ({attempt + 1}/{max_retries})")
            time.sleep(delay)
        else:
            logger.error(f"Max retries reached. Failed to fetch settings from {url}")
            raise
    return None

def get_env_value(key, default=None):
    env_key = key.replace('.', '_').upper()
    value = os.getenv(env_key, default)
    if value is None:
        logger.debug(f"Environment variable for '{key}' not found")
    logger.debug(f"Checking environment variable for key '{key}'")
    return value

def update_settings(current_settings, updated_settings, prefix=''):
    if not isinstance(current_settings, dict):
        logger.error(f"Expected a dictionary for settings, but got {type(current_settings)}: {current_settings}")
        return

    for key, value in current_settings.items():
        full_key = f"{prefix}.{key}" if prefix else key
        logger.debug(f"Processing key '{full_key}' with value Type: {type(value)}")
        if key == 'debug':
            log_level = os.getenv('LOG_LEVEL', '').upper()
            if log_level == 'DEBUG':
                updated_settings['debug'] = True
                logger.info(f"LOG_LEVEL is DEBUG, setting 'debug' to True")
            else:
                updated_settings['debug'] = False
                logger.info(f"LOG_LEVEL is not DEBUG, setting 'debug' to False")
            continue

        if isinstance(value, dict):
            nested_updated = {}
            update_settings(value, nested_updated, full_key)
            if nested_updated:
                updated_settings[key] = nested_updated
                if 'enabled' in value:
                    updated_settings[key]['enabled'] = True
                if 'enable' in value:
                    updated_settings[key]['enable'] = True

        elif isinstance(value, bool):
            updated_settings[key] = value
            obfuscated_value = obfuscate_value(full_key, str(value))
            logger.debug(f"Setting '{full_key}' updated with boolean value '{obfuscated_value}'")

        elif isinstance(value, list):
            updated_settings[key] = value
            obfuscated_value = obfuscate_value(full_key, str(value))
            logger.debug(f"Setting '{full_key}' updated with list value '{obfuscated_value}'")

        elif isinstance(value, (int, float, str)):
            env_value = get_env_value(full_key)
            if env_value is not None:
                try:
                    if env_value.lower() in ['true', 'false']:
                        updated_settings[key] = env_value.lower() == 'true'
                    elif env_value.isdigit():
                        updated_settings[key] = int(env_value)
                    else:
                        try:
                            updated_settings[key] = float(env_value)
                        except ValueError:
                            updated_settings[key] = env_value
                except ValueError:
                    logger.error(f"ValueError converting environment variable '{full_key}': {env_value}")
                obfuscated_value = obfuscate_value(full_key, env_value)
                logger.debug(f"Setting '{full_key}' updated with value '{obfuscated_value}' from environment variable")
            else:
                updated_settings[key] = value
                if isinstance(value, (int, float)):
                    logger.debug(f"Setting '{full_key}' retained its numeric value: {value}")
                else:
                    obfuscated_value = obfuscate_value(full_key, value)
                    logger.debug(f"Setting '{full_key}' retained its value: {obfuscated_value}")
        else:
            logger.error(f"Unsupported value type for key '{key}': {type(value)}")
            updated_settings[key] = value

        logger.debug(f"Processed setting for '{key}'")

def load_settings():
    logger.info("Loading Riven settings")

    set_env_variables()

    try:
        get_url = 'http://127.0.0.1:8080/settings/get/all'
        time.sleep(5)
        settings_response = fetch_settings(get_url)

        if not isinstance(settings_response, dict):
            logger.error(f"Unexpected type for settings response: {type(settings_response)}")
            return
        if not settings_response.get('success'):
            logger.error("Failed to fetch current settings")
            return

        current_settings = settings_response.get('data', {})
        if not isinstance(current_settings, dict):
            logger.error(f"Unexpected type for current settings: {type(current_settings)}")
            return
        
        updated_settings = {}
        if current_settings:  
            update_settings(current_settings, updated_settings)
        else:
            logger.error("No current settings data to update")

        logger.debug(f"Updated settings payload")
        payload = []
        for key, value in updated_settings.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if subvalue != {}:
                        payload.append({"key": f"{key}.{subkey}", "value": subvalue})
            else:
                payload.append({"key": key, "value": value})

        if not payload:
            logger.info("No settings to update.")
            return

        set_url = 'http://127.0.0.1:8080/settings/set'
        save_url = 'http://127.0.0.1:8080/settings/save'
        max_retries = 10
        for attempt in range(max_retries):
            try:
                response = requests.post(set_url, json=payload)
                if response.status_code == 200:
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