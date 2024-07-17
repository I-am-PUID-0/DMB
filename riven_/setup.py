from base import *
from utils.logger import *


logger = get_logger()

def r_setup():
    logger.info("Configuring Riven")
    riven_dir = "./riven"
    frontend_dir = os.path.join(riven_dir, "frontend")    
    if not os.path.exists(frontend_dir):
        from .download import get_latest_release
        success, error = get_latest_release()
        if not success:
            logger.error(f"Failed to download the latest release: {error}")
            raise Exception(f"Failed to download the latest release: {error}")
    try:
        # Frontend setup
        logger.info("Setting up Riven frontend")
        result = subprocess.run(["npm", "install"], cwd=frontend_dir, check=True, capture_output=True, text=True)
        logger.debug(f"npm install output: {result.stdout}")
        logger.debug(f"npm install errors: {result.stderr}")
        
        result = subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True, capture_output=True, text=True)
        logger.debug(f"npm run build output: {result.stdout}")
        logger.debug(f"npm run build errors: {result.stderr}")
        logger.info("Riven frontend setup complete")
        
        # Backend setup
        logger.info("Setting up Riven backend")
        result = subprocess.run(["poetry", "install", "--without", "dev"], cwd=riven_dir, check=True, capture_output=True, text=True)
        logger.debug(f"poetry install output: {result.stdout}")
        logger.debug(f"poetry install errors: {result.stderr}")
        logger.info("Riven backend setup complete")
        logger.info("Riven configuration complete")
    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess error: {e.returncode}, {e.output}")
        raise
    except FileNotFoundError as e:
        logger.error(f"File not found error: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise
    
if __name__ == "__main__":
    r_setup()
