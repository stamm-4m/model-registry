
from fastapi import APIRouter, HTTPException

from model_registry.api.models.prediction_request import PredictionRequest
from fastapi import Request

router = APIRouter(prefix="", tags=["ML"])

import logging

from model_registry.api.models.predictor import ModelPredictor
from model_registry.api.utils.project_loader import (
    deep_update,
    list_projects_by_id,
    load_model,
    load_project_info,
    save_model,
)

logger = logging.getLogger(__name__)
# ---------------- Project Metadata ----------------

@router.get("/list_projects/")
def list_projects():
    """
    List all projects with their ID and basic information from project_info.yaml.
    """
    try:
        project_map = list_projects_by_id()
        projects = []
        for project_id in project_map.keys():
            info = load_project_info(project_id)
            if not info:
                continue
            projects.append({
                "project_ID": info.get("project_ID", project_id),
                "name": info.get("project_name", project_map[project_id]),
                "description": info.get("description", ""),
                "coordinator": info.get("coordinator", ""),
                "start_date": info.get("start_date", ""),
                "end_date": info.get("end_date", "")
            })
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing projects: {e}")
    
@router.get("/{project_id}/project_info/")
def get_project_info(project_id: str):
    """Get information about project

    Args:
        project_id (str): identification of project

    Raises:
        HTTPException: No info for project ID

    Returns:
        stream: Project metadata information
    """
    info = load_project_info(project_id)
    if not info:
        raise HTTPException(status_code=404, detail=f"No info for project ID {project_id}")
    return info

@router.get("/{project_id}/db_config/")
def get_db_config(project_id: str):
    info = load_project_info(project_id)
    return info.get("db_config", {})

@router.get("/{project_id}/references/")
def get_references(project_id: str):
    info = load_project_info(project_id)
    return info.get("references", [])

@router.get("/{project_id}/variables/")
def get_variables(project_id: str):
    info = load_project_info(project_id)
    return info.get("variables", [])

# ---------------- Model Endpoints ----------------

@router.get("/{project_id}/list_models/")
def list_models_endpoint(project_id: str, request: Request):
    """
    List all models in a project with both model_ID and human-readable name.
    """
    try:
        registry = request.app.state.registry

        models = registry.get_project(project_id)

        return [
            {
                "model_ID": model_id,
                "model_name": info["name"],
                "metadata": info["config"]["ml_model_configuration"]["model_identification"]
            }
            for model_id, info in models.items()
        ]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{project_id}/metadata/{model_id}")
def get_model_metadata(project_id: str, model_id: str, request: Request):
    """Return model metadata using model ID."""
    try:
        registry = request.app.state.registry
        models = registry.get_project(project_id)

        if model_id not in models:
            raise ValueError(
                f"Model ID '{model_id}' not found in project '{project_id}'"
            )

        return models[model_id]["config"]["ml_model_configuration"]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{project_id}/models_full/")
def list_models_full(project_id: str, request: Request):
    try:
        registry = request.app.state.registry
        models_full = registry.get_models_full(project_id)
        return models_full
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---  ------------- Model update ----------------
@router.put("/{project_id}/update/{model_id}")
def update_model(project_id: str, model_id: str, payload: dict, request: Request):
    try:
        registry = request.app.state.registry
        registry.update_model(project_id, model_id, payload)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------- Prediction Endpoint ----------------

@router.post("/{project_id}/predict/{model_id}")
def predict(project_id: str, model_id: str, request: PredictionRequest, req: Request):
    """
    Predict using a model identified by its ID.
    """
    try:
        registry = req.app.state.registry
        models = registry.get_project(project_id)

        if model_id not in models:
            raise HTTPException(status_code=404, detail="Model not found")

        model_info = models[model_id]

        model = model_info["model"]
        config = model_info["config"]
        input_scaler = model_info["input_scaler"]
        output_scaler = model_info["output_scaler"]
        outputs = config["ml_model_configuration"]["outputs"]
        
        logger.info(f"Model and scalers loaded for project '{project_id}', model '{model}'")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Fix: language can be list of dicts or dict
    language_info = config["ml_model_configuration"]["model_description"]["language"]
    if isinstance(language_info, list):
        lang_entry = next((item for item in language_info if "name" in item), {})
        language = lang_entry.get("name", "").lower()
    else:
        language = language_info.get("name", "").lower()

    print(f"DEBUG >> model_id={model_id}, language={language}")

    # If R model -> proxy to R FastAPI
    if language == "r":
        return ModelPredictor._proxy_to_r_api(project_id, model_id, request)

    # Otherwise -> run Python prediction
    logger.info(f"Running prediction for project '{project_id}', model '{model}' using Python model.")
    return ModelPredictor(model, input_scaler, output_scaler, outputs).predict(request)



