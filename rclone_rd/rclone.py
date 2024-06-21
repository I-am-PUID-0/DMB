from base import *

logger = get_logger()

def get_port_from_config(config_file_path, key_type):
    try:
        with open(config_file_path, 'r') as file:
            for line in file:
                if line.strip().startswith("port:"):
                    port = line.split(':')[1].strip()
                    return port
    except Exception as e:
        logger.error(f"Error reading port from config file: {e}")
    return '9999'  

def obscure_password(password):
    """Obscure the password using rclone."""
    try:
        result = subprocess.run(["rclone", "obscure", password], check=True, stdout=subprocess.PIPE)
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        print("Error obscuring password:", e)
        return None

def setup():
    logger.info("Checking rclone flags")
 
    try:
        if not RCLONEMN:
            raise Exception("Please set a name for the rclone mount")
        logger.info(f"Configuring the rclone mount name to \"{RCLONEMN}\"")

        if not RDAPIKEY and not ADAPIKEY:
            raise Exception("Please set the API Key for the rclone mount")

        if RDAPIKEY and ADAPIKEY:
            RCLONEMN_RD = f"{RCLONEMN}_RD"
            RCLONEMN_AD = f"{RCLONEMN}_AD"
        else:
            RCLONEMN_RD = RCLONEMN_AD = RCLONEMN

        config_file_path_rd = '/zurg/RD/config.yml'
        config_file_path_ad = '/zurg/AD/config.yml'

        with open("/config/rclone.config", "w") as f:
            if RDAPIKEY:
                rd_port = get_port_from_config(config_file_path_rd, 'RDAPIKEY')
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
                ad_port = get_port_from_config(config_file_path_ad, 'ADAPIKEY')
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
            mount_names.append(RCLONEMN_RD)
        if ADAPIKEY:
            mount_names.append(RCLONEMN_AD)

        subprocesses = []

        for idx, mn in enumerate(mount_names):
            logger.info(f"Configuring rclone for {mn}")
            subprocess.run(["umount", f"/data/{mn}"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.makedirs(f"/data/{mn}", exist_ok=True)
            if NFSMOUNT is not None and NFSMOUNT.lower() == "true":
                if NFSPORT:
                    port = NFSPORT                    
                    logger.info(f"Setting up rclone NFS mount server for {mn} at 0.0.0.0:{port}")
                    rclone_command = ["rclone", "serve", "nfs", f"{mn}:", "--config", "/config/rclone.config", "--addr", f"0.0.0.0:{port}", "--vfs-cache-mode=full", "--dir-cache-time=10"]
                else: 
                    port = random.randint(8001, 8999)                    
                    logger.info(f"Setting up rclone NFS mount server for {mn} at 0.0.0.0:{port}")
                    rclone_command = ["rclone", "serve", "nfs", f"{mn}:", "--config", "/config/rclone.config", "--addr", f"0.0.0.0:{port}", "--vfs-cache-mode=full", "--dir-cache-time=10"]                    
            else:
                rclone_command = ["rclone", "mount", f"{mn}:", f"/data/{mn}", "--config", "/config/rclone.config", "--allow-other", "--poll-interval=0", "--dir-cache-time=10"]
            if not PLEXDEBRID or idx != len(mount_names) - 1:
                rclone_command.append("--daemon")
    
            logger.info(f"Starting rclone{' daemon' if '--daemon' in rclone_command else ''} for {mn}")
            process_name = "rclone"
            subprocess_logger = SubprocessLogger(logger, process_name)
            process = subprocess.Popen(rclone_command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            subprocess_logger.start_monitoring_stderr(process, mn, process_name)

        logger.info("rclone startup complete")

    except Exception as e:
        logger.error(e)
        exit(1)