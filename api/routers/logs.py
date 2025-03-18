from fastapi import APIRouter, Depends, Query
from pathlib import Path
from utils.dependencies import get_logger
from utils.config_loader import CONFIG_MANAGER
import os, re

logs_router = APIRouter()


def find_log_file(process_name: str, logger):
    logger.debug(f"Looking up process: {process_name}")

    if "dmb" in process_name.lower():
        log_dir = Path("/log")
        if log_dir.exists():
            log_files = sorted(
                log_dir.glob("DMB-*.log"), key=os.path.getmtime, reverse=True
            )
            return log_files[0] if log_files else None

    key, instance_name = CONFIG_MANAGER.find_key_for_process(process_name)
    logger.debug(f"Found key: {key}, instance: {instance_name}")
    if not key:
        logger.debug(f"No log file found for {process_name}")
        return None

    service_config = CONFIG_MANAGER.get_instance(instance_name, key)
    if not service_config:
        logger.debug(f"No service config found for {process_name}")
        return None

    if "log_file" in service_config:
        return Path(service_config["log_file"])

    if "config_file" in service_config:
        log_dir = Path(service_config["config_file"]).parent / "logs"
        if log_dir.exists():
            log_files = sorted(
                log_dir.glob("*.log"), key=os.path.getmtime, reverse=True
            )
            return log_files[0] if log_files else None

    if "config_dir" in service_config:
        log_dir = Path(service_config["config_dir"]) / "logs"
        if log_dir.exists():
            log_files = sorted(
                log_dir.glob("*.log"), key=os.path.getmtime, reverse=True
            )
            return log_files[0] if log_files else None

    if "zurg" in process_name.lower() and "config_dir" in service_config:
        log_path = Path(service_config["config_dir"]) / "logs" / "zurg.log"
        if log_path.exists():
            return log_path

    logger.debug(f"No log file found for {process_name}")
    return None


def filter_dmb_log(log_path, logger):
    logger.debug(f"Filtering DMB log for latest startup from {log_path}")
    try:
        with open(log_path, "r") as log_file:
            lines = log_file.readlines()

        for i in range(len(lines) - 2, -1, -1):
            if re.match(r"^.* - INFO - ", lines[i]) and re.match(
                r"^\s*DDDDDDDDDDDDD", lines[i + 2]
            ):
                logger.debug(f"Found latest DMB startup banner at line {i}")
                return "".join(lines[i:])

        return "".join(lines)

    except Exception as e:
        logger.error(f"Error filtering DMB log file: {e}")
        return ""


@logs_router.get("")
async def get_log_file(
    process_name: str = Query(..., description="The process name"),
    logger=Depends(get_logger),
):
    log_path = find_log_file(process_name, logger)
    logger.debug(f"Resolved log path: {log_path}")
    if not log_path or not log_path.exists():
        return {
            "process_name": process_name,
            "log": "",
        }

    try:
        if process_name.lower() == "dmb":
            log_content = filter_dmb_log(log_path, logger)
        else:
            with open(log_path, "r") as log_file:
                log_content = log_file.read()

        return {"process_name": process_name, "log": log_content}
    except Exception as e:
        logger.error(f"Error reading log file for {process_name}: {e}")
        return {"process_name": process_name, "log": ""}
