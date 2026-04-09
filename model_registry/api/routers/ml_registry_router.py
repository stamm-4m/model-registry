
from fastapi import APIRouter, HTTPException

from model_registry.api.models import user
from model_registry.api.models.prediction_request import PredictionRequest
from model_registry.api.models.laboratory_project import LaboratoryProject
from fastapi import Request
from model_registry.api.models.project import Project

router = APIRouter(prefix="", tags=["ML"])

import logging
from model_registry.api.core.constants.permissions import Permission as PERMISSIONS
from model_registry.api.core.dependencies import require_permissions, require_permissions_projects
from fastapi import Depends, HTTPException
from model_registry.api.models.user import User
from sqlalchemy.orm import Session
from model_registry.api.core.database import get_db
from model_registry.api.models.predictor import ModelPredictor
from model_registry.api.utils.project_loader import (
    load_project_info
)

logger = logging.getLogger(__name__)

# ---------------- Project Metadata ----------------

@router.get("/list_projects/")
def list_projects(
    user=Depends(require_permissions([PERMISSIONS.VIEW_MODEL])),
    db: Session = Depends(get_db)
):
    """
    List all projects with their ID and basic information from project_info.yaml
    filtered by user's laboratory access.
    """
    try:
        user_lab_ids = list(set(ur.laboratory_id for ur in user.roles if ur.laboratory_id))
        if not user_lab_ids:
            logger.debug(f"User '{user.email}' has no laboratory access.")
            return []  # No lab access
        # get projects id
        project_ids = (
            db.query(LaboratoryProject.project_id)
            .filter(LaboratoryProject.laboratory_id.in_(user_lab_ids))
            .all()
        )
        project_ids = [p[0] for p in project_ids]
        if not project_ids:
            logger.debug(f"User '{user.email}' has no access to any projects.")
            return []  # No projects for user's labs
        # Get info db by projects
        projects_db = (
            db.query(Project)
            .filter(Project.id.in_(project_ids))
            .all()
        )
        projects = []
        for project in projects_db:
            info = load_project_info(project.project_id)
            if not info:
                continue
            projects.append({
                "project_ID": info.get("project_ID", project.project_id),
                "name": info.get("project_name", project.name),
                "description": info.get("description", project.description),
                "create_at": info.get("create_at", project.created_at),
            })
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing projects: {e}")

@router.get("/{project_id}/project_info/")
def get_project_info(
    project_id: str,
    user=Depends(require_permissions_projects([PERMISSIONS.VIEW_MODEL])),
):
    """Get information about project

    Args:
        project_id (str): identification of project
        user (User, optional): user info from token. Defaults to Depends(require_permissions([PERMISSIONS.VIEW_MODEL])).
        db (Session, optional): db session. Defaults to Depends(get_db).

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
def get_db_config(
    project_id: str,
    user=Depends(require_permissions_projects([PERMISSIONS.VIEW_MODEL]))
):
    info = load_project_info(project_id)
    return info.get("db_config", {})

@router.get("/{project_id}/references/")
def get_references(
    project_id: str,
    user=Depends(require_permissions_projects([PERMISSIONS.VIEW_MODEL]))
):
    info = load_project_info(project_id)
    return info.get("references", [])

@router.get("/{project_id}/variables/")
def get_variables(
    project_id: str,
    user=Depends(require_permissions_projects([PERMISSIONS.VIEW_MODEL]))
):
    info = load_project_info(project_id)
    return info.get("variables", [])

# ---------------- Model Endpoints ----------------

@router.get("/{project_id}/list_models/")
def list_models_endpoint(
    project_id: str,
    request: Request,
    user=Depends(require_permissions_projects([PERMISSIONS.VIEW_MODEL])),
):
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
def get_model_metadata(
    project_id: str, 
    model_id: str, 
    request: Request,
    user=Depends(require_permissions_projects([PERMISSIONS.VIEW_MODEL]))
    ):
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
def list_models_full(
    project_id: str,
    request: Request,
    user=Depends(require_permissions_projects([PERMISSIONS.VIEW_MODEL]))
):
    """List all models in a project with full metadata, but only for models with status "online".

    Args:
        project_id (str): identification of project
        request (Request): request object to access registry

    Raises:
        HTTPException: Error accessing registry or project

    Returns:
        models_full (list): List of model configurations for all online models in the project
    """
    ""
    try:
        registry = request.app.state.registry
        models_full = registry.get_models_full(project_id)
        return models_full
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---  ------------- Model update ----------------
@router.put("/{project_id}/update/{model_id}")
def update_model(
    project_id: str, 
    model_id: str, 
    payload: dict, 
    request: Request,
    user=Depends(require_permissions_projects([PERMISSIONS.EDIT_MODEL]))
    ):
    try:
        registry = request.app.state.registry
        registry.update_model(project_id, model_id, payload)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------- Prediction Endpoint ----------------

@router.post("/{project_id}/predict/{model_id}")
def predict(
    project_id: str,
    model_id: str,
    request: PredictionRequest,
    req: Request,
    user=Depends(require_permissions_projects([PERMISSIONS.USAGE_MODEL]))
):
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



