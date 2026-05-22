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
from model_registry.api.core.constants.permissions import PermissionManager


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

    # --- FermOps streaming + soft-sensor demo
    ("soft_sensors",           M.SoftSensor),
    ("project_soft_sensors",   M.ProjectSoftSensor),
    ("streaming_jobs",         M.StreamingJob),

    # --- Model registry + federated learning (proposal 2026-05-22)
    ("models",                    M.Model),
    ("project_models",            M.ProjectModel),
    ("federations",               M.Federation),
    ("federation_participants",   M.FederationParticipant),
    ("model_contributions",       M.ModelContribution),
]

for prefix, model in _TABLES:
    register_crud(router, model, prefix, read_perms=READ, write_perms=WRITE,
                  tag=f"crud:{prefix}")
