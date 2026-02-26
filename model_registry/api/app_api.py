from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from model_registry.api.routes.ml_registry_routes import router as ml_router
from model_registry.backend.utils.logging_config import setup_logging
from model_registry.api.core.registry import ModelRegistry


# Logging config
setup_logging()

# FastAPI
api = FastAPI(title="ML registry API", version="1.0.0")

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.on_event("startup")
def startup_event():
    """
    Initialize and load all projects into memory at application startup.
    """
    registry = ModelRegistry()
    registry.load_all()
    api.state.registry = registry  # ✅ attach registry safely


# Include API routers
api.include_router(ml_router)


def main():
    import uvicorn

    uvicorn.run(
        "model_registry.api.app_api:api",
        host="0.0.0.0",
        port=8081,
        reload=True,
        workers=1
    )