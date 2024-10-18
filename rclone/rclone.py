from base import *
from utils.logger import *


logger = get_logger()


def get_port_from_config(config_file_path, key_type):
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
    """Obscure the password using rclone."""
    try:
        result = subprocess.run(
            ["rclone", "obscure", password], check=True, stdout=subprocess.PIPE
        )
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error obscuring password: {e}")
        return None


def wait_for_url(url, endpoint="/dav/", timeout=600):
    time.sleep(5)
    start_time = time.time()
    logger.info(
        f"Waiting to start the rclone process until the Zurg WebDAV {url}{endpoint} is accessible."
    )
    auth = None
    if "ZURGUSER" in globals() and "ZURGPASS" in globals() and ZURGUSER and ZURGPASS:
        auth = (ZURGUSER, ZURGPASS)

    while time.time() - start_time < timeout:
        try:
            if auth:
                response = requests.get(f"{url}{endpoint}", auth=auth)
            else:
                response = requests.get(f"{url}{endpoint}")

            if 200 <= response.status_code < 300:
                logger.debug(
                    f"Zurg WebDAV {url}{endpoint} is accessible with status code {response.status_code}."
                )
                return True
            else:
                logger.debug(
                    f"Received status code {response.status_code} while waiting for {url}{endpoint} to be accessible."
                )
        except requests.ConnectionError as e:
            logger.debug(
                f"Connection error while waiting for the Zurg WebDAV {url}{endpoint} to be accessible: {e}"
            )
        time.sleep(5)

    logger.error(
        f"Timeout: Zurg WebDAV {url}{endpoint} is not accessible after {timeout} seconds."
    )
    return False


def setup(process_handler=None):
    logger.info("Checking rclone flags")

    try:
        if not RCLONEMN:
            raise Exception("Please set a name for the rclone mount")
        logger.info(f'Configuring the rclone mount name to "{RCLONEMN}"')

        if not RDAPIKEY and not ADAPIKEY:
            raise Exception("Please set the API Key for the rclone mount")

        if RDAPIKEY and ADAPIKEY:
            RCLONEMN_RD = f"{RCLONEMN}_RD"
            RCLONEMN_AD = f"{RCLONEMN}_AD"
        else:
            RCLONEMN_RD = RCLONEMN_AD = RCLONEMN

        config_file_path_rd = "/zurg/RD/config.yml"
        config_file_path_ad = "/zurg/AD/config.yml"

        with open("/config/rclone.config", "w") as f:
            if RDAPIKEY:
                rd_port = get_port_from_config(config_file_path_rd, "RDAPIKEY")
                f.write(f"[{RCLONEMN_RD}]\n")
                f.write("type = webdav\n")
                f.write(f"url = http://localhost:{rd_port}/dav\n")
                f.write("vendor = other\n")
                f.write("pacer_min_sleep = 0\n")
                if ZURGUSER and ZURGPASS:
                    obscured_password = obscure_password(ZURGPASS)
                    if obscured_password:
                        f.write(f"user = {ZURGUSER}\n")
                        f.write(f"pass = {obscured_password}\n")

            if ADAPIKEY:
                ad_port = get_port_from_config(config_file_path_ad, "ADAPIKEY")
                f.write(f"[{RCLONEMN_AD}]\n")
                f.write("type = webdav\n")
                f.write(f"url = http://localhost:{ad_port}/dav\n")
                f.write("vendor = other\n")
                f.write("pacer_min_sleep = 0\n")
                if ZURGUSER and ZURGPASS:
                    obscured_password = obscure_password(ZURGPASS)
                    if obscured_password:
                        f.write(f"user = {ZURGUSER}\n")
                        f.write(f"pass = {obscured_password}\n")

        with open("/etc/fuse.conf", "a") as f:
            f.write("user_allow_other\n")

        mount_names = []
        if RDAPIKEY:
            os.chown(config_file_path_rd, user_id, group_id)
            mount_names.append(RCLONEMN_RD)
        if ADAPIKEY:
            os.chown(config_file_path_ad, user_id, group_id)
            mount_names.append(RCLONEMN_AD)

        for idx, mn in enumerate(mount_names):
            logger.info(f"Configuring rclone for {mn}")
            subprocess.run(
                ["umount", f"{RCLONEDIR}/{mn}"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            os.makedirs(f"{RCLONEDIR}/{mn}", exist_ok=True)
            if NFSMOUNT is not None and NFSMOUNT.lower() == "true":
                if NFSPORT:
                    port = NFSPORT
                    logger.info(
                        f"Setting up rclone NFS mount server for {mn} at 0.0.0.0:{port}"
                    )
                    rclone_command = [
                        "rclone",
                        "serve",
                        "nfs",
                        f"{mn}:",
                        "--config",
                        "/config/rclone.config",
                        "--addr",
                        f"0.0.0.0:{port}",
                        "--vfs-cache-mode=full",
                        "--dir-cache-time=10",
                    ]
                else:
                    port = random.randint(8001, 8999)
                    logger.info(
                        f"Setting up rclone NFS mount server for {mn} at 0.0.0.0:{port}"
                    )
                    rclone_command = [
                        "rclone",
                        "serve",
                        "nfs",
                        f"{mn}:",
                        "--config",
                        "/config/rclone.config",
                        "--addr",
                        f"0.0.0.0:{port}",
                        "--vfs-cache-mode=full",
                        "--dir-cache-time=10",
                    ]
            else:
                rclone_command = [
                    "rclone",
                    "mount",
                    f"{mn}:",
                    f"{RCLONEDIR}/{mn}",
                    "--config",
                    "/config/rclone.config",
                    f"--uid={user_id}",
                    f"--gid={group_id}",
                    "--allow-other",
                    "--poll-interval=0",
                    "--dir-cache-time=10",
                ]
            if not RIVENBACKEND or idx != len(mount_names) - 1:
                rclone_command.append("--daemon")

            url = f"http://localhost:{rd_port if mn == RCLONEMN_RD else ad_port}"
            if os.path.exists(f"/healthcheck/{mn}"):
                os.rmdir(f"/healthcheck/{mn}")
            if wait_for_url(url):
                os.makedirs(
                    f"/healthcheck/{mn}"
                )  # makedir for healthcheck. Don't like it, but it works for now...
                logger.info(
                    f"The Zurg WebDAV URL {url}/dav is accessible. Starting rclone{' daemon' if '--daemon' in rclone_command else ''} for {mn}"
                )
                process_name = "rclone"
                suppress_logging = False
                if str(RCLONELOGS).lower() == "off":
                    suppress_logging = True
                    logger.info(f"Suppressing {process_name} logging")
                rclone_process = process_handler.start_process(
                    process_name,
                    "/config",
                    rclone_command,
                    mn,
                    suppress_logging=suppress_logging,
                )
            else:
                logger.error(
                    f"The Zurg WebDav URL {url}/dav is not accessible within the timeout period. Skipping rclone setup for {mn}"
                )

        logger.info("rclone startup complete")

    except Exception as e:
        logger.error(e)
        exit(1)
