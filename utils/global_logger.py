from utils.logger import get_logger

logger = None
_logger_initialized = False
websocket_manager = None


def initialize_logger():
    global logger, _logger_initialized, websocket_manager
    if not _logger_initialized:
        from utils.api_service import websocket_manager

        logger = get_logger(
            log_name="DMB", log_dir="./log", websocket_manager=websocket_manager
        )
        logger.debug(f"Logger initialized with websocket manager: {websocket_manager}")
        _logger_initialized = True
    else:
        logger.debug("Logger already initialized.")


initialize_logger()