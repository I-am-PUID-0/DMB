from utils import postgres
from utils.config_loader import CONFIG_MANAGER
from utils.global_logger import logger
from utils.download import Downloader
from utils.versions import Versions
from utils.user_management import chown_recursive
import yaml, os, shutil, random, subprocess, re

user_id = CONFIG_MANAGER.get("puid")
group_id = CONFIG_MANAGER.get("pgid")
downloader = Downloader()
versions = Versions()


def setup_release_version(process_handler, config, process_name, key):
    if key == "plex_debrid":
        return False, "Release version not supported for plex_debrid."

    logger.info(f"Using release version {config['release_version']} for {process_name}")

    if config.get("clear_on_update"):
        exclude_dirs = config.get("exclude_dirs", [])
        success, error = clear_directory(config["config_dir"], exclude_dirs)
        if not success:
            return False, f"Failed to clear directory: {error}"
    else:
        exclude_dirs = None

    if key == "zurg":
        success, error = downloader.download_release_version(
            process_name=process_name,
            key=key,
            repo_owner=config["repo_owner"],
            repo_name=config["repo_name"],
            release_version=config["release_version"],
            target_dir=config["config_dir"],
            zip_folder_name=None,
            exclude_dirs=exclude_dirs,
        )
        if not success:
            return False, f"Failed to download release: {error}"

        downloader.set_permissions(config["command"], 0o755)
        if not os.path.exists(os.path.join(config["config_dir"], "logs")):
            os.makedirs(os.path.join(config["config_dir"], "logs"), exist_ok=True)
            chown_recursive(
                config["config_dir"],
                CONFIG_MANAGER.get("puid"),
                CONFIG_MANAGER.get("pgid"),
            )

        # chown_recursive(config["config_dir"], user_id, group_id)

    else:
        success, error = downloader.download_release_version(
            process_name=process_name,
            key=key,
            repo_owner=config["repo_owner"],
            repo_name=config["repo_name"],
            release_version=config["release_version"],
            target_dir=config["config_dir"],
            zip_folder_name=None,
            exclude_dirs=exclude_dirs,
        )
        if not success:
            return False, f"Failed to download release: {error}"

    if key == "zilean":
        versions.version_write(
            process_name,
            key,
            version_path=os.path.join(config["config_dir"], "version.txt"),
            version=config["release_version"],
        )

    elif key == "decypharr":
        versions.version_write(
            process_name,
            key,
            version_path=os.path.join(config["config_dir"], "version.txt"),
            version=config["release_version"],
        )

    success, error = additional_setup(process_handler, process_name, config, key)
    if not success:
        return False, error

    return True, None


def setup_branch_version(process_handler, config, process_name, key):
    if key == "zurg":
        return False, "Branch version not supported for Zurg."
    else:
        logger.info(f"Using branch {config['branch']} for {process_name}")
        branch_url, zip_folder_name = downloader.get_branch(
            config["repo_owner"], config["repo_name"], config["branch"]
        )
        if not branch_url:
            return False, f"Failed to fetch branch {config['branch']}"

        exclude_dirs = None
        if config.get("clear_on_update"):
            exclude_dirs = config.get("exclude_dirs", [])
            success, error = clear_directory(config["config_dir"], exclude_dirs)
            if not success:
                return False, f"Failed to clear directory: {error}"

        success, error = downloader.download_and_extract(
            branch_url,
            config["config_dir"],
            zip_folder_name=zip_folder_name,
            exclude_dirs=exclude_dirs,
        )
        if not success:
            return False, f"Failed to download branch: {error}"

        success, error = additional_setup(process_handler, process_name, config, key)
        if not success:
            return False, error

    return True, None


def additional_setup(process_handler, process_name, config, key):
    if key == "riven_frontend":
        success, error = vite_modifications(config["config_dir"])
        if not success:
            return False, f"Failed to make vite modifications: {error}"

    if config.get("platforms"):
        success, error = setup_environment(
            process_handler, key, config["platforms"], config["config_dir"]
        )
        if not success:
            return (
                False,
                f"Failed to set up environment for {process_name}: {error}",
            )

    if key == "plex_debrid":
        success, error = chown_recursive(
            os.path.join(config["config_dir"], "config"), user_id, group_id
        )
        if not success:
            return False, error
    #    if user_id and group_id and not config["config_dir"].startswith("/zurg"):
    #        success, error = chown_recursive(config["config_dir"], user_id, group_id)
    #        if not success:
    #            return False, error

    return True, None


def setup_project(process_handler, process_name):
    if process_name in process_handler.setup_tracker:
        process_handler.logger.info(
            f"{process_name} is already set up. Skipping setup."
        )
        return True, None

    key, instance_name = CONFIG_MANAGER.find_key_for_process(process_name)
    if not key:
        raise ValueError(f"Key for {process_name} not found in the configuration.")

    config = CONFIG_MANAGER.get_instance(instance_name, key)
    if not config:
        raise ValueError(f"Configuration for {process_name} not found.")

    logger.info(f"Setting up {process_name}...")
    try:
        if config.get("release_version_enabled") and not config.get("auto_update"):
            repo_owner = config.get("repo_owner")
            repo_name = config.get("repo_name")
            nightly = "nightly" in config["release_version"].lower()
            prerelease = config.get("release_version").lower() == "prerelease"
            update_needed, update_info = versions.compare_versions(
                process_name,
                repo_owner,
                repo_name,
                instance_name,
                key,
                nightly=nightly,
                prerelease=prerelease,
            )

            if update_needed:
                logger.info(
                    f"Update needed for {process_name}: {update_info['latest_version']}, but using the requested version: {config['release_version']}"
                )
                success, error = setup_release_version(
                    process_handler, config, process_name, key
                )
                if not success:
                    return False, error
            else:
                logger.info(
                    f"No update needed for {process_name}: current version is {update_info['current_version']}, and requested version is: {config['release_version']}"
                )

        elif config.get("branch_enabled"):
            success, error = setup_branch_version(
                process_handler, config, process_name, key
            )
            if not success:
                return False, error

        if config.get("env_copy"):
            src, dest = config["env_copy"]["source"], config["env_copy"]["destination"]
            if os.path.exists(src):
                shutil.copy(src, dest)
                logger.info(f"Copied .env from {src} to {dest}")

        if config.get("env"):
            for env_key, value in config["env"].items():
                if isinstance(value, str) and "{" in value and "}" in value:
                    if "$" in value:
                        continue

                    if key == "zilean":
                        postgres_host = CONFIG_MANAGER.get("postgres").get(
                            "host", "127.0.0.1"
                        )
                        postgres_port = CONFIG_MANAGER.get("postgres").get("port", 5432)
                        postgres_user = CONFIG_MANAGER.get("postgres").get(
                            "user", "DMB"
                        )
                        postgres_password = CONFIG_MANAGER.get("postgres").get(
                            "password", "postgres"
                        )
                        value = (
                            value.replace("{postgres_host}", postgres_host)
                            .replace("{postgres_port}", str(postgres_port))
                            .replace("{postgres_user}", postgres_user)
                            .replace("{postgres_password}", postgres_password)
                        )

                    for placeholder in config.keys():
                        placeholder_pattern = f"{{{placeholder}}}"
                        if placeholder_pattern in value:
                            value = value.replace(
                                placeholder_pattern, str(config[placeholder])
                            )

                    config["env"][env_key] = value

        if key == "dmb_frontend":
            success, error = dmb_frontend_setup()
            if not success:
                return False, error

        if key == "riven_frontend":
            copy_server_config(
                "/config/server.json",
                os.path.join(config["config_dir"], "config/server.json"),
            )

        if key == "riven_backend":
            port = str(config.get("port", 8080))
            command = config.get("command", [])
            if not isinstance(command, list):
                raise ValueError(f"Unexpected type for command: {type(command)}")

            for i, arg in enumerate(command):
                if arg in ("-p", "--port") and i + 1 < len(command):
                    if command[i + 1] != "{port}":
                        command[i + 1] = "{port}"
                    break
            else:
                command.extend(["-p", "{port}"])

            formatted_command = [
                arg.format(port=port) if "{port}" in arg else arg for arg in command
            ]

            config["command"] = formatted_command

            symlink_library_path = config.get("symlink_library_path")
            if symlink_library_path and not os.path.exists(symlink_library_path):
                os.makedirs(symlink_library_path, exist_ok=True)
                os.chown(symlink_library_path, user_id, group_id)

        if key == "zurg":
            success, error = zurg_setup()
            if not success:
                return False, error

        if key == "zilean":
            config_app_wwwroot_dir = os.path.join(
                config["config_dir"], "app", "wwwroot"
            )
            config_wwwroot_dir = os.path.join(config["config_dir"], "wwwroot")
            if not os.path.exists(config_wwwroot_dir):
                os.symlink(config_app_wwwroot_dir, config_wwwroot_dir)

        if key == "rclone":
            success, error = rclone_setup()
            if not success:
                return False, error

        if key == "postgres":
            success, error = postgres.postgres_setup(process_handler)
            if not success:
                return False, error

        if key == "pgadmin":
            success, error = postgres.pgadmin_setup(process_handler)
            if not success:
                return False, error

        if key == "plex_debrid":
            success, error = plex_debrid_setup()
            if not success:
                return False, error

        if key == "phalanx_db":
            success, error = phalanx_setup(process_handler)
            if not success:
                return False, error

        if key == "decypharr":
            success, error = setup_decypharr()
            if not success:
                return False, error

        process_handler.setup_tracker.add(process_name)
        logger.debug(f"Post Setup tracker: {process_handler.setup_tracker}")
        logger.info(f"{process_name} setup complete")
        return True, None

    except Exception as e:
        return False, f"Error during setup of {process_name}: {e}"


def setup_decypharr():
    config = CONFIG_MANAGER.get("decypharr")
    if not config:
        return False, "Configuration for Decypharr not found."

    logger.info("Starting Decypharr setup...")

    try:
        decypharr_config_dir = config.get("config_dir")
        decypharr_config_file = config.get("config_file")
        decypharr_binary_file = config.get("binary_file", "decypharr")
        binary_path = os.path.join(decypharr_config_dir, decypharr_binary_file)

        if not os.path.exists(decypharr_config_dir):
            logger.debug(
                f"Creating Decypharr config directory at {decypharr_config_dir}"
            )
            os.makedirs(decypharr_config_dir, exist_ok=True)
            chown_recursive(decypharr_config_dir, user_id, group_id)

        if not os.path.isfile(binary_path):
            logger.warning(
                f"Decypharr project not found at {decypharr_config_dir}. Downloading..."
            )
            release, error = downloader.get_latest_release(
                repo_owner=config.get("repo_owner"),
                repo_name=config.get("repo_name"),
            )
            if not release:
                return False, f"Failed to get latest release: {error}"

            success, error = downloader.download_release_version(
                process_name=config.get("process_name"),
                key="decypharr",
                repo_owner=config.get("repo_owner"),
                repo_name=config.get("repo_name"),
                release_version=release,
                target_dir=decypharr_config_dir,
            )
            if not success:
                return False, f"Failed to download Decypharr: {error}"

            if os.path.isfile(binary_path):
                os.chmod(binary_path, 0o755)
                logger.debug(f"Marked {binary_path} as executable")

            versions.version_write(
                process_name=config.get("process_name"),
                key="decypharr",
                version_path=os.path.join(decypharr_config_dir, "version.txt"),
                version=release,
            )

        env_vars = {
            **config.get("env", {}),
        }
        config["env"] = env_vars

        if os.path.exists(decypharr_config_file):
            from utils.decypharr_settings import patch_decypharr_config

            patch_decypharr_config()

        logger.info("Decypharr setup complete.")
        return True, None
    except Exception as e:
        return False, f"Error during Decypharr setup: {e}"


def plex_debrid_setup():
    config = CONFIG_MANAGER.get("plex_debrid")
    if not config:
        return False, "Configuration for Plex Debrid not found."

    if not os.path.exists(config["config_file"]):
        logger.debug(
            f"Copying settings-default.json from {config['config_dir']} to {config['config_file']}"
        )
        shutil.copy(
            os.path.join(config["config_dir"], "settings-default.json"),
            config["config_file"],
        )
        chown_recursive(os.path.join(config["config_dir"], "config"), user_id, group_id)

    trakt_file = os.path.join(config["config_dir"], "content", "services", "trakt.py")
    if os.path.exists(trakt_file):
        with open(trakt_file, "r") as f:
            trakt_contents = f.read()

        updated_trakt_contents = re.sub(
            r'env_file\s*=\s*[\'"]\.env[\'"]',
            'env_file = "./config/.env"',
            trakt_contents,
        )

        with open(trakt_file, "w") as f:
            f.write(updated_trakt_contents)

        logger.debug("Updated env_file path in trakt.py to './config/.env'")
    return True, None


def dmb_frontend_setup():
    dmb_config = CONFIG_MANAGER.get("dmb")
    config = dmb_config.get("frontend")
    if not config:
        return False, "Configuration for DMB Frontend not found."
    api_config = dmb_config.get("api_service", {})
    if not api_config:
        return False, "Configuration for API Service not found."
    frontend_host = config.get("host", "127.0.0.1")
    frontend_port = str(config.get("port", 3005))
    api_host = api_config.get("host", "127.0.0.1")
    api_port = str(api_config.get("port", 8000))
    api_url = f"http://{api_host}:{api_port}"
    env_vars = {
        "HOST": frontend_host,
        "PORT": frontend_port,
        "DMB_API_URL": api_url,
        **config.get("env", {}),
    }
    config["env"] = env_vars
    return True, None


def phalanx_setup(process_handler):
    config = CONFIG_MANAGER.get("phalanx_db")
    if not config:
        return False, "Configuration for Phalanx not found."

    logger.info("Starting Phalanx setup...")

    try:
        phalanx_config_dir = config.get("config_dir")
        phalanx_data_dir = os.path.join(phalanx_config_dir, "data")
        original_js_file = os.path.join(phalanx_config_dir, "phalanx_db_rest.js")

        if not os.path.isfile(original_js_file):
            logger.warning(f"Phalanx project not found at {original_js_file}")
            success, error = setup_release_version(
                process_handler,
                config,
                process_name=config.get("process_name"),
                key="phalanx_db",
            )
            if not success:
                return False, f"Failed to download Phalanx: {error}"

        for subdir in ["db_data", "p2p-db-storage", "logs"]:
            target_path = os.path.join(phalanx_data_dir, subdir)
            symlink_path = os.path.join(phalanx_config_dir, subdir)

            os.makedirs(target_path, exist_ok=True)

            if os.path.islink(symlink_path):
                if not os.path.exists(os.readlink(symlink_path)):
                    logger.warning(
                        f"Broken symlink detected at {symlink_path}. Recreating..."
                    )
                    os.remove(symlink_path)
                    os.symlink(target_path, symlink_path)
            elif os.path.exists(symlink_path):
                logger.warning(
                    f"Expected symlink at {symlink_path}, but found real file/dir. Skipping."
                )
            else:
                os.symlink(target_path, symlink_path)

        logs_dir = os.path.join(phalanx_data_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        chown_recursive(
            phalanx_data_dir, CONFIG_MANAGER.get("puid"), CONFIG_MANAGER.get("pgid")
        )

        port = str(config.get("port", 8888))
        debug = (
            "true" if config.get("log_level", "debug").lower() == "debug" else "false"
        )
        env_vars = {
            "PORT": port,
            "DEBUG": debug,
            **config.get("env", {}),
        }
        config["env"] = env_vars

        logger.info("Phalanx setup complete.")
        return True, None

    except Exception as e:
        return False, f"Error during Phalanx setup: {e}"


def zurg_setup():
    config = CONFIG_MANAGER.get("zurg")
    if not config:
        return False, "Configuration for Zurg not found."

    logger.info("Starting Zurg setup...")

    try:

        def setup_zurg_instance(instance, key_type):
            try:
                instance_config_dir = instance["config_dir"]
                if not os.path.exists(instance_config_dir):
                    logger.debug(
                        f"Creating Zurg instance {instance} directory: {instance_config_dir}"
                    )
                    os.makedirs(instance_config_dir, exist_ok=True)
                    chown_recursive(
                        instance_config_dir,
                        CONFIG_MANAGER.get("puid"),
                        CONFIG_MANAGER.get("pgid"),
                    )
                instance_user = instance["user"]
                instance_password = instance["password"]
                instance_port = instance["port"]
                logger.debug(f"Initial port from config: {instance_port}")
                if not instance_port:
                    instance_port = random.randint(9001, 9999)
                    logger.debug(f"Assigned random port: {instance_port}")
                    instance["port"] = instance_port
                instance_zurg_binaries = os.path.join(instance_config_dir, "zurg")
                instance_config_file = os.path.join(instance_config_dir, "config.yml")
                instance_plex_update_file = os.path.join(
                    instance_config_dir, "plex_update.sh"
                )

                if os.path.exists("/config/zurg"):
                    logger.debug(
                        f"Copying Zurg binary from override to {instance_zurg_binaries}"
                    )
                    shutil.copy("/config/zurg", instance_zurg_binaries)
                    chown_recursive(
                        instance_zurg_binaries,
                        CONFIG_MANAGER.get("puid"),
                        CONFIG_MANAGER.get("pgid"),
                    )

                if os.path.exists("/config/config.yml"):
                    logger.debug(
                        f"Copying config.yml from override to {instance_config_file}"
                    )
                    shutil.copy("/config/config.yml", instance_config_file)
                    chown_recursive(
                        instance_config_file,
                        CONFIG_MANAGER.get("puid"),
                        CONFIG_MANAGER.get("pgid"),
                    )

                elif not os.path.exists(instance_config_file):
                    logger.debug(
                        f"Copying config.yml from base to {instance_config_file}"
                    )
                    shutil.copy("/zurg/config.yml", instance_config_file)
                    chown_recursive(
                        instance_config_file,
                        CONFIG_MANAGER.get("puid"),
                        CONFIG_MANAGER.get("pgid"),
                    )

                if not os.path.exists(instance_plex_update_file):
                    shutil.copy("/zurg/plex_update.sh", instance_plex_update_file)
                    chown_recursive(
                        instance_plex_update_file,
                        CONFIG_MANAGER.get("puid"),
                        CONFIG_MANAGER.get("pgid"),
                    )
                config_dir_stat = os.stat(instance_config_dir)
                if config_dir_stat.st_uid != CONFIG_MANAGER.get(
                    "puid"
                ) or config_dir_stat.st_gid != CONFIG_MANAGER.get("pgid"):
                    logger.debug(
                        f"Changing ownership of {instance_config_dir} to {CONFIG_MANAGER.get('puid')}:{CONFIG_MANAGER.get('pgid')}"
                    )
                    os.chown(
                        instance_config_dir,
                        CONFIG_MANAGER.get("puid"),
                        CONFIG_MANAGER.get("pgid"),
                    )

                update_port(instance_config_file, instance_port)

                token = instance["api_key"]
                if token:
                    update_token(instance_config_file, token)
                else:
                    return False, f"API key not found for Zurg instance {key_type}"

                update_creds(instance_config_file, instance_user, instance_password)

                logger.info(
                    f"Zurg instance '{key_type}' configured with port {instance_port}."
                )

                if not os.path.exists(instance_zurg_binaries):
                    if instance.get("release_version_enabled"):
                        release_version = instance.get("release_version")
                    else:
                        release_version = "latest"
                    success, error = downloader.download_release_version(
                        process_name=instance["process_name"],
                        key="zurg",
                        repo_owner=instance["repo_owner"],
                        repo_name=instance["repo_name"],
                        release_version=release_version,
                        target_dir=instance_config_dir,
                        zip_folder_name=None,
                        exclude_dirs=instance.get("exclude_dirs", []),
                    )
                    if not success:
                        return False, f"Failed to download Zurg: {error}"
                    downloader.set_permissions(instance_zurg_binaries, 0o755)

                logger.info(f"Zurg instance '{key_type}' setup complete.")
                return True, None

            except Exception as e:
                return False, f"Error setting up Zurg instance for {key_type}: {e}"

        for key_type, instance in config.get("instances", {}).items():
            if instance.get("enabled"):
                if not instance.get("api_key"):
                    raise ValueError(f"API key not found for Zurg instance {key_type}")
                logger.info(f"Setting up enabled instance: {key_type}")
                success, error = setup_zurg_instance(instance, key_type)
                if not success:
                    return False, error

        logger.info("All enabled Zurg instances have been set up.")
        return True, None

    except Exception as e:
        return False, f"Error during Zurg setup: {e}"


def update_port(config_file_path, instance_port):
    logger.debug(f"Updating port in {config_file_path} to {instance_port}")
    with open(config_file_path, "r") as file:
        lines = file.readlines()
    with open(config_file_path, "w") as file:
        for line in lines:
            if line.strip().startswith("port:") or line.strip().startswith("# port:"):
                file.write(f"port: {instance_port}\n")
            else:
                file.write(line)


def update_token(config_file_path, token):
    logger.debug(f"Updating token in {config_file_path}")
    with open(config_file_path, "r") as file:
        lines = file.readlines()
    with open(config_file_path, "w") as file:
        for line in lines:
            if line.strip().startswith("token:"):
                file.write(f"token: {token}\n")
            else:
                file.write(line)


def update_creds(config_file_path, username, password):
    if username and password:
        logger.debug(f"Updating credentials in {config_file_path}")
        with open(config_file_path, "r") as file:
            lines = file.readlines()
        with open(config_file_path, "w") as file:
            for line in lines:
                if line.strip().startswith("username:") or line.strip().startswith(
                    "# username:"
                ):
                    file.write(f"username: {username}\n")
                elif line.strip().startswith("password:") or line.strip().startswith(
                    "# password:"
                ):
                    file.write(f"password: {password}\n")
                else:
                    file.write(line)
    else:
        logger.debug(f"Removing credentials in {config_file_path}")
        with open(config_file_path, "r") as file:
            lines = file.readlines()
        with open(config_file_path, "w") as file:
            for line in lines:
                if line.strip().startswith("username:") or line.strip().startswith(
                    "# username:"
                ):
                    file.write("# username: <username>\n")
                elif line.strip().startswith("password:") or line.strip().startswith(
                    "# password:"
                ):
                    file.write("# password: <password>\n")
                else:
                    file.write(line)


def get_port_from_config(config_file_path):
    try:
        with open(config_file_path, "r") as file:
            for line in file:
                if line.strip().startswith("port:"):
                    port = line.split(":")[1].strip()
                    return port
    except Exception as e:
        logger.error(f"Error reading port from config file: {e}")
    return "9999"


def obscure_password(password):
    try:
        result = subprocess.run(
            ["rclone", "obscure", password], check=True, stdout=subprocess.PIPE
        )
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error obscuring password: {e}")
        return None


def is_mount_point(path):
    with open("/proc/mounts", "r") as mounts:
        for line in mounts:
            if path in line.split():
                return True
    return False


def ensure_directory(mount_dir, mount_name):
    full_path = os.path.join(mount_dir, mount_name)
    logger.debug(f"Ensuring directory {full_path} exists...")

    if is_mount_point(full_path):
        logger.info(f"{full_path} is a mount point. Attempting to unmount...")
        try:
            subprocess.run(["umount", full_path], check=True)
            logger.info(f"Successfully unmounted {full_path}.")
            return full_path, None
        except subprocess.CalledProcessError as e:
            return False, f"Failed to unmount {full_path}: {e.stderr}"

    if os.path.exists(full_path) and not os.path.isdir(full_path):
        return False, f"{full_path} exists but is not a directory."

    os.makedirs(full_path, exist_ok=True)
    logger.info(f"Directory {full_path} is ready.")
    return full_path, None


def rclone_setup():
    config = CONFIG_MANAGER.get("rclone")
    if not config:
        return False, "Configuration for Rclone not found."
    fuse_conf_path = "/etc/fuse.conf"
    user_allow_other_line = "user_allow_other"
    logger.info("Starting Rclone setup...")

    try:
        with open(fuse_conf_path, "r") as f:
            fuse_conf_content = f.readlines()

        updated_content = []
        line_found = False
        for line in fuse_conf_content:
            stripped_line = line.strip()
            if stripped_line == f"#{user_allow_other_line}":
                updated_content.append(f"{user_allow_other_line}\n")
                line_found = True
                logger.debug(
                    f"Uncommented '{user_allow_other_line}' in {fuse_conf_path}"
                )
            elif stripped_line == user_allow_other_line:
                line_found = True
                updated_content.append(line)
            else:
                updated_content.append(line)

        if not line_found:
            updated_content.append(f"{user_allow_other_line}\n")
            logger.debug(f"Added '{user_allow_other_line}' to {fuse_conf_path}")

        with open(fuse_conf_path, "w") as f:
            f.writelines(updated_content)

    except FileNotFoundError:
        with open(fuse_conf_path, "w") as f:
            f.write(f"{user_allow_other_line}\n")
        logger.debug(f"Created {fuse_conf_path} and added '{user_allow_other_line}'")

    except PermissionError:
        return False, "Permission denied while accessing /etc/fuse.conf."

    try:

        def setup_rclone_instance(instance_name, instance):
            if not instance.get("enabled", False):
                logger.debug(f"Skipping disabled Rclone instance: {instance_name}")
                return True, None

            config_file = instance["config_file"]
            config_dir = instance["config_dir"]
            mount_name = instance["mount_name"]
            mount_dir = instance["mount_dir"]

            os.makedirs(config_dir, exist_ok=True)
            logger.info(f"Setting up Rclone instance: {instance_name}")

            if instance.get("zurg_enabled", False) and instance.get(
                "decypharr_enabled", False
            ):
                return (
                    False,
                    "Both Zurg and Decypharr cannot be enabled at the same time for Rclone.",
                )

            elif instance.get("zurg_enabled", False) and not instance.get(
                "decypharr_enabled", False
            ):

                zurg_instance = (
                    CONFIG_MANAGER.get("zurg", {})
                    .get("instances", {})
                    .get(instance_name, {})
                )
                zurg_user = zurg_instance.get("user", "")
                zurg_password = zurg_instance.get("password", "")
                zurg_config_file = instance["zurg_config_file"]

                config_data = {}
                if os.path.exists(config_file):
                    with open(config_file, "r") as f:
                        lines = f.readlines()
                    section = None
                    for line in lines:
                        line = line.strip()
                        if line.startswith("[") and line.endswith("]"):
                            section = line[1:-1]
                            config_data[section] = []
                        elif section and line:
                            config_data[section].append(line)

                url = f"http://localhost:{get_port_from_config(zurg_config_file)}/dav/"

                config_data[mount_name] = [
                    "type = webdav",
                    f"url = {url}",
                    "vendor = other",
                    "pacer_min_sleep = 0",
                ]

                if zurg_user and zurg_password:
                    obscured_password = obscure_password(zurg_password)
                    if obscured_password:
                        config_data[mount_name].extend(
                            [
                                f"user = {zurg_user}",
                                f"pass = {obscured_password}",
                            ]
                        )
                    auth = {"user": zurg_user, "password": zurg_password}
                    instance["wait_for_url"] = [{"url": url, "auth": auth}]
                    # logger.debug(f"wait_for_url: {instance['wait_for_url']}")
                else:
                    instance["wait_for_url"] = [{"url": url}]
                    # logger.debug(f"wait_for_url: {instance['wait_for_url']}")

                with open(config_file, "w") as f:
                    for section, lines in config_data.items():
                        f.write(f"[{section}]\n")
                        f.write("\n".join(lines) + "\n")

            elif instance.get("decypharr_enabled", False) and not instance.get(
                "zurg_enabled", False
            ):
                decypharr_config = CONFIG_MANAGER.get("decypharr", {})
                url = None
                config_data = {}
                if instance.get("key_type").lower() == "realdebrid":
                    url = f"http://localhost:{decypharr_config.get('port', 8282)}/webdav/realdebrid"
                elif instance.get("key_type").lower() == "alldebrid":
                    url = f"http://localhost:{decypharr_config.get('port', 8282)}/webdav/alldebrid"
                elif instance.get("key_type").lower() == "debrid link":
                    url = f"http://localhost:{decypharr_config.get('port', 8282)}/webdav/debridlink"
                elif instance.get("key_type").lower() == "torbox":
                    url = f"http://localhost:{decypharr_config.get('port', 8282)}/webdav/torbox"

                config_data[mount_name] = [
                    "type = webdav",
                    f"url = {url}",
                    "vendor = other",
                    "pacer_min_sleep = 0",
                ]

                with open(config_file, "w") as f:
                    for section, lines in config_data.items():
                        f.write(f"[{section}]\n")
                        f.write("\n".join(lines) + "\n")

            elif not instance.get("zurg_enabled", False) and not instance.get(
                "decypharr_enabled", False
            ):
                config_data = {}
                if os.path.exists(config_file):
                    with open(config_file, "r") as f:
                        lines = f.readlines()
                    section = None
                    for line in lines:
                        line = line.strip()
                        if line.startswith("[") and line.endswith("]"):
                            section = line[1:-1]
                            config_data[section] = []
                        elif section and line:
                            config_data[section].append(line)

                if instance.get("key_type"):
                    key_type = instance["key_type"]
                    if key_type.lower() == "realdebrid":
                        obscured_password = obscure_password(instance["password"])
                        config_data[mount_name] = [
                            "type = webdav",
                            "url = https://dav.real-debrid.com/",
                            "vendor = other",
                            f"user = {instance['username']}",
                            f"pass = {obscured_password}",
                        ]
                    elif key_type.lower() == "alldebrid":
                        obscured_password = obscure_password("eeeee")
                        config_data[mount_name] = [
                            "type = webdav",
                            "url = https://webdav.debrid.it/",
                            "vendor = other",
                            f"user = {instance['api_key']}",
                            f"pass = {obscured_password}",
                        ]
                    elif key_type.lower() == "premiumize":
                        obscured_password = obscure_password(instance["api_key"])
                        config_data[mount_name] = [
                            "type = webdav",
                            "url = davs://webdav.premiumize.me",
                            "vendor = other",
                            f"user = {instance['customer_id']}",
                            f"pass = {obscured_password}",
                        ]
                    elif key_type.lower() == "torbox":
                        obscured_password = obscure_password(instance["password"])
                        config_data[mount_name] = [
                            "type = webdav",
                            "url = https://webdav.torbox.app",
                            "vendor = rclone",
                            f"user = {instance['username']}",
                            f"pass = {obscured_password}",
                            "pacer_min_sleep = 15s",
                        ]
                    elif key_type.lower() == "torbox-ftp":
                        obscured_password = obscure_password(instance["password"])
                        config_data[mount_name] = [
                            "type = ftp",
                            "host = ftp.torbox.app",
                            f"user = {instance['username']}",
                            f"pass = {obscured_password}",
                        ]

                with open(config_file, "w") as f:
                    for section, lines in config_data.items():
                        f.write(f"[{section}]\n")
                        f.write("\n".join(lines) + "\n")

            full_path, error = ensure_directory(mount_dir, mount_name)
            if error:
                return False, f"Failed to ensure mount directory: {error}"
            if os.path.exists(full_path):
                stat_info = os.stat(full_path)
                if stat_info.st_uid != user_id or stat_info.st_gid != group_id:
                    logger.debug(
                        f"Changing ownership of {full_path} to {user_id}:{group_id}"
                    )
                    os.chown(full_path, user_id, group_id)
                else:
                    logger.debug(f"Ownership of {full_path} is already correct.")
            os.makedirs(instance["cache_dir"], exist_ok=True)
            chown_recursive(instance["cache_dir"], user_id, group_id)

            def update_or_generate_command(instance):
                mount_name = instance["mount_name"]
                mount_dir = instance["mount_dir"]
                config_file = instance["config_file"]
                cache_dir = os.path.abspath(instance["cache_dir"])
                log_file = os.path.abspath(instance["log_file"])
                log_level = instance.get("log_level", "INFO").upper()

                base_cmd = [
                    "rclone",
                    "mount",
                    f"{mount_name}:",
                    f"{mount_dir}/{mount_name}",
                ]

                required_flags = {
                    "--config": config_file,
                    "--uid": str(user_id),
                    "--gid": str(group_id),
                    "--allow-other": None,
                    "--poll-interval": "0",
                    "--dir-cache-time": "10s",
                    "--allow-non-empty": None,
                    "--cache-dir": cache_dir,
                    "--log-file": log_file,
                    "--log-level": log_level,
                }

                if instance.get("decypharr_enabled", False):
                    required_flags.update(
                        {
                            "--rc": None,
                            "--rc-addr": ":5572",
                            "--rc-no-auth": None,
                        }
                    )

                existing = instance.get("command", [])
                parsed_flags = {}

                i = 0
                while i < len(existing):
                    item = existing[i]
                    if item.startswith("--"):
                        if "=" in item:
                            flag, val = item.split("=", 1)
                            parsed_flags[flag] = val
                        elif i + 1 < len(existing) and not existing[i + 1].startswith(
                            "--"
                        ):
                            parsed_flags[item] = existing[i + 1]
                            i += 1
                        else:
                            parsed_flags[item] = None
                    i += 1

                for key, value in required_flags.items():
                    parsed_flags[key] = value

                space_style = {"--rc-addr"}
                final_cmd = base_cmd
                for key, value in parsed_flags.items():
                    if value is None:
                        final_cmd.append(key)
                    elif key in space_style:
                        final_cmd.extend([key, value])
                    else:
                        final_cmd.append(f"{key}={value}")

                instance["command"] = final_cmd
                logger.debug(
                    f"Final rclone command for {instance['mount_name']}: {final_cmd}"
                )

            update_or_generate_command(instance)

            from utils.riven_settings import parse_config_keys

            parse_config_keys(CONFIG_MANAGER.config)

            logger.info(f"Rclone instance '{instance_name}' has been set up.")
            return True, None

        for instance_name, instance in config.get("instances", {}).items():
            success, error = setup_rclone_instance(instance_name, instance)
            if not success:
                return False, error

        logger.info("All Rclone instances have been set up.")
        return True, None

    except Exception as e:
        return False, f"Error during Rclone setup: {e}"


def setup_environment(process_handler, key, platforms, config_dir):
    try:
        logger.info(
            f"Setting up environment for {key} in {config_dir} with {platforms}"
        )

        if "python" in platforms:
            success, error = setup_python_environment(process_handler, key, config_dir)
            if not success:
                return False, error

        if "pnpm" in platforms:
            success, error = setup_pnpm_environment(process_handler, config_dir)
            if not success:
                return False, error

        if "dotnet" in platforms:
            success, error = setup_dotnet_environment(
                process_handler,
                key,
                config_dir,
            )
            if not success:
                return False, error

        logger.info(f"Environment setup complete")
        return True, None
    except Exception as e:
        return False, f"Environment setup failed: {e}"


def clear_directory(directory_path, exclude_dirs=None, retries=3, delay=2):

    if exclude_dirs is None:
        exclude_dirs = []

    venv_path = os.path.abspath(os.path.join(directory_path, "venv"))
    if os.path.exists(venv_path) and not any(
        os.path.abspath(ex) == venv_path for ex in exclude_dirs
    ):
        logger.debug(f"Adding venv path to exclude_dirs: {venv_path}")
        exclude_dirs.append(venv_path)

    exclude_dirs = {os.path.abspath(exclude_dir) for exclude_dir in exclude_dirs}
    directory_path = os.path.abspath(directory_path)
    logger.debug(f"Excluding directories: {exclude_dirs}")

    def should_exclude(path):
        path = os.path.abspath(path)
        return any(
            path == exclude or path.startswith(f"{exclude}{os.sep}")
            for exclude in exclude_dirs
        )

    def clear_contents(path):
        for item in os.listdir(path):
            item_path = os.path.abspath(os.path.join(path, item))
            if should_exclude(item_path):
                logger.debug(f"Skipping excluded path: {item_path}")
                continue
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    clear_contents(item_path)
                    os.rmdir(item_path)
            except OSError as e:
                raise

    if not os.path.exists(directory_path):
        return False, f"Directory {directory_path} does not exist"

    try:
        logger.debug(f"Clearing directory: {directory_path}")
        clear_contents(directory_path)
        return True, None
    except OSError as e:
        if e.errno == 39:
            return True, None
        else:
            return False, f"Failed to clear directory {directory_path}: {e}"


def copy_server_config(source, destination):
    try:
        if not os.path.exists(source):
            logger.debug(f"server.json not found at {source}, skipping copy.")
            return

        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copy2(source, destination)
        logger.info(f"Copied server configuration to {destination}")
    except Exception as e:
        logger.error(f"Error copying server configuration: {e}")


def setup_python_environment(process_handler, key, config_dir):
    try:

        requirements_file = (
            os.path.join(config_dir, "requirements.txt")
            if os.path.exists(os.path.join(config_dir, "requirements.txt"))
            else None
        )

        if key == "cli_debrid":
            requirements_file = (
                os.path.join(config_dir, "requirements-linux.txt")
                if os.path.exists(os.path.join(config_dir, "requirements-linux.txt"))
                else None
            )

        poetry_install = True if key == "riven_backend" else False

        logger.info(f"Setting up Python environment in {config_dir}")

        venv_path = os.path.join(config_dir, "venv")

        process_handler.start_process(
            "python_env_setup", config_dir, ["python", "-m", "venv", "venv"]
        )
        process_handler.wait("python_env_setup")

        if process_handler.returncode != 0:
            return (
                False,
                f"Error creating Python virtual environment: {process_handler.stderr}",
            )
        logger.debug(f"venv_path: {venv_path} for {key}")
        python_executable = os.path.abspath(f"{venv_path}/bin/python")
        poetry_executable = os.path.abspath(f"{venv_path}/bin/poetry")
        pip_executable = os.path.abspath(f"{venv_path}/bin/pip")

        if requirements_file is not None:
            install_cmd = f"{pip_executable} install -r {requirements_file}"
            logger.debug(f"Installing requirements from {requirements_file} for {key}")
            process_handler.start_process(
                "install_requirements", config_dir, ["/bin/bash", "-c", install_cmd]
            )
            process_handler.wait("install_requirements")

            if process_handler.returncode != 0:
                return False, f"Error installing requirements: {process_handler.stderr}"

            logger.info(f"Installed requirements from {requirements_file}")

        if poetry_install is True:
            logger.debug(f"Installing Poetry for {key}")
            env = os.environ.copy()
            env["PATH"] = f"{venv_path}/bin:" + env["PATH"]
            env["POETRY_VIRTUALENVS_CREATE"] = "false"
            env["VIRTUAL_ENV"] = venv_path

            process_handler.start_process(
                "install_poetry",
                config_dir,
                [python_executable, "-m", "pip", "install", "poetry"],
                None,
                False,
                env=env,
            )
            process_handler.wait("install_poetry")

            if process_handler.returncode != 0:
                return False, f"Error installing Poetry: {process_handler.stderr}"

            process_handler.start_process(
                "poetry_install",
                config_dir,
                [poetry_executable, "install", "--no-root", "--without", "dev"],
                None,
                False,
                env=env,
            )
            process_handler.wait("poetry_install")

            if process_handler.returncode != 0:
                return False, f"Error installing dependencies with Poetry"

            logger.info(f"Poetry environment setup complete at {venv_path}")

        logger.info(f"Python environment setup complete")
        return True, None

    except Exception as e:
        return False, f"Error during Python environment setup: {e}"


def setup_dotnet_environment(process_handler, key, config_dir):
    try:
        logger.info(f"Setting up .NET environment in {config_dir}")
        process_handler.start_process(
            "dotnet_env_restore", config_dir, ["dotnet", "restore", "/nodeReuse:false"]
        )
        process_handler.wait("dotnet_env_restore")
        if process_handler.returncode != 0:
            return False, f"Error running dotnet restore: {process_handler.stderr}"
        project_paths = []
        if key == "zilean":
            project_paths = [
                os.path.join(config_dir, "src/Zilean.ApiService"),
                os.path.join(config_dir, "src/Zilean.Scraper"),
            ]
        for project_path in project_paths:
            if os.path.exists(project_path):
                logger.info(f"Publishing .NET project {project_path}")
                output_path = os.path.join(config_dir, "app")
                process_handler.start_process(
                    "dotnet_publish",
                    config_dir,
                    [
                        "dotnet",
                        "publish",
                        project_path,
                        "-c",
                        "Release",
                        "--no-restore",
                        "-o",
                        output_path,
                        "/nodeReuse:false",
                        "/p:UseSharedCompilation=false",
                    ],
                )
                process_handler.wait("dotnet_publish")
                if process_handler.returncode != 0:
                    return (
                        False,
                        f"Error publishing .NET project {project_path}: {process_handler.stderr}",
                    )

        logger.info(f".NET environment setup complete")
        return True, None

    except Exception as e:
        return False, f"Error during .NET environment setup: {e}"


def vite_modifications(config_dir):
    try:
        vite_config_path = os.path.join(config_dir, "vite.config.ts")
        with open(vite_config_path, "r") as file:
            lines = file.readlines()
        build_section_exists = any("build:" in line for line in lines)
        if not build_section_exists:
            for i, line in enumerate(lines):
                if line.strip().startswith("export default defineConfig({"):
                    lines.insert(i + 1, "    build: {\n        minify: false\n    },\n")
                    break
        with open(vite_config_path, "w") as file:
            file.writelines(lines)
        logger.debug("vite.config.ts modified to disable minification")
        about_page_path = os.path.join(
            config_dir, "src", "routes", "settings", "about", "+page.server.ts"
        )
        with open(about_page_path, "r") as file:
            about_page_lines = file.readlines()
        for i, line in enumerate(about_page_lines):
            if "versionFilePath: string = '/riven/version.txt';" in line:
                about_page_lines[i] = line.replace(
                    "/riven/version.txt", "/riven/frontend/version.txt"
                )
                logger.debug(
                    f"Modified versionFilePath in +page.ts to point to /riven/frontend/version.txt"
                )
                break
        with open(about_page_path, "w") as file:
            file.writelines(about_page_lines)
        return True, None

    except Exception as e:
        return False, f"Error modifying vite.config.ts: {e}"


def setup_pnpm_environment(process_handler, config_dir):
    try:
        with open(os.path.join(config_dir, ".npmrc"), "w") as file:
            file.write("store-dir=./.pnpm-store\n")

        logger.info(f"Setting up pnpm environment in {config_dir}")
        for attempt in range(3):
            process_handler.start_process(
                "pnpm_install", config_dir, ["pnpm", "install"]
            )
            process_handler.wait("pnpm_install")
            if process_handler.returncode == 0:
                break
            if "eagain" not in (process_handler.stdout or "").lower():
                return False, f"Error during pnpm install: {process_handler.stderr}"
            logger.warning("pnpm install hit EAGAIN. Retrying...")
        else:
            return False, f"Error during pnpm install: {process_handler.stderr}"

        package_json_path = os.path.join(config_dir, "package.json")
        build_script_exists = False
        if os.path.isfile(package_json_path):
            import json

            with open(package_json_path, "r") as f:
                package_data = json.load(f)
                scripts = package_data.get("scripts", {})
                build_script_exists = "build" in scripts

        if build_script_exists:
            logger.info(f"Build script found. Running pnpm build...")
            process_handler.start_process(
                "pnpm_build", config_dir, ["pnpm", "run", "build"]
            )
            process_handler.wait("pnpm_build")
            if process_handler.returncode != 0:
                return False, f"Error during pnpm build: {process_handler.stderr}"
        else:
            logger.info(f"No build script found. Skipping pnpm build step.")

        logger.info(f"pnpm environment setup complete")
        return True, None

    except Exception as e:
        return False, f"Error during pnpm setup: {e}"


def setup_traefik(process_handler):
    """Configures and starts Traefik using ProcessHandler"""

    traefik_config = CONFIG_MANAGER.get("traefik")
    if not traefik_config or not traefik_config.get("enabled"):
        logger.info("Traefik is disabled. Skipping setup.")
        return True, None

    config_dir = traefik_config.get("config_dir", "/config/traefik")

    # Ensure config directory exists
    os.makedirs(config_dir, exist_ok=True)

    logger.info(f"Setting up Traefik configuration in {config_dir}")

    # Generate traefik.yml (static configuration)
    static_config = {
        "entryPoints": traefik_config.get("entrypoints", {}),
        "api": {"dashboard": True},
        "providers": {"file": {"directory": config_dir, "watch": True}},
    }

    static_config_path = os.path.join(config_dir, "traefik.yml")
    with open(static_config_path, "w") as file:
        yaml.dump(static_config, file, default_flow_style=False)

    logger.info(f"Generated Traefik static config: {static_config_path}")

    # Generate dynamic configuration for services
    dynamic_config = {"http": {"routers": {}, "services": {}, "middlewares": {}}}

    # Add middleware definitions
    if "middlewares" in traefik_config:
        dynamic_config["http"]["middlewares"] = traefik_config["middlewares"]

    # Add services and routers
    for service_name, service_info in traefik_config.get("services", {}).items():
        router_name = f"{service_name}_router"
        service_url = service_info.get("url")
        middlewares = service_info.get("middlewares", [])

        if not service_url:
            logger.warning(f"Skipping {service_name}, no URL defined")
            continue

        dynamic_config["http"]["services"][service_name] = {
            "loadBalancer": {"servers": [{"url": service_url}]}
        }

        dynamic_config["http"]["routers"][router_name] = {
            "rule": f"PathPrefix(`/{service_name}`)",
            "service": service_name,
            "entryPoints": ["web"],
            "middlewares": middlewares,
        }

    dynamic_config_path = os.path.join(config_dir, "dynamic_config.yml")
    with open(dynamic_config_path, "w") as file:
        yaml.dump(dynamic_config, file, default_flow_style=False)

    logger.info(f"Generated Traefik dynamic config: {dynamic_config_path}")

    return True, None


def start_traefik(process_handler, config_dir: str):
    """Ensures Traefik is running via ProcessHandler"""

    traefik_bin = "/usr/local/bin/traefik"  # Adjust path if needed

    # Check if Traefik is already running
    if process_handler.is_process_running("traefik"):
        logger.info("Traefik is already running, restarting it.")
        process_handler.stop_process("traefik")

    # Start Traefik with config directory
    process_handler.start_process(
        process_name="traefik",
        cmd=[traefik_bin, "--configFile", os.path.join(config_dir, "traefik.yml")],
        env={},
    )

    logger.info("Traefik has been started successfully.")
