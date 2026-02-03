from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from model_registry.api.routes.ml_registry_routes import router as ml_router
from model_registry.backend.utils.logging_config import setup_logging

# Logging config
setup_logging()


# FastAPI
api = FastAPI(title="ML registry API", version="1.0.0")
api.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# Include API routers
api.include_router(ml_router)

def main():
    import uvicorn
    uvicorn.run(
        "model_registry.api.app_api:api",  # ruta al objeto FastAPI
        host="0.0.0.0",
        port=8081,
        reload=True,  # <-- recarga automática activada
        workers=1    # opcional, en desarrollo suele ser 1
    )