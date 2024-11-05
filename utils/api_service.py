from base import *
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class APIState:
    def __init__(self, riven_update, zilean_update, zurg_update, logger):
        self.riven_update = riven_update
        self.zilean_update = zilean_update
        self.zurg_update = zurg_update
        self.logger = logger
        self.service_status = {
            "riven_frontend": "stopped",
            "riven_backend": "stopped",
            "Zilean": "stopped",
            "Zurg": "stopped",
        }

    def set_status(self, process_name, status):
        if process_name in self.service_status:
            self.logger.info(f"Setting status for {process_name}: {status}")
            self.service_status[process_name] = status

    def get_status(self, process_name):
        return self.service_status.get(process_name, "unknown")

    def debug_state(self):
        self.logger.info("Current APIState:")
        self.logger.info(f"  riven_update: {self.riven_update}")
        self.logger.info(f"  zilean_update: {self.zilean_update}")
        self.logger.info(f"  zurg_update: {self.zurg_update}")
        self.logger.info(f"  service_status: {self.service_status}")


def create_app(riven_updater, zilean_updater, zurg_updater, logger):
    api_state = APIState(riven_updater, zilean_updater, zurg_updater, logger)
    app = FastAPI()

    origin_from_env = os.getenv("ORIGIN")

    origins = [origin_from_env] if origin_from_env else ["http://localhost", "http://localhost:8000"]

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
        return FileResponse("static/index.html")

    def get_api_state():
        return api_state

    class ServiceRequest(BaseModel):
        process_name: str

    @app.post("/stop-service")
    async def stop_service(request: ServiceRequest, api_state: APIState = Depends(get_api_state)):
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
            api_state.logger.error(f"Process not found: {process_name}")
            raise HTTPException(status_code=404, detail="Process not found")

        try:
            api_state.logger.info(f"Initiating shutdown for {process_name}")
            update_handler.stop_process(process_name)
            api_state.set_status(process_name, "stopped")
        except Exception as e:
            api_state.logger.error(f"Failed to stop {process_name}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to stop {process_name}: {str(e)}")

        return {"status": "Service stopped successfully", "process_name": process_name}

    @app.post("/start-service")
    async def start_service(request: ServiceRequest, api_state: APIState = Depends(get_api_state)):
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
            api_state.logger.info(f"Starting {process_name} process")
            update_handler.start_process(process_name, config_dir=directory)
            api_state.set_status(process_name, "running")
        except Exception as e:
            api_state.logger.error(f"Failed to start {process_name}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to start {process_name}: {str(e)}")

        return {"status": "Service started successfully", "process_name": process_name}

    @app.post("/restart-service")
    async def restart_service(request: ServiceRequest, api_state: APIState = Depends(get_api_state)):
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
            raise HTTPException(status_code=500, detail=f"Failed to restart {process_name}: {str(e)}")

        return {"status": "Service restarted successfully", "process_name": process_name}

    @app.get("/service-status/{process_name}")
    async def service_status(process_name: str, api_state: APIState = Depends(get_api_state)):
        status = api_state.get_status(process_name)
        if status == "unknown":
            api_state.logger.error(f"Service not found: {process_name}")
            raise HTTPException(status_code=404, detail="Service not found")
        return {"process_name": process_name, "status": status}

    return app
