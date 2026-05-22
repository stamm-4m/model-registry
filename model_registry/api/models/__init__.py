# Existing auth + organization models
from .user import User
from .role import Role
from .user_role import UserRole
from .laboratory import Laboratory
from .laboratory_project import LaboratoryProject
from .laboratory_user import LaboratoryUser
from .project import Project
from .permission import Permission
from .role_permission import RolePermission
from .refresh_token import RefreshToken
from .organization import Organization
from .department import Department
from .organization_department import OrganizationDepartment
from .department_laboratory import DepartmentLaboratory

# FermOps domain models added 2026-04-30 (Step 3).
from .alert_rule import AlertRule
from .drift_detector import DriftDetector
from .phase_note import PhaseNote
from .phase_override import PhaseOverride
from .access_request import AccessRequest
from .audit_event import AuditEvent
from .instrument import Instrument
from .bioreactor_instrument import BioreactorInstrument

# Bioprocess models added 2026-04-30 (Step 4) so the CRUD scaffold
# can cover the rest of FermOps' read surface.
from .equipment import Equipment
from .sensor import Sensor
from .actuator import Actuator
from .sensor_reading import SensorReading
from .actuator_state import ActuatorState
from .run import Run
from .experiment import Experiment
from .prediction import Prediction
from .annotation import Annotation
from .alert import Alert
from .equipment_component import EquipmentComponent
from .experiment_equipment import ExperimentEquipment

# Soft-sensor / model registry (proposal landing 2026-05-22).
# Replaces the path-only soft_sensors table with structured rows.
# Federated-learning lineage modelled via Federation +
# FederationParticipant + ModelContribution.
from .model import Model
from .project_model import ProjectModel
from .federation import Federation
from .federation_participant import FederationParticipant
from .model_contribution import ModelContribution
from .department_laboratory import DepartmentLaboratory

# FermOps streaming + soft-sensor demo models. Files were already present in
# the develop tree but weren't registered here. Without these imports the
# CRUD scaffold can't see the tables and `/api/v1/streaming_jobs/` returns 404.
from .soft_sensor import SoftSensor
from .project_soft_sensor import ProjectSoftSensor
from .streaming_job import StreamingJob

__all__ = [
    # auth + organization
    "User", "Role", "UserRole",
    "Laboratory", "LaboratoryProject", "LaboratoryUser", "Project",
    "Permission", "RolePermission", "RefreshToken",
    "Organization", "Department", "DepartmentLaboratory",
    "OrganizationDepartment", "DepartmentLaboratory",
    # FermOps domain (Step 3)
    "AlertRule", "DriftDetector",
    "PhaseNote", "PhaseOverride",
    "AccessRequest", "AuditEvent",
    "Instrument", "BioreactorInstrument",
    # Bioprocess (Step 4)
    "Equipment", "Sensor", "Actuator",
    "SensorReading", "ActuatorState",
    "Run", "Experiment", "Prediction",
    "Annotation", "Alert",
    "EquipmentComponent", "ExperimentEquipment",
    # Streaming + soft-sensor demo (FermOps streamer)
    "SoftSensor", "ProjectSoftSensor", "StreamingJob",
    # Model registry + federated learning (proposal 2026-05-22)
    "Model", "ProjectModel",
    "Federation", "FederationParticipant", "ModelContribution",
]
