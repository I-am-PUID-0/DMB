from base import *
from utils.logger import *
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class APIState:
    def __init__(
        self, riven_update, zilean_update, zurg_update, process_handler, logger
    ):
        self.riven_update = riven_update
        self.zilean_update = zilean_update
        self.zurg_update = zurg_update
        self.process_handler = process_handler
        self.logger = logger
        self.service_status = {
            "riven_frontend": "stopped",
            "riven_backend": "stopped",
            "Zilean": "stopped",
            "Zurg": "stopped",
        }
        self.shutdown_in_progress = set()
        self.status_file_path = "/healthcheck/health_status.json"
        os.makedirs(os.path.dirname(self.status_file_path), exist_ok=True)
        self.write_status_to_file()
        self.logger.info("APIState initialized with all services stopped.")

    def set_status(self, process_name, status):
        if process_name in self.service_status:
            self.logger.info(f"Setting status for {process_name}: {status}")
            self.service_status[process_name] = status
            self.write_status_to_file()

    def get_status(self, process_name):
        self.logger.debug(f"Retrieving status for {process_name}")
        if self.poll_update_status(process_name):
            self.service_status[process_name] = "running"
            self.logger.info(f"{process_name} is currently running.")
        else:
            self.service_status[process_name] = "stopped"
            self.logger.info(f"{process_name} is currently stopped.")
        return self.service_status.get(process_name, "unknown")

    def poll_update_status(self, process_name):
        process = self.process_handler.process_names.get(process_name)
        if process is None:
            self.logger.warning(
                f"Process {process_name} not found, setting status as unknown."
            )
            return False
        is_running = process.poll() is None
        self.logger.debug(
            f"Poll result for {process_name}: {'running' if is_running else 'stopped'}"
        )
        return is_running

    def write_status_to_file(self):
        try:
            with open(self.status_file_path, "w") as f:
                dump(self.service_status, f)
            self.logger.debug("Health status file updated successfully.")
        except Exception as e:
            self.logger.error(f"Failed to write health status file: {e}")

    def debug_state(self):
        self.logger.info("Current APIState:")
        self.logger.info(f"  riven_update: {self.riven_update}")
        self.logger.info(f"  zilean_update: {self.zilean_update}")
        self.logger.info(f"  zurg_update: {self.zurg_update}")
        self.logger.info(f"  service_status: {self.service_status}")


def create_app(riven_updater, zilean_updater, zurg_updater, process_handler, logger):
    api_state = APIState(
        riven_updater, zilean_updater, zurg_updater, process_handler, logger
    )
    app = FastAPI()

    origin_from_env = os.getenv("ORIGIN")
    logger.debug(f"ORIGIN environment variable set to: {origin_from_env}")

    origins = (
        [origin_from_env]
        if origin_from_env
        else ["http://localhost", "http://localhost:8000"]
    )
    logger.info(f"Allowed CORS origins set to: {origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/")
    async def serve_homepage():
        logger.info("Serving homepage /static/index.html")
        return FileResponse("static/index.html")

    @app.get("/health")
    async def health_check():
        try:
            result = subprocess.run(
                ["sh", "-c", "source /venv/bin/activate && python /healthcheck.py"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                error_output = result.stderr.strip()
                return {"status": "unhealthy", "details": error_output}
            return {"status": "healthy"}

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to run health check: {str(e)}"
            )

    def get_api_state():
        logger.debug("Retrieving APIState dependency.")
        return api_state

    class ServiceRequest(BaseModel):
        process_name: str

    @app.post("/stop-service")
    async def stop_service(
        request: ServiceRequest, api_state: APIState = Depends(get_api_state)
    ):
        logger.info(
            f"Received stop-service request for {request.process_name}, Request ID: {id(request)}"
        )
        api_state.debug_state()

        process_name = request.process_name
        process_map = {
            "riven_frontend": api_state.riven_update,
            "riven_backend": api_state.riven_update,
            "Zilean": api_state.zilean_update,
            "Zurg": api_state.zurg_update,
        }

        update_handler = process_map.get(process_name)

        if update_handler is None:
            logger.error(f"Process not found: {process_name}")
            raise HTTPException(status_code=404, detail="Process not found")

        if process_name in api_state.shutdown_in_progress:
            logger.info(f"Shutdown for {process_name} is already in progress.")
            return {
                "status": "Shutdown already in progress",
                "process_name": process_name,
            }

        try:
            api_state.shutdown_in_progress.add(process_name)
            logger.info(f"Initiating shutdown for {process_name}")
            update_handler.stop_process(process_name)
            api_state.set_status(process_name, "stopped")
            logger.info(f"{process_name} stopped successfully.")
        except Exception as e:
            logger.error(f"Failed to stop {process_name}: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to stop {process_name}: {str(e)}"
            )
        finally:
            api_state.shutdown_in_progress.remove(process_name)

        return {"status": "Service stopped successfully", "process_name": process_name}

    @app.post("/start-service")
    async def start_service(
        request: ServiceRequest, api_state: APIState = Depends(get_api_state)
    ):
        logger.info(f"Received start-service request for {request.process_name}")
        api_state.debug_state()

        process_name = request.process_name
        process_map = {
            "riven_frontend": (api_state.riven_update, "/riven/frontend"),
            "riven_backend": (api_state.riven_update, "/riven/backend"),
            "Zilean": (api_state.zilean_update, "/zilean/app"),
            "Zurg": (api_state.zurg_update, "/zurg/RD"),
        }

        update_handler, directory = process_map.get(process_name, (None, None))

        if update_handler is None:
            logger.error(f"Process not found: {process_name}")
            raise HTTPException(status_code=404, detail="Process not found")

        try:
            logger.info(f"Starting {process_name} process in directory {directory}")
            update_handler.start_process(process_name, config_dir=directory)
            api_state.set_status(process_name, "running")
            logger.info(f"{process_name} started successfully.")
        except Exception as e:
            logger.error(f"Failed to start {process_name}: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to start {process_name}: {str(e)}"
            )

        return {"status": "Service started successfully", "process_name": process_name}

    @app.post("/restart-service")
    async def restart_service(
        request: ServiceRequest, api_state: APIState = Depends(get_api_state)
    ):
        api_state.debug_state()
        process_name = request.process_name
        process_map = {
            "riven_frontend": (api_state.riven_update, "/riven/frontend"),
            "riven_backend": (api_state.riven_update, "/riven/backend"),
            "Zilean": (api_state.zilean_update, "/zilean/app"),
            "Zurg": (api_state.zurg_update, "/zurg/RD"),
        }
        update_handler, directory = process_map.get(process_name, (None, None))
        if update_handler is None:
            api_state.logger.error(f"Process not found: {process_name}")
            raise HTTPException(status_code=404, detail="Process not found")

        try:
            api_state.logger.info(f"Initiating shutdown for {process_name}")
            update_handler.stop_process(process_name)
            api_state.set_status(process_name, "stopped")
            api_state.logger.info(f"Starting {process_name} process")
            update_handler.start_process(process_name, config_dir=directory)
            api_state.set_status(process_name, "running")
        except Exception as e:
            api_state.logger.error(f"Failed to restart {process_name}: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to restart {process_name}: {str(e)}"
            )

        return {
            "status": "Service restarted successfully",
            "process_name": process_name,
        }

    @app.get("/service-status/{process_name}")
    async def service_status(
        process_name: str, api_state: APIState = Depends(get_api_state)
    ):
        logger.info(f"Checking status for {process_name}")
        status = api_state.get_status(process_name)
        if status == "unknown":
            logger.error(f"Service not found: {process_name}")
            raise HTTPException(status_code=404, detail="Service not found")
        logger.info(f"Status for {process_name}: {status}")
        return {"process_name": process_name, "status": status}

    return app
