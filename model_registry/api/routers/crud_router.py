"""
Auto-generated CRUD router for every SQLAlchemy ORM model.

Mounts ``/api/v1/<table_name>/`` for each model, with list / get / create /
update / delete endpoints. Auth is enforced via ``require_permissions``.

Permission policy (v1):
* Read endpoints (`list`, `get`)         -> require ``VIEW_MODEL``
* Write endpoints (`create`, `update`,
  `delete`)                              -> require ``MANAGE_PROJECT``

These can be tightened per-table later by hand. For now everything goes
through the same broad pair so authenticated users with the standard
"engineer" role can use the API end-to-end.
"""

import logging
from typing import Any

from fastapi import APIRouter

from model_registry.api import models as M
from model_registry.api.core.constants.permissions import PermissionManager
from model_registry.api.scaffold import register_crud
from model_registry.backend.services.template_validator import (
    TemplateValidationError,
    validate_model_payload,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")


# Permission sets for CRUD operations. These are broad and can be tightened
def get_read_perms():
    # Can be customized to get read permissions based on your naming convention
    return [p.name for p in PermissionManager.all() if ":read" in p.name]


def get_write_perms():
    # Can be customized to get write permissions based on your naming convention
    return [
        p.name
        for p in PermissionManager.all()
        if any(s in p.name for s in (":write", ":edit", ":deploy"))
    ]


READ = get_read_perms()
WRITE = get_write_perms()


# Map from file extension → artifact.format enum value in base.schema.json
_EXT_TO_FORMAT = {
    "pkl": "pickle",
    "pickle": "pickle",
    "joblib": "joblib",
    "onnx": "onnx",
    "pb": "savedmodel",
    "h5": "keras",
    "keras": "keras",
    "pt": "torch",
    "pth": "torch",
    "pmml": "pmml",
    "rds": "rds",
    "rdata": "rdata",
    "rda": "rdata",
}


def _preprocess_model_body(body: dict[str, Any]) -> dict[str, Any]:
    """Flatten nested convenience blocks into real Model column names.

    artifact   → artifact_path / artifact_format / artifact_size_bytes / artifact_sha256
    training   → training_dataset_hash + training_information JSONB
    governance → validation_status / validation_notes
    """
    flat = dict(body)

    # artifact block
    artifact = flat.pop("artifact", None)
    if isinstance(artifact, dict):
        raw_fmt = artifact.get("format", "")
        mapped_fmt = _EXT_TO_FORMAT.get(str(raw_fmt).lower(), raw_fmt or "custom")
        flat.setdefault("artifact_path", artifact.get("path"))
        flat.setdefault("artifact_format", mapped_fmt)
        flat.setdefault("artifact_size_bytes", artifact.get("size_bytes"))
        flat.setdefault("artifact_sha256", artifact.get("sha256"))

    # Also normalise the top-level artifact_format if sent as a raw extension
    if "artifact_format" in flat and flat["artifact_format"]:
        flat["artifact_format"] = _EXT_TO_FORMAT.get(
            str(flat["artifact_format"]).lower(), flat["artifact_format"]
        )

    # training block
    training = flat.pop("training", None)
    if isinstance(training, dict):
        flat.setdefault("training_dataset_hash", training.get("dataset_hash", ""))
        ti_extra = {k: v for k, v in training.items() if k != "dataset_hash"}
        if ti_extra:
            existing = flat.get("training_information") or {}
            flat["training_information"] = {**ti_extra, **existing}

    # governance block
    governance = flat.pop("governance", None)
    if isinstance(governance, dict):
        flat.setdefault(
            "validation_status", governance.get("validation_status", "pending")
        )
        flat.setdefault("validation_notes", governance.get("validation_notes"))

    # Ensure NOT NULL JSONB columns with defaults are never None
    for col, default in [
        ("config", {}),
        ("metrics", {}),
        ("inputs", []),
        ("outputs", []),
        ("packages", []),
        ("config_files", {}),
        ("training_information", {}),
        ("language", {}),
    ]:
        if flat.get(col) is None:
            flat[col] = default

    return flat


def _validate_model_payload_advisory(body: dict[str, Any]) -> None:
    """Advisory template validation — logs warnings but never raises."""
    try:
        validate_model_payload(body)
    except TemplateValidationError as e:
        logger.warning("Template validation warnings (save proceeds): %s", e)
    except ValueError as e:
        logger.debug("Template validation skipped: %s", e)


# Map of (path_prefix -> SQLAlchemy model). The prefix matches the
# table name, so the URL reads `/api/v1/<table>/...`.
_TABLES = [
    # --- auth + organization
    ("users", M.User, None),
    ("roles", M.Role, None),
    ("user_role", M.UserRole, None),
    ("permissions", M.Permission, None),
    ("role_permission", M.RolePermission, None),
    ("laboratories", M.Laboratory, None),
    ("laboratory_project", M.LaboratoryProject, None),
    ("laboratory_user", M.LaboratoryUser, None),
    ("projects", M.Project, None),
    ("refresh_tokens", M.RefreshToken, None),
    ("organizations", M.Organization, None),
    ("departments", M.Department, None),
    ("organizations_departments", M.OrganizationDepartment, None),
    ("department_laboratory", M.DepartmentLaboratory, None),
    # --- FermOps domain (8 new tables added 2026-04-30)
    ("alert_rules", M.AlertRule, None),
    ("drift_detectors", M.DriftDetector, None),
    ("phase_notes", M.PhaseNote, None),
    ("phase_overrides", M.PhaseOverride, None),
    ("access_requests", M.AccessRequest, None),
    ("audit_events", M.AuditEvent, None),
    ("instruments", M.Instrument, None),
    ("bioreactor_instruments", M.BioreactorInstrument, None),
    # --- bioprocess (Step 4)
    ("equipments", M.Equipment, None),
    ("sensors", M.Sensor, None),
    ("actuators", M.Actuator, None),
    ("sensor_readings", M.SensorReading, None),
    ("actuator_states", M.ActuatorState, None),
    ("runs", M.Run, None),
    ("experiments", M.Experiment, None),
    ("predictions", M.Prediction, None),
    ("annotations", M.Annotation, None),
    ("alerts", M.Alert, None),
    ("equipment_components", M.EquipmentComponent, None),
    ("experiments_equipments", M.ExperimentEquipment, None),
    # --- FermOps streaming + soft-sensor demo
    ("soft_sensors", M.SoftSensor, None),
    ("project_soft_sensors", M.ProjectSoftSensor, None),
    ("streaming_jobs", M.StreamingJob, None),
    # --- Model registry + federated learning (proposal 2026-05-22)
    # 4-tuple: (prefix, model, validator, preprocessor)
    ("models", M.Model, _validate_model_payload_advisory, _preprocess_model_body),
    ("project_models", M.ProjectModel, None, None),
    ("federations", M.Federation, None, None),
    ("federation_participants", M.FederationParticipant, None, None),
    ("model_contributions", M.ModelContribution, None, None),
    # --- Phase 4: drift monitoring
    ("experiment_drift_detectors", M.ExperimentDriftDetector, None, None),
    ("drift_results", M.DriftResult, None, None),
    # --- Phase 5: drift-detector packs (versioned catalog source)
    ("detector_packs", M.DetectorPack, None, None),
]

for entry in _TABLES:
    if len(entry) == 4:
        prefix, model, validator, preprocessor = entry
    elif len(entry) == 3:
        prefix, model, validator = entry
        preprocessor = None
    else:
        prefix, model = entry
        validator = preprocessor = None
    register_crud(
        router,
        model,
        prefix,
        read_perms=READ,
        write_perms=WRITE,
        tag=f"crud:{prefix}",
        create_validator=validator,
        create_preprocessor=preprocessor,
    )
