from fastapi import APIRouter, HTTPException, Request

from model_registry.api.models.explain_request import ExplainRequest
from model_registry.api.models.laboratory_project import LaboratoryProject
from model_registry.api.models.prediction_request import PredictionRequest
from model_registry.api.models.project import Project
from model_registry.api.services import explainability

router = APIRouter(prefix="", tags=["ML"])

import logging

from fastapi import Depends
from sqlalchemy.orm import Session

from model_registry.api.core.database import get_db
from model_registry.api.core.dependencies import require_permission_resource
from model_registry.api.models.predictor import ModelPredictor
from model_registry.api.utils.project_loader import load_project_info

logger = logging.getLogger(__name__)

# ---------------- Project Metadata ----------------


@router.get("/list_projects/")
def list_projects(
    user=Depends(require_permission_resource("project:read", "Projects")),
    db: Session = Depends(get_db),
):
    """
    List all projects with their ID and basic information from project_info.yaml
    filtered by user's laboratory access.
    """
    try:
        logger.info(f"Listing projects for user '{user.email}' and User ID '{user.id}'")
        user_lab_ids = set(
            lu.laboratory_id
            for lu in user.laboratory_users
            if lu.laboratory_id is not None
        )

        if not user_lab_ids:
            logger.debug(f"User '{user.email}' has no laboratory access.")
            return []

        # get project IDs from laboratory_project table based on user's lab access
        project_ids = (
            db.query(LaboratoryProject.project_id)
            .filter(LaboratoryProject.laboratory_id.in_(user_lab_ids))
            .distinct()
            .all()
        )
        project_ids = [p[0] for p in project_ids]

        if not project_ids:
            logger.debug(f"User '{user.email}' has no access to any projects.")
            return []

        # get projects based on project IDs
        projects_db = db.query(Project).filter(Project.id.in_(project_ids)).all()
        projects = []
        for project in projects_db:
            try:
                info = load_project_info(project.project_id) or {}
                projects.append(
                    {
                        "project_ID": info.get("project_ID", project.project_id),
                        "name": info.get("project_name", project.name),
                        "description": info.get("description", project.description),
                        "create_at": info.get("create_at", project.created_at),
                    }
                )
            except Exception as exc:
                # A single corrupt project must not break the listing.
                logger.warning(
                    "Skipping project_id=%s due to error: %s",
                    project.project_id,
                    exc,
                )
                continue
        return projects
    except Exception as e:
        logger.exception("list_projects failed")
        raise HTTPException(status_code=500, detail=f"Error listing projects: {e}")


@router.get("/{project_id}/project_info/")
def get_project_info(
    project_id: str,
    user=Depends(require_permission_resource("project:read", "Projects")),
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
        raise HTTPException(
            status_code=404, detail=f"No info for project ID {project_id}"
        )
    return info


@router.get("/{project_id}/db_config/")
def get_db_config(
    project_id: str,
    user=Depends(require_permission_resource("project:read", "Projects")),
):
    info = load_project_info(project_id)
    return info.get("db_config", {})


@router.get("/{project_id}/references/")
def get_references(
    project_id: str,
    user=Depends(require_permission_resource("project:read", "Projects")),
):
    info = load_project_info(project_id)
    return info.get("references", [])


@router.get("/{project_id}/variables/")
def get_variables(
    project_id: str,
    user=Depends(require_permission_resource("project:read", "Projects")),
):
    info = load_project_info(project_id)
    return info.get("variables", [])


# ---------------- Model Endpoints ----------------


@router.get("/{project_id}/list_models/")
def list_models_endpoint(
    project_id: str,
    request: Request,
    user=Depends(require_permission_resource("models:read", "Models")),
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
                "metadata": info["config"]["ml_model_configuration"][
                    "model_identification"
                ],
            }
            for model_id, info in models.items()
        ]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{project_id}/reload/")
def reload_project_endpoint(
    project_id: str,
    request: Request,
    user=Depends(require_permission_resource("models:write", "Models")),
):
    """Force the in-memory registry to reload ``project_id`` from the DB.

    Called by the backend right after creating / linking a new model so the
    next read endpoint sees the fresh state without a process restart.
    """
    try:
        registry = request.app.state.registry
        models = registry.reload_project(project_id)
        return {"project_id": project_id, "model_count": len(models)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{project_id}/metadata/{model_id}")
def get_model_metadata(
    project_id: str,
    model_id: str,
    request: Request,
    user=Depends(require_permission_resource("models:read", "Models")),
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
    user=Depends(require_permission_resource("models:read", "Models")),
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
    user=Depends(require_permission_resource("models:edit", "Models")),
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
    user=Depends(require_permission_resource("models:deploy", "Models")),
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

        logger.info(
            f"Model and scalers loaded for project '{project_id}', model '{model}'"
        )
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
    logger.info(
        f"Running prediction for project '{project_id}', model '{model}' using Python model."
    )
    return ModelPredictor(model, input_scaler, output_scaler, outputs).predict(request)


# ---------------- Explainability Endpoint ----------------


@router.post("/{project_id}/explain/{model_id}")
def explain_model(
    project_id: str,
    model_id: str,
    req: Request,
    body: ExplainRequest | None = None,
    user=Depends(require_permission_resource("models:read", "Models")),
):
    """Return XAI explanations for a model. Loads nothing — uses the model the
    registry already holds in memory (resolved from the DB row). With no body,
    explanations use a background sampled from each feature's declared range;
    pass `rows` (+ optional `target_column`) to evaluate on uploaded data."""
    try:
        models = req.app.state.registry.get_project(project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    if model_id not in models:
        raise HTTPException(status_code=404, detail="Model not found")

    info = models[model_id]
    model = info.get("model")
    config = info.get("config")
    scaler = info.get("input_scaler")
    family = body.family if body else None

    if body and body.rows:
        try:
            import pandas as pd

            df = pd.DataFrame(body.rows)
        except Exception as e:
            return {"ok": False, "reason": f"could not parse rows: {e}"}
        y = None
        if body.target_column and body.target_column in df.columns:
            y = df[body.target_column].to_numpy()
        return explainability.explain_with_data(model, config, scaler, family, df, y)

    return explainability.explain(model, config, scaler, family)


# ---------------- Artifact / Bundle Download ----------------

def _resolve_artifact_path(project_id: str, model_id: str, req):
    """Return (config, absolute_file_path_or_None) for a model, using the
    already-loaded registry entry + the project's models dir."""
    import os
    from model_registry.api.utils.project_loader import get_project_paths
    try:
        models = req.app.state.registry.get_project(project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    if model_id not in models:
        raise HTTPException(status_code=404, detail="Model not found")
    config = models[model_id].get("config") or {}
    mlc = config.get("ml_model_configuration", {})
    model_file = (
        (mlc.get("model_description", {}) or {}).get("config_files", {}) or {}
    ).get("model_file")
    path = None
    if model_file:
        candidate = os.path.join(get_project_paths(project_id)["MODEL_DIR"], model_file)
        if os.path.exists(candidate):
            path = candidate
    return config, model_file, path


def _build_metadata_xlsx(config) -> bytes:
    """Well-structured Excel of a model's metadata, one sheet per section."""
    import io
    import json

    import pandas as pd

    mlc = (config or {}).get("ml_model_configuration", {}) or {}
    ident = mlc.get("model_identification", {}) or {}
    desc = mlc.get("model_description", {}) or {}
    training = mlc.get("training_information", {}) or {}
    inputs = mlc.get("inputs", {}) or {}
    outputs = mlc.get("outputs", {}) or {}

    def _cell(v):
        return json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v

    def kv_df(d):
        rows = [{"Field": k, "Value": _cell(v)} for k, v in (d or {}).items()]
        return pd.DataFrame(rows or [{"Field": "", "Value": ""}])

    def list_df(items, cols):
        rows = []
        for it in (items or []):
            if isinstance(it, dict):
                rows.append({c: _cell(it.get(c)) for c in cols})
            elif isinstance(it, str):
                rows.append({cols[0]: it})
        return pd.DataFrame(rows or [{c: "" for c in cols}])

    overview = {
        **ident,
        "learner": desc.get("learner"), "model_type": desc.get("model_type"),
        "model_name": desc.get("model_name"), "description": desc.get("description"),
    }
    description = {
        "language": desc.get("language"), "packages": desc.get("packages"),
        "config_files": desc.get("config_files"),
        "input_time_interval": desc.get("input_time_interval"),
    }
    tr = dict(training)
    hp = tr.pop("hyperparameters", None)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        kv_df(overview).to_excel(xw, sheet_name="Overview", index=False)
        kv_df(description).to_excel(xw, sheet_name="Description", index=False)
        kv_df(tr).to_excel(xw, sheet_name="Training", index=False)
        if isinstance(hp, dict) and hp:
            kv_df(hp).to_excel(xw, sheet_name="Hyperparameters", index=False)
        list_df(inputs.get("features") if isinstance(inputs, dict) else inputs,
                ["name", "type", "units", "lag", "feature_scaling",
                 "expected_range", "description"]).to_excel(
                    xw, sheet_name="Inputs", index=False)
        list_df(outputs.get("information") if isinstance(outputs, dict) else outputs,
                ["name", "description", "units", "forecast_horizon",
                 "feature_scaling", "expected_range"]).to_excel(
                    xw, sheet_name="Outputs", index=False)
    buf.seek(0)
    return buf.getvalue()


@router.get("/{project_id}/model_artifact/{model_id}")
def download_model_artifact(
    project_id: str,
    model_id: str,
    req: Request,
    user=Depends(require_permission_resource("models:read", "Models")),
):
    """Stream the raw model binary. 404 if the model has no artifact on disk."""
    import os
    from fastapi.responses import FileResponse
    _config, model_file, path = _resolve_artifact_path(project_id, model_id, req)
    if not path:
        raise HTTPException(status_code=404, detail="This model has no downloadable artifact.")
    return FileResponse(path, filename=os.path.basename(model_file),
                        media_type="application/octet-stream")


@router.get("/{project_id}/model_bundle/{model_id}")
def download_model_bundle(
    project_id: str,
    model_id: str,
    req: Request,
    user=Depends(require_permission_resource("models:read", "Models")),
):
    """Zip {binary + metadata.yaml}, matching the stamm-sdk ArtifactBundle.
    metadata.yaml is always present; the binary is added when it exists on disk."""
    import io
    import os
    import zipfile

    import yaml
    from fastapi.responses import StreamingResponse

    config, model_file, path = _resolve_artifact_path(project_id, model_id, req)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("metadata.yaml",
                   yaml.safe_dump(config or {}, sort_keys=False, allow_unicode=True))
        if path:
            z.write(path, arcname=os.path.basename(model_file))
        try:
            z.writestr("metadata.xlsx", _build_metadata_xlsx(config))
        except Exception as exc:  # openpyxl missing / build issue -> skip xlsx
            logging.getLogger(__name__).info("metadata.xlsx skipped: %s", exc)
    buf.seek(0)
    fname = f"{model_id}_bundle.zip"
    return StreamingResponse(
        buf, media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )
