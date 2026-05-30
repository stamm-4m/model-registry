import logging
import os
from typing import Any, Dict, Optional
from uuid import UUID

import joblib
import tensorflow as tf

from model_registry.api.core.database import SessionLocal
from model_registry.api.models.model import Model
from model_registry.api.models.project import Project
from model_registry.api.models.project_model import ProjectModel

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_uuid(value: str) -> bool:
    try:
        UUID(str(value))
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def _project_filter(project_id: str):
    """Build a SQLAlchemy filter accepting either Project.id (UUID) or
    Project.project_id (string slug)."""
    if _is_uuid(project_id):
        return Project.id == UUID(str(project_id))
    return Project.project_id == str(project_id)


def _model_filter(model_id: str):
    if _is_uuid(model_id):
        return Model.id == UUID(str(model_id))
    return Model.slug == str(model_id)


def _synthesize_yaml_shape(model_row: Model) -> Dict[str, Any]:
    """Build the ``ml_model_configuration`` dict the dashboard expects.

    Maps the ``models`` table columns (plus its ``config`` JSONB blob) onto
    the historical YAML-shaped keys consumed by the routers and the
    frontend, so callers don't need to know data now lives in the DB.
    Dedicated columns (``learner``, ``model_type``, ``language``,
    ``packages``, ``config_files``, ``input_time_interval``,
    ``training_information``, ``doi``, ``external_uuid``,
    ``creation_date``, ``status_description``, ``model_architecture``)
    are read first; the ``config`` JSONB is used only as a fallback for
    anything still living there.
    """
    raw_config = dict(model_row.config or {})
    # ``config`` JSONB may already be a full ml_model_configuration blob, or
    # just hold algo-specific bits (hyperparameters, packages, ...). Support
    # both shapes by treating any non-mlc keys as supplemental metadata.
    base_config: Dict[str, Any] = {}
    mlc: Dict[str, Any] = {}
    if isinstance(raw_config.get("ml_model_configuration"), dict):
        base_config = {k: v for k, v in raw_config.items() if k != "ml_model_configuration"}
        mlc = dict(raw_config["ml_model_configuration"])
        supplemental: Dict[str, Any] = {}
    else:
        supplemental = raw_config

    # ----- Identification ---------------------------------------------------
    mlc.setdefault("model_identification", {})
    ident_existing = mlc["model_identification"]
    mlc["model_identification"].update({
        "ID": model_row.slug or str(model_row.id),
        "UUID": model_row.external_uuid or str(model_row.id),
        "uuid": str(model_row.id),
        "doi": model_row.doi or ident_existing.get("doi", "") or "",
        "name": model_row.name,
        "version": model_row.version,
        "status": model_row.is_active,
        "status_description": (
            model_row.status_description
            or model_row.validation_notes
            or model_row.notes
            or ident_existing.get("status_description", "")
            or ""
        ),
        "author": model_row.authors or "",
        "authors": model_row.authors or "",
        "creation_date": (
            model_row.creation_date
            or (model_row.created_at.isoformat() if model_row.created_at else "")
        ),
        "created_at": (
            model_row.created_at.isoformat() if model_row.created_at else None
        ),
        "algorithm": model_row.algorithm,
        "description": model_row.description,
    })

    # ----- Description ------------------------------------------------------
    mlc.setdefault("model_description", {})
    md = mlc["model_description"]
    md["learner"] = model_row.learner or md.get("learner") or model_row.algorithm or ""
    md["model_type"] = model_row.model_type or md.get("model_type") or supplemental.get("model_type", "")
    md.setdefault("model_name", model_row.name or "")
    md.setdefault("description", model_row.description or "")
    md["language"] = list(model_row.language or []) or md.get("language") or supplemental.get("language", []) or []
    md["packages"] = list(model_row.packages or []) or md.get("packages") or supplemental.get("packages", []) or []
    md["input_time_interval"] = (
        dict(model_row.input_time_interval)
        if model_row.input_time_interval
        else (md.get("input_time_interval") or supplemental.get("input_time_interval", {}) or {})
    )
    if model_row.model_architecture:
        md.setdefault("model_architecture", dict(model_row.model_architecture))

    # ----- Config files (merge column dict onto any existing values) --------
    cf = dict(md.get("config_files") or {})
    cf.update(dict(model_row.config_files or {}))
    if model_row.artifact_path and not cf.get("model_file"):
        cf["model_file"] = os.path.basename(model_row.artifact_path)
    cf.setdefault("server", "")
    cf.setdefault("port", "")
    cf.setdefault("rest_api", "")
    md["config_files"] = cf

    # ----- Training information --------------------------------------------
    ti_existing = dict(mlc.get("training_information") or {})
    ti_col = dict(model_row.training_information or {})
    ti = {**ti_existing, **ti_col}
    ti.setdefault("hyperparameters", supplemental.get("hyperparameters", {}) or {})
    ti.setdefault("number_of_instances", supplemental.get("number_of_instances", ""))
    ti.setdefault("validation", supplemental.get("validation", model_row.validation_status or ""))
    ti.setdefault("experiments_ID", supplemental.get("experiments_ID", []) or [])
    if model_row.training_dataset_hash:
        ti.setdefault("training_dataset_hash", model_row.training_dataset_hash)
    mlc["training_information"] = ti

    # ----- Inputs / outputs -------------------------------------------------
    # ``model_row.inputs`` / ``model_row.outputs`` may be stored as either:
    #   - a flat list of variable names (legacy), or
    #   - a dict ``{"scaler": "...", "features"|"information": [ ... ]}``
    # Preserve both the rich ``features``/``information`` list and the
    # flat ``variables`` list used by inference.
    raw_inputs = model_row.inputs
    raw_outputs = model_row.outputs

    if isinstance(raw_inputs, dict):
        input_features = list(raw_inputs.get("features") or [])
        input_scaler = raw_inputs.get("scaler")
        input_vars = [
            (f.get("name") if isinstance(f, dict) else f)
            for f in input_features
            if (isinstance(f, dict) and f.get("name")) or isinstance(f, str)
        ]
    else:
        input_vars = list(raw_inputs or [])
        input_features = [{"name": v} for v in input_vars]
        input_scaler = None

    if isinstance(raw_outputs, dict):
        output_info = list(raw_outputs.get("information") or [])
        output_scaler = raw_outputs.get("scaler")
        output_vars = [
            (o.get("name") if isinstance(o, dict) else o)
            for o in output_info
            if (isinstance(o, dict) and o.get("name")) or isinstance(o, str)
        ]
    else:
        output_vars = list(raw_outputs or [])
        output_info = [{"name": v} for v in output_vars]
        output_scaler = None

    mlc.setdefault("inputs", {})
    mlc["inputs"]["variables"] = input_vars
    mlc["inputs"]["features"] = input_features
    if input_scaler is not None:
        mlc["inputs"]["scaler"] = input_scaler

    mlc.setdefault("outputs", {})
    mlc["outputs"]["variables"] = output_vars
    mlc["outputs"]["information"] = output_info
    if output_scaler is not None:
        mlc["outputs"]["scaler"] = output_scaler

    mlc["metrics"] = dict(model_row.metrics or {})
    mlc["tags"] = list(model_row.tags or [])

    base_config["ml_model_configuration"] = mlc
    logger.debug(f"Synthesized YAML-shaped config for model {model_row.id}")
    return base_config


def _resolve_artifact_path(path: str) -> Optional[str]:
    """Locate an artifact file on disk.

    The DB sometimes stores paths with a leading ``model-registry/`` prefix
    (the repo folder name) or as plain relative paths. Try a few sensible
    bases before giving up.
    """
    if not path:
        return None

    # Normalize separators so Windows / POSIX paths both work.
    normalized = path.replace("\\", "/").lstrip("./")

    # repo root = three levels up from this file (api/core/registry.py
    # -> api -> model_registry -> repo root).
    here = os.path.dirname(os.path.abspath(__file__))
    api_dir = os.path.dirname(here)            # .../model_registry/api
    pkg_dir = os.path.dirname(api_dir)         # .../model_registry
    repo_root = os.path.dirname(pkg_dir)       # .../<repo>

    # Strip a leading "<repo-folder-name>/" if present (e.g. "model-registry/").
    repo_folder = os.path.basename(repo_root)
    stripped = normalized
    if stripped.startswith(repo_folder + "/"):
        stripped = stripped[len(repo_folder) + 1:]

    candidates = [
        path,
        normalized,
        os.path.join(repo_root, normalized),
        os.path.join(repo_root, stripped),
        os.path.join(pkg_dir, stripped),
        os.path.join(api_dir, stripped),
        os.path.join(os.getcwd(), normalized),
        os.path.join(os.getcwd(), stripped),
    ]

    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate
    return None


def _load_artifact(model_row: Model):
    """Load the binary artifact pointed to by ``Model.artifact_path``.

    Returns ``None`` if the file is missing or the format isn't supported.
    """
    path = model_row.artifact_path
    if not path:
        return None

    resolved = _resolve_artifact_path(path)
    if resolved is None:
        logger.warning(f"Artifact file not found: {path}")
        return None

    fmt = (model_row.artifact_format or os.path.splitext(resolved)[-1]).lower()
    if fmt.startswith("."):
        fmt = fmt[1:]

    try:
        if fmt in ("keras", "h5"):
            return tf.keras.models.load_model(resolved)
        if fmt in ("joblib", "pkl", "pickle"):
            return joblib.load(resolved)
        if fmt in ("rds", "rdata"):
            logger.info(f"R model {resolved} registered (metadata + REST only).")
            return None
        logger.warning(f"Unsupported artifact format '{fmt}' for {resolved}")
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception(f"Failed to load artifact {resolved}: {exc}")
    return None


def _load_scaler(scaler_path: Optional[str]):
    if not scaler_path:
        return None
    resolved = _resolve_artifact_path(scaler_path)
    if resolved is None:
        return None
    try:
        return joblib.load(resolved)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception(f"Failed to load scaler {resolved}: {exc}")
        return None


def _build_entry(model_row: Model) -> Dict[str, Any]:
    """Build the in-memory record kept under ``registry.projects[pid][mid]``."""
    config = _synthesize_yaml_shape(model_row)
    raw_config = dict(model_row.config or {})
    return {
        "config": config,
        "model": _load_artifact(model_row),
        "name": model_row.name,
        "input_scaler": _load_scaler(raw_config.get("input_scaler_path")),
        "output_scaler": _load_scaler(raw_config.get("output_scaler_path")),
        "_row_id": str(model_row.id),
        "_slug": model_row.slug,
    }


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class ModelRegistry:
    """
    Central registry that mirrors the ``projects``, ``project_models`` and
    ``models`` tables into memory.

    Project / model lookups accept either the row UUID or the human-readable
    slug (``Project.project_id`` / ``Model.slug``) so existing dashboard URLs
    keep working.
    """

    def __init__(self):
        # { project_slug: { model_slug: entry_dict } }
        self.projects: Dict[str, Dict[str, Dict[str, Any]]] = {}

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load_all(self):
        """Load every project from ``/api/v1/projects`` (DB table)."""
        logger.info("Loading all projects from DB into registry...")
        db = SessionLocal()
        try:
            for project in db.query(Project).all():
                self._load_project_row(db, project)
        finally:
            db.close()

    def load_project(self, project_id: str):
        """Load a single project by UUID or slug."""
        db = SessionLocal()
        try:
            project = db.query(Project).filter(_project_filter(project_id)).first()
            if project is None:
                raise ValueError(f"Project '{project_id}' not found")
            return self._load_project_row(db, project)
        finally:
            db.close()

    def reload_project(self, project_id: str):
        """Force reload of a project from the DB."""
        logger.info(f"Reloading project '{project_id}'")
        key = self._resolve_project_key(project_id)
        if key and key in self.projects:
            del self.projects[key]
        return self.load_project(project_id)

    def _load_project_row(self, db, project: Project):
        logger.info(f"Loading project '{project.project_id}' into registry")
        models: Dict[str, Dict[str, Any]] = {}

        rows = (
            db.query(Model)
            .join(ProjectModel, ProjectModel.model_id == Model.id)
            .filter(ProjectModel.project_id == project.id)
            .all()
        )
        for model_row in rows:
            key = model_row.slug or str(model_row.id)
            models[key] = _build_entry(model_row)

        self.projects[project.project_id] = models
        return models

    # ------------------------------------------------------------------
    # Read API (kept stable for existing callers)
    # ------------------------------------------------------------------

    def _resolve_project_key(self, project_id: str) -> Optional[str]:
        """Map either UUID or slug onto the slug key we store under."""
        if project_id in self.projects:
            return project_id
        if _is_uuid(project_id):
            db = SessionLocal()
            try:
                project = db.query(Project).filter(Project.id == UUID(str(project_id))).first()
                if project and project.project_id in self.projects:
                    return project.project_id
            finally:
                db.close()
        return None

    def get_project(self, project_id: str):
        key = self._resolve_project_key(project_id)
        if key is None:
            raise ValueError(f"Project '{project_id}' not loaded")
        return self.projects[key]

    def get_models_full(self, project_id: str):
        """Return full config dicts for all *online* models in a project."""
        project = self.get_project(project_id)
        return [
            entry["config"]
            for entry in project.values()
            if entry
                .get("config", {})
                .get("ml_model_configuration", {})
                .get("model_identification", {})
                .get("status", "")
                .lower() == "online"
        ]

    # ------------------------------------------------------------------
    # Mutations -- write through to the DB then refresh memory
    # ------------------------------------------------------------------

    _COLUMN_ALIASES = {
        "ID": "slug",
        "id": "slug",
        "name": "name",
        "description": "description",
        "algorithm": "algorithm",
        "status": "status",
        "version": "version",
        "tags": "tags",
        "inputs": "inputs",
        "outputs": "outputs",
        "metrics": "metrics",
        "artifact_path": "artifact_path",
        "artifact_format": "artifact_format",
        "notes": "notes",
    }

    def update_model(self, project_id: str, model_id: str, updates: dict):
        """Update a model row.

        ``updates`` may contain either real ``Model`` column names, or the
        legacy ``ml_model_configuration`` nested dict -- in which case the
        nested payload is merged into ``Model.config`` (JSONB) and only the
        well-known identification fields are mapped to dedicated columns.
        """
        db = SessionLocal()
        try:
            project = db.query(Project).filter(_project_filter(project_id)).first()
            if project is None:
                raise ValueError(f"Project '{project_id}' not loaded")

            model_row = (
                db.query(Model)
                .join(ProjectModel, ProjectModel.model_id == Model.id)
                .filter(ProjectModel.project_id == project.id)
                .filter(_model_filter(model_id))
                .first()
            )
            if model_row is None:
                raise ValueError(
                    f"Model '{model_id}' not found in project '{project_id}'"
                )

            # Legacy nested-YAML payload -- merge into JSONB + lift known fields.
            mlc = (updates or {}).get("ml_model_configuration")
            if mlc is not None:
                merged_config = dict(model_row.config or {})
                merged_config.setdefault("ml_model_configuration", {})
                _deep_update(merged_config["ml_model_configuration"], mlc)
                model_row.config = merged_config

                ident = mlc.get("model_identification") or {}
                if "name" in ident:
                    model_row.name = ident["name"]
                if "status" in ident:
                    model_row.status = ident["status"]
                if "version" in ident:
                    model_row.version = ident["version"]
                if "algorithm" in ident:
                    model_row.algorithm = ident["algorithm"]
                if "description" in ident:
                    model_row.description = ident["description"]

            # Flat-key payload (real column names).
            for key, value in (updates or {}).items():
                if key == "ml_model_configuration":
                    continue
                column = self._COLUMN_ALIASES.get(key)
                if column is None:
                    continue
                setattr(model_row, column, value)

            db.commit()
            db.refresh(model_row)
            self._load_project_row(db, project)
        finally:
            db.close()


def _deep_update(original: dict, updates: dict) -> dict:
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(original.get(key), dict):
            _deep_update(original[key], value)
        else:
            original[key] = value
    return original