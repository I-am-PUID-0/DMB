from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from utils.dependencies import (
    get_process_handler,
    get_logger,
    get_api_state,
    get_updater,
)
from utils.config_loader import CONFIG_MANAGER, find_service_config
from utils.setup import setup_project
from utils.versions import Versions


class ServiceRequest(BaseModel):
    process_name: str


process_router = APIRouter()
versions = Versions()

STATIC_URLS_BY_KEY = {
    "rclone": "https://rclone.org",
    "pgadmin": "https://www.pgadmin.org/",
    "postgres": "https://www.postgresql.org/",
    "dmb_api_service": "https://github.com/I-am-PUID-0/DMB",
    "cli_battery": "https://github.com/godver3/cli_debrid/tree/main/cli_battery",
}


@process_router.get("/")
async def fetch_process(process_name: str = Query(...), logger=Depends(get_logger)):
    try:
        if not process_name:
            raise HTTPException(status_code=400, detail="process_name is required")

        config = find_service_config(CONFIG_MANAGER.config, process_name)
        if not config:
            raise HTTPException(status_code=404, detail="Process not found")

        config_key, instance_name = CONFIG_MANAGER.find_key_for_process(process_name)
        version, _ = versions.version_check(
            process_name=config.get("process_name"),
            instance_name=instance_name,
            key=config_key,
        )

        return {
            "process_name": process_name,
            "config": config,
            "version": version,
            "config_key": config_key,
        }
    except Exception as e:
        logger.error(f"Failed to load process: {e}")
        raise HTTPException(status_code=500, detail="Failed to load process")


@process_router.get("/processes")
async def fetch_processes():
    logger = (Depends(get_logger),)
    try:
        processes = []
        config = CONFIG_MANAGER.config

        def find_processes(data, parent_key=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict) and "process_name" in value:
                        process_name = value.get("process_name")
                        enabled = value.get("enabled", False)
                        display_name = f"{parent_key} {key}".strip()
                        config_key, instance_name = CONFIG_MANAGER.find_key_for_process(
                            process_name
                        )
                        version, _ = versions.version_check(
                            process_name=value.get("process_name"),
                            instance_name=instance_name,
                            key=config_key,
                        )
                        repo_owner = value.get("repo_owner")
                        repo_name = value.get("repo_name")
                        if repo_owner and repo_name:
                            repo_url = f"https://github.com/{repo_owner}/{repo_name}"
                        else:
                            repo_url = STATIC_URLS_BY_KEY.get(config_key)
                        processes.append(
                            {
                                "name": display_name,
                                "process_name": process_name,
                                "enabled": enabled,
                                "config": value,
                                "version": version,
                                "key": key,
                                "config_key": config_key,
                                "repo_url": repo_url,
                            }
                        )
                    elif isinstance(value, dict):
                        find_processes(value, parent_key=f"{parent_key} {key}".strip())

        find_processes(config)
        return {"processes": processes}
    except Exception as e:
        logger.error(f"Failed to load processes: {e}")
        raise HTTPException(status_code=500, detail="Failed to load processes")


@process_router.post("/start-service")
async def start_service(
    request: ServiceRequest,
    process_handler=Depends(get_process_handler),
    updater=Depends(get_updater),
    logger=Depends(get_logger),
):
    process_name = request.process_name
    service_config = find_service_config(CONFIG_MANAGER.config, process_name)

    if not service_config:
        raise HTTPException(status_code=404, detail="Service not enabled or found")

    if process_name in process_handler.setup_tracker:
        process_handler.setup_tracker.remove(process_name)
        success, error = setup_project(process_handler, process_name)
        if not success:
            raise HTTPException(
                status_code=500, detail=f"Failed to setup project: {error}"
            )

    service_config["enabled"] = True
    command = service_config.get("command")
    if any("{" in c for c in command):
        success, error = setup_project(process_handler, process_name)
        if not success:
            raise HTTPException(
                status_code=500, detail=f"Failed to setup project: {error}"
            )
        command = service_config.get("command")

    env = service_config.get("env")
    if env is not None:
        logger.debug(f"Checking for variables in service config. {env}")
        if any("{" in c for c in env):
            success, error = setup_project(process_handler, process_name)
            if not success:
                raise HTTPException(
                    status_code=500, detail=f"Failed to setup project: {error}"
                )
            env = service_config.get("env")

    config_dir = service_config.get("config_dir")
    suppress_logging = service_config.get("suppress_logging", False)
    logger.info(f"Starting {process_name} with command: {command}")

    try:
        auto_update_enabled = service_config.get("auto_update", False)
        process, error = updater.auto_update(
            process_name, enable_update=auto_update_enabled
        )
        if not process:
            raise Exception(f"Error starting {process_name}: {error}")
        elif process:
            logger.info(f"{process_name} started successfully.")
            return {
                "status": "Service started successfully",
                "process_name": process_name,
            }
    except Exception as e:
        detailed_error = f"Service '{process_name}' could not be started due to an internal error: {str(e)}"
        logger.error(detailed_error)
        raise HTTPException(
            status_code=500,
            detail=f"Unable to start the service '{process_name}'. Please check the logs for more details.",
        )


@process_router.post("/stop-service")
async def stop_service(
    request: ServiceRequest,
    process_handler=Depends(get_process_handler),
    logger=Depends(get_logger),
    api_state=Depends(get_api_state),
):
    process_name = request.process_name
    logger.info(f"Received request to stop {process_name}")

    # Check if the service exists and is enabled
    # service_config = CONFIG_MANAGER.config.get(process_name)
    # logger.debug(f"Service config: {service_config}")
    # if not service_config or not service_config.get("enabled", False):
    #    raise HTTPException(status_code=404, detail="Service not enabled or found")

    if process_name in api_state.shutdown_in_progress:
        return {
            "status": "Shutdown already in progress",
            "process_name": process_name,
        }

    try:
        api_state.shutdown_in_progress.add(process_name)
        logger.debug(f"Shutdown in progress: {api_state.shutdown_in_progress}")
        process_handler.stop_process(process_name)
        logger.info(f"{process_name} stopped successfully.")
        return {
            "status": "Service stopped successfully",
            "process_name": process_name,
        }
    except Exception as e:
        logger.error(f"Failed to stop {process_name}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to stop {process_name}: {str(e)}"
        )
    finally:
        api_state.shutdown_in_progress.remove(process_name)


@process_router.post("/restart-service")
async def restart_service(
    request: ServiceRequest,
    process_handler=Depends(get_process_handler),
    updater=Depends(get_updater),
    logger=Depends(get_logger),
    api_state=Depends(get_api_state),
):
    process_name = request.process_name
    logger.info(f"Received request to restart {process_name}")

    try:
        process_handler.stop_process(process_name)
        logger.info(f"{process_name} stopped successfully.")

        service_config = find_service_config(CONFIG_MANAGER.config, process_name)
        if not service_config:
            raise HTTPException(
                status_code=404, detail="Service configuration not found."
            )

        if process_name in process_handler.setup_tracker:
            process_handler.setup_tracker.remove(process_name)
            success, error = setup_project(process_handler, process_name)
            if not success:
                raise HTTPException(
                    status_code=500, detail=f"Failed to setup project: {error}"
                )

        auto_update_enabled = service_config.get("auto_update", False)
        process, error = updater.auto_update(
            process_name, enable_update=auto_update_enabled
        )
        if not process:
            raise HTTPException(status_code=500, detail=f"Failed to restart: {error}")

        logger.info(f"{process_name} started successfully.")

        status = api_state.get_status(process_name)
        if status != "running":
            raise HTTPException(
                status_code=500,
                detail=f"Service did not restart successfully. Current status: {status}",
            )

        return {
            "status": "Service restarted successfully",
            "process_name": process_name,
        }
    except Exception as e:
        logger.error(f"Failed to restart {process_name}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to restart {process_name}: {str(e)}"
        )


@process_router.get("/service-status")
async def service_status(
    process_name: str = Query(..., description="The name of the process to check"),
    api_state=Depends(get_api_state),
):
    status = api_state.get_status(process_name)
    return {"process_name": process_name, "status": status}
