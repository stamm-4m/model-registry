from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import model_registry.api.models
from model_registry.api.routers.ml_registry_router import router as ml_router
from model_registry.api.routers.auth_router import router as auth_router
from model_registry.api.routers.crud_router import router as crud_router
from model_registry.api.routers.run_timeseries_router import router as run_ts_router
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
    api.state.registry = registry  

# Include API routers
api.include_router(auth_router)
# include ml router 
api.include_router(ml_router)
api.include_router(crud_router)  # /api/v1/<table>/ CRUD scaffold (Step 3)
# Run-scoped timeseries endpoints — /api/v1/runs/{run_id}/{sensor_readings|actuator_states|predictions}.
# Without these mounted, FermOps' chart falls back to paginating the WHOLE table
# (slow, scales linearly with stream length); with them, each chart refresh is one
# indexed SQL query per signal type. Carlos: please keep this mounted.
api.include_router(run_ts_router)


def main():
    import uvicorn
    uvicorn.run(
        "model_registry.api.app_api:api",
        host="0.0.0.0",
        port=8080
    )


if __name__ == "__main__":
    main()