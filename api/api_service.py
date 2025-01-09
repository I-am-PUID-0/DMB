from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute, APIWebSocketRoute
from uvicorn.config import Config
from uvicorn.server import Server
from utils.dependencies import (
    get_api_state,
    get_process_handler,
    get_logger,
    get_websocket_manager,
)
from api.routers.process import process_router
from api.routers.config import config_router
from api.routers.health import health_router
from api.routers.websocket_logs import websocket_router
from utils.config_loader import CONFIG_MANAGER
import threading


def create_app() -> FastAPI:
    app = FastAPI()

    app.dependency_overrides[get_process_handler] = get_process_handler
    app.dependency_overrides[get_logger] = get_logger
    app.dependency_overrides[get_api_state] = get_api_state
    app.dependency_overrides[get_websocket_manager] = get_websocket_manager

    app.include_router(process_router, prefix="/process", tags=["Process Management"])
    app.include_router(config_router, prefix="/config", tags=["Configuration"])
    app.include_router(health_router, prefix="/health", tags=["Health"])
    app.include_router(websocket_router, prefix="/ws", tags=["WebSocket Logs"])

    logger = get_logger()
    for route in app.routes:
        if isinstance(route, APIRoute):
            logger.debug(f"Route: {route.path} | Methods: {route.methods}")
        elif isinstance(route, APIWebSocketRoute):
            logger.debug(f"WebSocket Route: {route.path}")

    origin_from_config = (
        CONFIG_MANAGER.config.get("dmb", {}).get("frontend", {}).get("origins", None)
    )
    origins = (
        [origin_from_config]
        if origin_from_config
        else ["http://localhost", "http://localhost:8000"]
    )
    logger.info(f"Allowed CORS origins set to: {origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("shutdown")
    async def on_shutdown():
        websocket_manager = get_websocket_manager()
        logger.info("Shutting down WebSocket manager...")
        await websocket_manager.shutdown()
        logger.info("WebSocket manager shutdown complete.")

    return app


def start_fastapi_process():
    app = create_app()

    host = (
        CONFIG_MANAGER.config.get("dmb", {})
        .get("api_service", {})
        .get("host", "0.0.0.0")
    )
    port = CONFIG_MANAGER.config.get("dmb", {}).get("api_service", {}).get("port", 8000)
    log_level = (
        CONFIG_MANAGER.config.get("dmb", {})
        .get("api_service", {})
        .get("log_level", "info")
        .lower()
    )
    logger = get_logger()

    def run_server():
        config = Config(
            app=app,
            host=host,
            port=port,
            log_config=None,
            log_level=log_level,
        )
        server = Server(config)
        server.run()

    uvicorn_thread = threading.Thread(target=run_server, daemon=True)
    uvicorn_thread.start()
    logger.info(f"Started FastAPI server at {host}:{port}")