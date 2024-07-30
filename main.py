from base import *
from utils.logger import *
import riven_ as r
import zurg as z 
from rclone import rclone
from utils import duplicate_cleanup


def shutdown(signum, frame):
    logger = get_logger()
    logger.info("Shutdown signal received. Cleaning up...")

    for mount_point in os.listdir('/data'):
        full_path = os.path.join('/data', mount_point)
        if os.path.ismount(full_path):
            logger.info(f"Unmounting {full_path}...")
            umount = subprocess.run(['umount', full_path], capture_output=True, text=True)
            if umount.returncode == 0:
                logger.info(f"Successfully unmounted {full_path}")
            else:
                logger.error(f"Failed to unmount {full_path}: {umount.stderr.strip()}")
    
    sys.exit(0)

def main():
    logger = get_logger()

    version = '3.2.0'

    ascii_art = f'''
                                                                       
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
'''

    logger.info(ascii_art.format(version=version)  + "\n" + "\n")

    def healthcheck():
        time.sleep(60)
        while True:
            time.sleep(10)
            try:
                result = subprocess.run(['python', 'healthcheck.py'], capture_output=True, text=True) 
                if result.stderr:
                    logger.error(result.stderr.strip())
            except Exception as e:
                logger.error('Error running healthcheck.py: %s', e)
            time.sleep(50)
    thread = threading.Thread(target=healthcheck)
    thread.daemon = True
    thread.start()
       
    try:
        if ZURG is None or str(ZURG).lower() == 'false':
            pass
        elif str(ZURG).lower() == 'true':
            try:
                if RDAPIKEY or ADAPIKEY:
                    try:
                        z.setup.zurg_setup() 
                        z_updater = z.update.ZurgUpdate()
                        if ZURGUPDATE and not ZURGVERSION:
                            z_updater.auto_update('Zurg',True)
                        else:
                            z_updater.auto_update('Zurg',False)
                    except Exception as e:
                        raise Exception(f"Error in Zurg setup: {e}")
                    try:    
                        if RCLONEMN:
                            try:
                                if not DUPECLEAN:
                                    pass
                                elif DUPECLEAN:
                                    duplicate_cleanup.setup()
                                rclone.setup()      
                            except Exception as e:
                                logger.error(e)                         
                    except Exception as e:
                        raise Exception(f"Error in setup: {e}")                          
                else:
                    raise MissingAPIKeyException()
            except Exception as e:
                logger.error(e)                    
    except Exception as e:
        logger.error(e)
        
    try:
        if (RIVENBACKEND is not None and str(RIVENBACKEND).lower() == 'true') or (RIVEN is not None and str(RIVEN).lower() == 'true'):
            try:
                r.setup.riven_setup('Riven_backend')
                r_updater = r.update.RivenUpdate()
                if RBUPDATE or RUPDATE:
                    r_updater.auto_update('Riven_backend', True)                                        
                else:
                    r_updater.auto_update('Riven_backend', False)              
            except Exception as e:
                logger.error(f"An error occurred in the Riven backend setup: {e}")
    except:
        pass

    try:
        if (RIVENFRONTEND is not None and str(RIVENFRONTEND).lower() == 'true') or (RIVEN is not None and str(RIVEN).lower() == 'true'):
            try:
                r.setup.riven_setup('Riven_frontend', RFBRANCH, RFVERSION)
                r_updater = r.update.RivenUpdate()
                if RFUPDATE or RUPDATE:       
                    r_updater.auto_update('Riven_frontend', True)
                else:
                    r_updater.auto_update('Riven_frontend', False)                    
            except Exception as e:
                logger.error(f"An error occurred in the Riven frontend setup: {e}")
    except:
        pass
   
    
    def perpetual_wait():
        stop_event = threading.Event()
        stop_event.wait()
    perpetual_wait()    
if __name__ == "__main__":
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    
    main()