from api.api_state import APIState
from utils.processes import ProcessHandler
from logging import Logger
from api.connection_manager import ConnectionManager

_shared_instances = {}


def initialize_dependencies(process_handler, updater, websocket_manager, logger):
    _shared_instances["process_handler"] = process_handler
    _shared_instances["updater"] = updater
    _shared_instances["websocket_manager"] = websocket_manager
    _shared_instances["logger"] = logger
    _shared_instances["api_state"] = APIState(
        process_handler=process_handler, logger=logger
    )


def get_process_handler() -> ProcessHandler:
    return _shared_instances["process_handler"]


def get_updater() -> object:
    return _shared_instances["updater"]


def get_websocket_manager() -> ConnectionManager:
    return _shared_instances["websocket_manager"]


def get_logger() -> Logger:
    return _shared_instances["logger"]


def get_api_state() -> APIState:
    return _shared_instances["api_state"]
