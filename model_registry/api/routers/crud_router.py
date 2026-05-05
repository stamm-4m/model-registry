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

from fastapi import APIRouter

from model_registry.api.scaffold import register_crud
from model_registry.api import models as M


router = APIRouter(prefix="/api/v1")

# Permission tuples for the v1 scaffold. Tighten per-table later.
READ = [
    "organization:read",
    "departments:read",
    "laboratory:read",
    "laboratories:read",
    "project:read",
    "experiments:read",
    "models:read",
    "users:read",
    "roles:read",
    "permissions:read",
    "department_laboratory:read",
    "organizations_departments:read",
    "laboratory_project:read",
    "laboratory_user:read",
    "user_role:read",
]
WRITE = [
    "organization:write", "organization:edit",
    "departments:write", "departments:edit",
    "laboratory:write", "laboratory:edit",
    "laboratories:write", "laboratories:edit",
    "project:write", "project:edit",
    "experiments:write", "experiments:edit",
    "models:write", "models:edit", "models:deploy",
    "users:write", "users:edit",
    "roles:write", "roles:edit",
    "permissions:write", "permissions:edit",
    "department_laboratory:write", "department_laboratory:edit",
    "organizations_departments:write", "organizations_departments:edit",
    "laboratory_project:write", "laboratory_project:edit",
    "laboratory_user:write", "laboratory_user:edit",
    "user_role:write", "user_role:edit",
]

# Map of (path_prefix -> SQLAlchemy model). The prefix matches the
# table name, so the URL reads `/api/v1/<table>/...`.
_TABLES = [
    # --- auth + organization
    ("users",                    M.User),
    ("roles",                    M.Role),
    ("user_role",                M.UserRole),
    ("permissions",              M.Permission),
    ("role_permission",          M.RolePermission),
    ("laboratories",             M.Laboratory),
    ("laboratory_project",       M.LaboratoryProject),
    ("laboratory_user",          M.LaboratoryUser),
    ("projects",                 M.Project),
    ("refresh_tokens",           M.RefreshToken),
    ("organizations",            M.Organization),
    ("departments",              M.Department),
    ("organizations_departments", M.OrganizationDepartment),
    ("department_laboratory",    M.DepartmentLaboratory),

    # --- FermOps domain (8 new tables added 2026-04-30)
    ("alert_rules",            M.AlertRule),
    ("drift_detectors",        M.DriftDetector),
    ("phase_notes",            M.PhaseNote),
    ("phase_overrides",        M.PhaseOverride),
    ("access_requests",        M.AccessRequest),
    ("audit_events",           M.AuditEvent),
    ("instruments",            M.Instrument),
    ("bioreactor_instruments", M.BioreactorInstrument),

    # --- bioprocess (Step 4)
    ("equipments",             M.Equipment),
    ("sensors",                M.Sensor),
    ("actuators",              M.Actuator),
    ("sensor_readings",        M.SensorReading),
    ("actuator_states",        M.ActuatorState),
    ("runs",                   M.Run),
    ("experiments",            M.Experiment),
    ("predictions",            M.Prediction),
    ("annotations",            M.Annotation),
    ("alerts",                 M.Alert),
    ("equipment_components",   M.EquipmentComponent),
    ("experiments_equipments", M.ExperimentEquipment),
]

for prefix, model in _TABLES:
    register_crud(router, model, prefix, read_perms=READ, write_perms=WRITE,
                  tag=f"crud:{prefix}")
