from base import *
from utils.global_logger import logger, websocket_manager
from riven_.update import RivenUpdate
from zilean_.update import ZileanUpdate
from zurg.update import ZurgUpdate
from utils import duplicate_cleanup, user_management, postgres, api_service
from utils.logger import MissingAPIKeyException
from utils.processes import ProcessHandler


def main():

    version = "5.4.5"

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
    logger.debug(f"Initialized ProcessHandler: {process_handler}")

    riven_updater = RivenUpdate(process_handler)
    zilean_updater = ZileanUpdate(process_handler)
    zurg_updater = ZurgUpdate(process_handler)
    logger.debug(f"Initialized ZurgUpdate: {zurg_updater}")
    logger.debug(f"Initialized ZileanUpdate: {zilean_updater}")
    logger.debug(f"Initialized RivenUpdate: {riven_updater}")

    api_service.start_fastapi_process(
        process_handler=process_handler,
        process_name="fastapi_server",
        config_dir=".",
        riven_updater=riven_updater,
        zilean_updater=zilean_updater,
        zurg_updater=zurg_updater,
        websocket_manager=websocket_manager,
        logger=logger,
    )

    command = "node .output/server/index.mjs"
    env_vars = {"PORT": "3005"}
    process = process_handler.start_process(
        process_name="dmb_frontend",
        config_dir="/dmb/frontend",
        command=command,
        key_type=None,
        suppress_logging=False,
        env=env_vars,
    )
    if process is not None:
        logger.info("dmb_frontend process started successfully.")
    else:
        logger.error("Failed to start the dmb_frontend process.")

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

    thread = threading.Thread(target=healthcheck)
    thread.daemon = True
    thread.start()

    try:
        user_management.create_system_user()
    except Exception as e:
        logger.error(f"An error occurred while creating system user: {e}")
        process_handler.shutdown(exit_code=1)

    try:
        if ZURG is None or str(ZURG).lower() == "false":
            pass
        elif str(ZURG).lower() == "true":
            try:
                if RDAPIKEY or ADAPIKEY:
                    try:
                        from zurg.setup import zurg_setup

                        zurg_setup(process_handler)
                    except Exception as e:
                        raise e
                    if (
                        ZURGUPDATE
                        and ZURGUPDATE.lower() == "true"
                        and (ZURGVERSION is None or ZURGVERSION.lower() == "nightly")
                    ):
                        zurg_updater.auto_update("Zurg", True)
                    else:
                        zurg_updater.auto_update("Zurg", False)
                    try:
                        if RCLONEMN:
                            try:
                                if not DUPECLEAN:
                                    pass
                                elif DUPECLEAN:
                                    duplicate_cleanup.setup()
                                from rclone import rclone

                                rclone.setup(process_handler)
                            except Exception as e:
                                logger.error(e)
                    except Exception as e:
                        raise Exception(f"An error occurred in the rclone setup: {e}")
                else:
                    raise MissingAPIKeyException()
            except Exception as e:
                logger.error(f"An error occurred in the Zurg setup: {e}")
                process_handler.shutdown(exit_code=1)
    except Exception as e:
        logger.error(e)
        process_handler.shutdown(exit_code=1)

    try:
        if (RIVENBACKEND is not None and str(RIVENBACKEND).lower() == "true") or (
            RIVEN is not None and str(RIVEN).lower() == "true"
        ):
            try:
                postgres.postgres_setup(process_handler)
            except Exception as e:
                logger.error(f"An error occurred in the PostgreSQL setup: {e}")
                process_handler.shutdown(exit_code=1)
            try:
                if ZILEAN is not None and str(ZILEAN).lower() == "true":
                    try:
                        from zilean_.setup import zilean_setup

                        zilean_setup(process_handler, "Zilean")
                    except Exception as e:
                        raise e
                    if (
                        ZILEANUPDATE
                        and ZILEANUPDATE.lower() == "true"
                        and not ZILEANVERSION
                    ):
                        zilean_updater.auto_update("Zilean", True)
                    else:
                        zilean_updater.auto_update("Zilean", False)
            except Exception as e:
                logger.error(f"An error occurred in the Zilean setup: {e}")
                process_handler.shutdown(exit_code=1)
            try:
                try:
                    from riven_.setup import riven_setup

                    riven_setup(process_handler, "riven_backend")
                except Exception as e:
                    raise e
                if (RBUPDATE or RUPDATE) and not RBVERSION:
                    riven_updater.auto_update("riven_backend", True)
                else:
                    riven_updater.auto_update("riven_backend", False)
            except Exception as e:
                logger.error(f"An error occurred in the Riven backend setup: {e}")
                process_handler.shutdown(exit_code=1)
    except Exception as e:
        logger.error(e)
        process_handler.shutdown(exit_code=1)

    try:
        if (RIVENFRONTEND is not None and str(RIVENFRONTEND).lower() == "true") or (
            RIVEN is not None and str(RIVEN).lower() == "true"
        ):
            try:
                from riven_.setup import riven_setup

                riven_setup(process_handler, "riven_frontend", RFBRANCH, RFVERSION)
            except Exception as e:
                raise e
            if (RFUPDATE or RUPDATE) and not RFVERSION:
                riven_updater.auto_update("riven_frontend", True)
            else:
                riven_updater.auto_update("riven_frontend", False)
    except Exception as e:
        logger.error(f"An error occurred in the Riven frontend setup: {e}")
        process_handler.shutdown(exit_code=1)

    def perpetual_wait():
        stop_event = threading.Event()
        stop_event.wait()

    perpetual_wait()


if __name__ == "__main__":
    main()
