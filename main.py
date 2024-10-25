from os import wait
from base import *
from utils.logger import *
import riven_ as r
import zurg as z
import zilean_ as zilean
from rclone import rclone
from utils import duplicate_cleanup, user_management, postgres
from utils.processes import ProcessHandler

logger = get_logger()
process_handler = ProcessHandler(logger)


def main():

    version = "5.4.0"

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
                        z.setup.zurg_setup(process_handler)
                    except Exception as e:
                        raise e
                    z_updater = z.update.ZurgUpdate(process_handler)
                    logger.debug(f"Initialized ZurgUpdate: {z_updater}")
                    if (
                        ZURGUPDATE
                        and ZURGUPDATE.lower() == "true"
                        and (ZURGVERSION is None or ZURGVERSION.lower() == "nightly")
                    ):
                        z_updater.auto_update("Zurg", True)
                    else:
                        z_updater.auto_update("Zurg", False)
                    try:
                        if RCLONEMN:
                            try:
                                if not DUPECLEAN:
                                    pass
                                elif DUPECLEAN:
                                    duplicate_cleanup.setup()
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
                        zilean.setup.zilean_setup(process_handler, "Zilean")
                    except Exception as e:
                        raise e
                    zilean_updater = zilean.update.ZileanUpdate(process_handler)
                    logger.debug(f"Initialized ZileanUpdate: {zilean_updater}")
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
                    r.setup.riven_setup(process_handler, "riven_backend")
                except Exception as e:
                    raise e
                r_updater = r.update.RivenUpdate(process_handler)
                logger.debug(f"Initialized RivenUpdate: {r_updater}")
                if (RBUPDATE or RUPDATE) and not RBVERSION:
                    r_updater.auto_update("riven_backend", True)
                else:
                    r_updater.auto_update("riven_backend", False)
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
                r.setup.riven_setup(
                    process_handler, "riven_frontend", RFBRANCH, RFVERSION
                )
            except Exception as e:
                raise e
            r_updater = r.update.RivenUpdate(process_handler)
            logger.debug(f"Initialized RivenUpdate: {r_updater}")
            if (RFUPDATE or RUPDATE) and not RFVERSION:
                r_updater.auto_update("riven_frontend", True)
            else:
                r_updater.auto_update("riven_frontend", False)
    except Exception as e:
        logger.error(f"An error occurred in the Riven frontend setup: {e}")
        process_handler.shutdown(exit_code=1)

    def perpetual_wait():
        stop_event = threading.Event()
        stop_event.wait()

    perpetual_wait()


if __name__ == "__main__":
    main()
