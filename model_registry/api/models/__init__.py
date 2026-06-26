# Existing auth + organization models
from .access_request import AccessRequest
from .actuator import Actuator
from .actuator_state import ActuatorState
from .alert import Alert

# FermOps domain models added 2026-04-30 (Step 3).
from .alert_rule import AlertRule
from .annotation import Annotation
from .audit_event import AuditEvent
from .bioreactor_instrument import BioreactorInstrument
from .department import Department
from .department_laboratory import DepartmentLaboratory

# --- Phase 5: drift-detector packs (versioned, uploadable catalog source)
from .detector_pack import DetectorPack
from .drift_detector import DriftDetector
from .drift_result import DriftResult

# Bioprocess models added 2026-04-30 (Step 4) so the CRUD scaffold
# can cover the rest of FermOps' read surface.
from .equipment import Equipment
from .equipment_component import EquipmentComponent
from .experiment import Experiment

# --- Phase 4: drift monitoring (selection + results)
from .experiment_drift_detector import ExperimentDriftDetector
from .experiment_equipment import ExperimentEquipment
from .federation import Federation
from .federation_participant import FederationParticipant
from .instrument import Instrument
from .laboratory import Laboratory
from .laboratory_project import LaboratoryProject
from .laboratory_user import LaboratoryUser

# Soft-sensor / model registry (proposal landing 2026-05-22).
# Replaces the path-only soft_sensors table with structured rows.
# Federated-learning lineage modelled via Federation +
# FederationParticipant + ModelContribution.
from .model import Model
from .model_contribution import ModelContribution
from .organization import Organization
from .organization_department import OrganizationDepartment
from .permission import Permission
from .phase_note import PhaseNote
from .phase_override import PhaseOverride
from .prediction import Prediction
from .project import Project
from .project_model import ProjectModel
from .project_soft_sensor import ProjectSoftSensor
from .refresh_token import RefreshToken
from .role import Role
from .role_permission import RolePermission
from .run import Run
from .sensor import Sensor
from .sensor_reading import SensorReading

# FermOps streaming + soft-sensor demo models. Files were already present in
# the develop tree but weren't registered here. Without these imports the
# CRUD scaffold can't see the tables and `/api/v1/streaming_jobs/` returns 404.
from .soft_sensor import SoftSensor
from .streaming_job import StreamingJob
from .user import User
from .user_role import UserRole

__all__ = [
    # auth + organization
    "User",
    "Role",
    "UserRole",
    "Laboratory",
    "LaboratoryProject",
    "LaboratoryUser",
    "Project",
    "Permission",
    "RolePermission",
    "RefreshToken",
    "Organization",
    "Department",
    "DepartmentLaboratory",
    "OrganizationDepartment",
    "DepartmentLaboratory",
    # FermOps domain (Step 3)
    "AlertRule",
    "DriftDetector",
    "PhaseNote",
    "PhaseOverride",
    "AccessRequest",
    "AuditEvent",
    "Instrument",
    "BioreactorInstrument",
    # Bioprocess (Step 4)
    "Equipment",
    "Sensor",
    "Actuator",
    "SensorReading",
    "ActuatorState",
    "Run",
    "Experiment",
    "Prediction",
    "Annotation",
    "Alert",
    "EquipmentComponent",
    "ExperimentEquipment",
    # Streaming + soft-sensor demo (FermOps streamer)
    "SoftSensor",
    "ProjectSoftSensor",
    "StreamingJob",
    # Model registry + federated learning (proposal 2026-05-22)
    "Model",
    "ProjectModel",
    "Federation",
    "FederationParticipant",
    "ModelContribution",
    # Drift-detector packs (Phase 5)
    "ExperimentDriftDetector",
    "DriftResult",
    "DetectorPack",
]
