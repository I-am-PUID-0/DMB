from base import *
from utils.global_logger import logger
import psycopg2
from psycopg2 import sql


SENSITIVE_KEY_PATTERN = re.compile(
    r"API|TOKEN|URL|HOST|PASSWORD|KEY|SECRET|USERNAME", re.IGNORECASE
)


def obfuscate_value(key, value, visible_chars=4):
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, bool):
        return str(value)
    if not value or not SENSITIVE_KEY_PATTERN.search(key) or value is None:
        return value
    return value[:visible_chars] + "*" * (len(value) - visible_chars)


def save_server_config(backend_url, api_key, config_dir="/config"):
    server_config = {"backendUrl": backend_url, "apiKey": api_key}

    os.makedirs(config_dir, exist_ok=True)

    config_file_path = os.path.join(config_dir, "server.json")

    try:
        with open(config_file_path, "w") as config_file:
            dump(server_config, config_file, indent=4)
            logger.info(f"Server config saved to {config_file_path}")
    except IOError as e:
        logger.error(f"Error saving server config: {e}")


def load_api_key_from_file(settings_file_path="/riven/backend/data/settings.json"):
    try:
        with open(settings_file_path, "r") as file:
            settings = load(file)
            api_key = settings.get("api_key")
            backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8080")

            if api_key:
                logger.info(f"API key loaded successfully from {settings_file_path}")

                save_server_config(backend_url, api_key)

                return api_key
            else:
                return None
    except FileNotFoundError:
        logger.error(f"Settings file {settings_file_path} not found")
        return None
    except JSONDecodeError as e:
        logger.error(f"Error parsing {settings_file_path}: {e}")
        return None


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

    api_key = os.getenv("BACKEND_API_KEY")
    if not api_key:
        logger.debug(
            "BACKEND_API_KEY not set in environment, attempting to load from settings.json"
        )
        api_key = load_api_key_from_file()
        if api_key:
            os.environ["BACKEND_API_KEY"] = api_key
        else:
            logger.debug("BACKEND_API_KEY not set")

    if ZILEAN is not None and ZILEAN.lower() == "true":
        set_env_variable("SCRAPING_ZILEAN_URL", None, "http://localhost:8182")

    env_vars = {
        "DOWNLOADERS_REAL_DEBRID_API_KEY": RDAPIKEY,
        "UPDATERS_PLEX_URL": PLEXADD,
        "UPDATERS_PLEX_TOKEN": PLEXTOKEN,
        "CONTENT_OVERSEERR_URL": SEERRADD,
        "CONTENT_OVERSEERR_API_KEY": SEERRAPIKEY,
        "SYMLINK_RCLONE_PATH": SYMLINKRCLONEPATH,
        "SYMLINK_LIBRARY_PATH": SYMLINKLIBRARYPATH,
        "BACKEND_URL": RIVENBACKENDURL,
        "DIALECT": RFDIALECT,
        "DATABASE_URL": RIVENDATABASEURL,
        "DATABASE_HOST": RIVENDATABASEHOST,
        "BACKEND_API_KEY": api_key,
    }

    default_env_vars = {
        "SYMLINK_RCLONE_PATH": f"{RCLONEDIR}/{RCLONEMN}/__all__",
        "SYMLINK_LIBRARY_PATH": "/mnt",
        "DATABASE_HOST": f"postgresql+psycopg2://{postgres_user}:{postgres_password}@{db_host}/{postgres_db}",
        "DATABASE_URL": f"postgres://{postgres_user}:{postgres_password}@{db_host}/{postgres_db}",
        "BACKEND_URL": "http://127.0.0.1:8080",
        "DIALECT": "postgres",
    }

    for key, value in env_vars.items():
        set_env_variable(key, value, default_env_vars.get(key))


def get_api_headers():
    api_key = os.getenv("BACKEND_API_KEY")

    if not api_key:
        return {}

    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    return headers


def get_backend_urls():
    base_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8080")
    api_key = os.getenv("BACKEND_API_KEY")

    if api_key:
        settings_url = f"{base_url}/api/v1/settings"
    else:
        settings_url = f"{base_url}/settings"

    return {
        "settings_url": settings_url,
        "set_url": f"{settings_url}/set",
        "save_url": f"{settings_url}/save",
        "get_all": f"{settings_url}/get/all",
    }


def fetch_settings(url, headers, max_retries=10, delay=5):
    for attempt in range(max_retries):
        try:
            logger.info(
                f"Attempt {attempt + 1}/{max_retries} to fetch settings from {url}"
            )
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        logger.info(
                            f"Successfully fetched settings on attempt {attempt + 1}"
                        )
                        return data, None
                    else:
                        return None, f"Unexpected JSON format: {data}"
                except ValueError as e:
                    return None, f"Error parsing JSON: {e}"
            elif response.status_code == 404:
                logger.error(f"Endpoint not found: {url}. Response: {response.text}")
                return None, f"404 Not Found: {response.text}"
            else:
                logger.error(
                    f"Failed to fetch settings: Status code {response.status_code}, Response: {response.text}"
                )
        except requests.ConnectionError as e:
            logger.error(f"Error fetching settings: {e}")

        if attempt < max_retries - 1:
            logger.info(f"Retrying in {delay} seconds... ({attempt + 1}/{max_retries})")
            time.sleep(delay)
        else:
            logger.error(f"Max retries reached. Failed to fetch settings from {url}")
            return None, "Max retries reached"


def get_env_value(key, default=None):
    env_key = key.replace(".", "_").upper()
    value = os.getenv(env_key, default)
    obfuscated_value = obfuscate_value(key, value)
    logger.debug(
        f"Checking environment variable for key '{env_key}': '{obfuscated_value}'"
    )
    return value


def update_settings(current_settings, updated_settings, payload, prefix=""):
    if not isinstance(current_settings, dict):
        logger.error(
            f"Expected a dictionary for settings, but got {type(current_settings)}: {current_settings}"
        )
        return
    for key, value in current_settings.items():
        full_key = f"{prefix}.{key}" if prefix else key
        logger.debug(f"Processing key '{full_key}' with value Type: {type(value)}")
        if key == "debug":
            log_level = os.getenv("LOG_LEVEL", "").upper()
            if log_level == "DEBUG":
                updated_settings["debug"] = True
                payload.append({"key": full_key, "value": True})
                logger.info(f"LOG_LEVEL is DEBUG, setting 'debug' to True")
            else:
                updated_settings["debug"] = False
                payload.append({"key": full_key, "value": False})
                logger.info(f"LOG_LEVEL is not DEBUG, setting 'debug' to False")
            continue
        env_value = get_env_value(full_key)
        if isinstance(value, dict):
            nested_updated = {}
            update_settings(value, nested_updated, payload, full_key)
            if nested_updated:
                updated_settings[key] = nested_updated
                meaningful_change = any(k in nested_updated for k in value)
                if meaningful_change:
                    if "enabled" in value:
                        updated_settings[key]["enabled"] = True
                        payload.append({"key": f"{full_key}.enabled", "value": True})
                        logger.debug(
                            f"'{full_key}.enabled' set to True due to updates in nested settings"
                        )
                    elif "enable" in value:
                        updated_settings[key]["enable"] = True
                        payload.append({"key": f"{full_key}.enable", "value": True})
                        logger.debug(
                            f"'{full_key}.enable' set to True due to updates in nested settings"
                        )
        elif env_value is not None:
            try:
                if env_value.lower() in ["true", "false"]:
                    updated_settings[key] = env_value.lower() == "true"
                elif env_value.isdigit():
                    updated_settings[key] = int(env_value)
                else:
                    try:
                        updated_settings[key] = float(env_value)
                    except ValueError:
                        updated_settings[key] = env_value
                payload.append({"key": full_key, "value": updated_settings[key]})
                obfuscated_value = obfuscate_value(full_key, updated_settings[key])
                logger.debug(
                    f"Setting '{full_key}' updated to '{obfuscated_value}' from environment variable"
                )
            except ValueError:
                logger.error(f"ValueError converting environment variable '{full_key}'")
        else:
            logger.debug(
                f"No environment variable found for '{full_key}', keeping original value."
            )
        logger.debug(f"Processed setting for '{key}'")


def load_settings():
    time.sleep(10)
    logger.info("Loading Riven settings")
    set_env_variables()
    urls = get_backend_urls()
    get_all = urls["get_all"]
    headers = get_api_headers()
    try:

        response, error = fetch_settings(get_all, headers)

        if error:
            logger.error(f"Failed to load settings: {error}")
            return

        if not isinstance(response, dict):
            logger.error(f"Unexpected type for settings response: {type(response)}")
            return

        current_settings = response
        if not isinstance(current_settings, dict):
            logger.error(
                f"Unexpected type for current settings: {type(current_settings)}"
            )
            return
        updated_settings = {}
        payload = []
        if current_settings:
            update_settings(current_settings, updated_settings, payload)
        else:
            logger.error("No current settings data to update")

        logger.debug(f"Updated settings payload")

        if not payload:
            logger.info("No settings to update.")
            return

        set_url = urls["set_url"]
        save_url = urls["save_url"]
        max_retries = 10
        for attempt in range(max_retries):
            try:
                response = requests.post(set_url, json=payload, headers=headers)
                if response.status_code == 200:
                    save_response = requests.post(save_url, headers=headers)
                    if save_response.status_code == 200:
                        logger.info("Settings saved successfully.")
                    else:
                        logger.error(f"Failed to save settings: {save_response.text}")
                    break
                else:
                    logger.error(f"Failed to set settings: {response.text}")
            except requests.ConnectionError as e:
                logger.error(f"Error loading Riven settings: {e}")
                if attempt < max_retries - 1:
                    logger.info(
                        f"Retrying in 5 seconds... ({attempt + 1}/{max_retries})"
                    )
                    time.sleep(5)
                else:
                    raise
    except Exception as e:
        logger.error(f"Error loading Riven settings: {e}")
        raise


if __name__ == "__main__":
    load_settings()
