from utils.config_loader import CONFIG_MANAGER as config
from utils.global_logger import logger, websocket_manager
from utils import duplicate_cleanup, user_management
from api.api_service import start_fastapi_process
from utils.processes import ProcessHandler
from utils.auto_update import Update
from utils.dependencies import initialize_dependencies
import subprocess, threading, time
from time import sleep


def main():

    with open("version.txt", "r") as file:
        version = file.read().strip()

    ascii_art = f"""
                                                                       
DDDDDDDDDDDDD        MMMMMMMM               MMMMMMMMBBBBBBBBBBBBBBBBB   
D::::::::::::DDD     M:::::::M             M:::::::MB::::::::::::::::B  
D:::::::::::::::DD   M::::::::M           M::::::::MB::::::BBBBBB:::::B 
DDD:::::DDDDD:::::D  M:::::::::M         M:::::::::MBB:::::B     B:::::B
  D:::::D    D:::::D M::::::::::M       M::::::::::M  B::::B     B:::::B
  D:::::D     D:::::DM:::::::::::M     M:::::::::::M  B::::B     B:::::B
  D:::::D     D:::::DM:::::::M::::M   M::::M:::::::M  B::::BBBBBB:::::B 
  D:::::D     D:::::DM::::::M M::::M M::::M M::::::M  B:::::::::::::BB  
  D:::::D     D:::::DM::::::M  M::::M::::M  M::::::M  B::::BBBBBB:::::B 
  D:::::D     D:::::DM::::::M   M:::::::M   M::::::M  B::::B     B:::::B
  D:::::D     D:::::DM::::::M    M:::::M    M::::::M  B::::B     B:::::B
  D:::::D    D:::::D M::::::M     MMMMM     M::::::M  B::::B     B:::::B
DDD:::::DDDDD:::::D  M::::::M               M::::::MBB:::::BBBBBB::::::B
D:::::::::::::::DD   M::::::M               M::::::MB:::::::::::::::::B 
D::::::::::::DDD     M::::::M               M::::::MB::::::::::::::::B  
DDDDDDDDDDDDD        MMMMMMMM               MMMMMMMMBBBBBBBBBBBBBBBBB   
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                              Version: {version}                                    
"""

    logger.info(ascii_art.format(version=version) + "\n" + "\n")

    process_handler = ProcessHandler(logger)
    updater = Update(process_handler)
    initialize_dependencies(
        process_handler=process_handler,
        updater=updater,
        websocket_manager=websocket_manager,
        logger=logger,
    )

    if config.get("dmb", {}).get("api_service", {}).get("enabled"):
        start_fastapi_process()

    try:
        user_management.create_system_user()
    except Exception as e:
        logger.error(f"An error occurred while creating system user: {e}")
        process_handler.shutdown(exit_code=1)

    try:
        dmb_config = config.get("dmb", {})
        frontend_config = dmb_config.get("frontend", {})
        process_name = frontend_config.get("process_name")
        api_config = dmb_config.get("api_service", {})
        if frontend_config.get("enabled") and api_config.get("enabled"):
            if frontend_config.get("auto_update", False):
                updater.auto_update(process_name, True)
            else:
                updater.auto_update(process_name, False)
        else:
            logger.info(f"{process_name} is disabled. Skipping process start.")
    except Exception as e:
        logger.error(f"An error occurred in the DMB Frontend setup: {e}")
        process_handler.shutdown(exit_code=1)

    try:
        key = "zurg"
        zurg_instances = config.get(key, {}).get("instances", {})
        enabled_zurg_instances = [
            name for name, instance in zurg_instances.items() if instance.get("enabled")
        ]

        if not enabled_zurg_instances:
            logger.info("No Zurg instances are enabled. Skipping Zurg setup.")
        else:
            for instance_name in enabled_zurg_instances:
                instance = zurg_instances[instance_name]
                process_name = instance.get("process_name")
                if instance.get("auto_update"):
                    updater.auto_update(process_name, True)
                else:
                    updater.auto_update(process_name, False)
    except Exception:
        process_handler.shutdown(exit_code=1)

    try:
        key = "rclone"
        duplicate_cleanup_enabled = config.get("dmb", {}).get("duplicate_cleanup")
        rclone_instances = config.get(key, {}).get("instances", {})
        enabled_rclone_instances = [
            name
            for name, instance in rclone_instances.items()
            if instance.get("enabled")
        ]

        if not enabled_rclone_instances:
            logger.info("No rclone instances are enabled. Skipping rclone setup.")
        else:
            for instance_name in enabled_rclone_instances:
                instance_config = rclone_instances[instance_name]

                if mount_name := instance_config.get("mount_name"):
                    logger.info(
                        f"Configuring rclone for instance: {instance_name} with mount name: {mount_name}"
                    )
                    try:
                        # if duplicate_cleanup_enabled:
                        #     logger.info(
                        #         f"Duplicate cleanup is enabled for instance: {instance_name}"
                        #     )
                        #     duplicate_cleanup.setup()

                        process_name = instance_config.get("process_name")
                        updater.auto_update(process_name, False)
                    except Exception as e:
                        logger.error(
                            f"Error during rclone setup for instance {instance_name}: {e}"
                        )
                        raise
                else:
                    raise ValueError(
                        f"No mount name found for rclone instance: {instance_name}"
                    )
    except Exception as e:
        logger.error(f"An error occurred in the rclone setup process: {e}")
        process_handler.shutdown(exit_code=1)

    try:
        postgres_config = config.get("postgres", {})
        pgadmin_config = config.get("pgadmin", {})
        riven_backend_config = config.get("riven_backend", {})
        riven_frontend_config = config.get("riven_frontend", {})
        zilean_config = config.get("zilean", {})

        if postgres_config.get("enabled"):
            try:
                process_name = postgres_config.get("process_name")
                updater.auto_update(process_name, False)
            except Exception as e:
                logger.error(f"An error occurred in the PostgreSQL setup: {e}")
                process_handler.shutdown(exit_code=1)

        if pgadmin_config.get("enabled"):
            try:
                process_name = pgadmin_config.get("process_name")
                updater.auto_update(process_name, False)
            except Exception as e:
                logger.error(f"An error occurred in the pgAdmin setup: {e}")
                process_handler.shutdown(exit_code=1)

        if zilean_config.get("enabled"):
            try:
                process_name = zilean_config.get("process_name")
                if zilean_config.get("auto_update", False):
                    updater.auto_update(process_name, True)
                else:
                    updater.auto_update(process_name, False)
            except Exception as e:
                logger.error(f"An error occurred in the Zilean setup: {e}")
                process_handler.shutdown(exit_code=1)

        sleep(10)

        if riven_backend_config.get("enabled"):
            try:
                process_name = riven_backend_config.get("process_name")
                if riven_backend_config.get("auto_update", False):
                    updater.auto_update(process_name, True)
                else:
                    updater.auto_update(process_name, False)
            except Exception as e:
                logger.error(f"An error occurred in the Riven Backend setup: {e}")
                process_handler.shutdown(exit_code=1)

        if riven_frontend_config.get("enabled"):
            try:
                process_name = riven_frontend_config.get("process_name")
                if riven_frontend_config.get("auto_update", False):
                    updater.auto_update(process_name, True)
                else:
                    updater.auto_update(process_name, False)
            except Exception as e:
                logger.error(f"An error occurred in the Riven Frontend setup: {e}")
                process_handler.shutdown(exit_code=1)

    except Exception as e:
        logger.error(f"An error occurred in the setup process: {e}")
        process_handler.shutdown(exit_code=1)

    def healthcheck():
        time.sleep(60)
        while True:
            time.sleep(10)
            try:
                result = subprocess.run(
                    ["python", "healthcheck.py"], capture_output=True, text=True
                )
                if result.stderr:
                    logger.error(result.stderr.strip())
            except Exception as e:
                logger.error("Error running healthcheck.py: %s", e)
            time.sleep(50)

    thread = threading.Thread(target=healthcheck, daemon=True)
    thread.start()

    def perpetual_wait():
        stop_event = threading.Event()
        stop_event.wait()

    perpetual_wait()


if __name__ == "__main__":
    main()
