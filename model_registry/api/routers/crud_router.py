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
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException

from model_registry.api.scaffold import register_crud
from model_registry.api import models as M
from model_registry.api.core.constants.permissions import PermissionManager
from model_registry.backend.services.template_validator import (
    validate_model_payload,
    TemplateValidationError,
)


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")


# Permission sets for CRUD operations. These are broad and can be tightened
def get_read_perms():
    # Can be customized to get read permissions based on your naming convention
    return [p.name for p in PermissionManager.all() if ":read" in p.name]

def get_write_perms():
    # Can be customized to get write permissions based on your naming convention
    return [p.name for p in PermissionManager.all() if any(s in p.name for s in (":write", ":edit", ":deploy"))]

READ = get_read_perms()
WRITE = get_write_perms()


def _validate_model_payload(body: Dict[str, Any]) -> None:
    """Validator for Model table create operations.

    Raises HTTPException with validation errors.
    """
    try:
        validate_model_payload(body)
    except TemplateValidationError as e:
        logger.warning(f"Model template validation failed: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Model template validation failed: {'; '.join(e.errors)}"
        )
    except ValueError as e:
        logger.warning(f"Invalid model payload: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Map of (path_prefix -> SQLAlchemy model). The prefix matches the
# table name, so the URL reads `/api/v1/<table>/...`.
_TABLES = [
    # --- auth + organization
    ("users",                    M.User,                       None),
    ("roles",                    M.Role,                       None),
    ("user_role",                M.UserRole,                   None),
    ("permissions",              M.Permission,                 None),
    ("role_permission",          M.RolePermission,             None),
    ("laboratories",             M.Laboratory,                 None),
    ("laboratory_project",       M.LaboratoryProject,          None),
    ("laboratory_user",          M.LaboratoryUser,             None),
    ("projects",                 M.Project,                    None),
    ("refresh_tokens",           M.RefreshToken,               None),
    ("organizations",            M.Organization,               None),
    ("departments",              M.Department,                 None),
    ("organizations_departments", M.OrganizationDepartment,    None),
    ("department_laboratory",    M.DepartmentLaboratory,       None),

    # --- FermOps domain (8 new tables added 2026-04-30)
    ("alert_rules",            M.AlertRule,                   None),
    ("drift_detectors",        M.DriftDetector,               None),
    ("phase_notes",            M.PhaseNote,                   None),
    ("phase_overrides",        M.PhaseOverride,               None),
    ("access_requests",        M.AccessRequest,               None),
    ("audit_events",           M.AuditEvent,                  None),
    ("instruments",            M.Instrument,                  None),
    ("bioreactor_instruments", M.BioreactorInstrument,        None),

    # --- bioprocess (Step 4)
    ("equipments",             M.Equipment,                   None),
    ("sensors",                M.Sensor,                      None),
    ("actuators",              M.Actuator,                    None),
    ("sensor_readings",        M.SensorReading,               None),
    ("actuator_states",        M.ActuatorState,               None),
    ("runs",                   M.Run,                         None),
    ("experiments",            M.Experiment,                  None),
    ("predictions",            M.Prediction,                  None),
    ("annotations",            M.Annotation,                  None),
    ("alerts",                 M.Alert,                       None),
    ("equipment_components",   M.EquipmentComponent,          None),
    ("experiments_equipments", M.ExperimentEquipment,         None),

    # --- FermOps streaming + soft-sensor demo
    ("soft_sensors",           M.SoftSensor,                  None),
    ("project_soft_sensors",   M.ProjectSoftSensor,           None),
    ("streaming_jobs",         M.StreamingJob,                None),

    # --- Model registry + federated learning (proposal 2026-05-22)
    # Use template validator for models table
    ("models",                    M.Model,                      _validate_model_payload),
    ("project_models",            M.ProjectModel,               None),
    ("federations",               M.Federation,                 None),
    ("federation_participants",   M.FederationParticipant,      None),
    ("model_contributions",       M.ModelContribution,          None),
]

for entry in _TABLES:
    if len(entry) == 3:
        prefix, model, validator = entry
    else:
        prefix, model = entry
        validator = None
    register_crud(router, model, prefix, read_perms=READ, write_perms=WRITE,
                  tag=f"crud:{prefix}", create_validator=validator)

