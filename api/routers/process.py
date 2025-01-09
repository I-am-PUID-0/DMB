from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from utils.dependencies import get_process_handler, get_logger, get_api_state
from utils.config_loader import CONFIG_MANAGER, find_service_config


class ServiceRequest(BaseModel):
    process_name: str


process_router = APIRouter()


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
                        processes.append(
                            {
                                "name": f"{parent_key} {key}".strip(),
                                "process_name": value.get("process_name"),
                                "enabled": value.get("enabled", False),
                                "config": value,
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
    logger=Depends(get_logger),
):
    process_name = request.process_name
    service_config = find_service_config(CONFIG_MANAGER.config, process_name)

    if not service_config:
        raise HTTPException(status_code=404, detail="Service not enabled or found")

    service_config["enabled"] = True
    command = service_config.get("command")
    config_dir = service_config.get("config_dir")
    suppress_logging = service_config.get("suppress_logging", False)
    logger.info(f"Starting {process_name} with command: {command}")

    try:
        process = process_handler.start_process(
            process_name=process_name,
            config_dir=config_dir,
            command=command,
            instance_name=None,
            suppress_logging=suppress_logging,
            env=service_config.get("env"),
        )
        if process:
            logger.info(f"{process_name} started successfully.")
            return {
                "status": "Service started successfully",
                "process_name": process_name,
            }
        else:
            raise Exception("Process failed to start.")
    except Exception as e:
        logger.error(f"Failed to start {process_name}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start {process_name}: {str(e)}"
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

        process_handler.start_process(
            process_name=process_name,
            config_dir=service_config.get("config_dir"),
            command=service_config.get("command"),
            suppress_logging=service_config.get("suppress_logging", False),
            env=service_config.get("env"),
        )
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
