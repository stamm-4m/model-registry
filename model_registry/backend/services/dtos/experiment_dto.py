"""DTOs for the Experiment domain."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExperimentDTO:
    id: Optional[str] = None
    experiment_id: Optional[str] = None
    project_id: Optional[str] = None
    lab_id: Optional[str] = None
    vessel_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    lead: Optional[str] = None
    status: Optional[str] = None
    mode: Optional[str] = None
    scale: Optional[str] = None
    organism: Optional[str] = None
    medium: Optional[str] = None
    is_reference: Optional[bool] = None
    final_titer: Optional[float] = None
    tags: Optional[List[str]] = None
    initial_conditions: Optional[Dict[str, Any]] = None
    set_points: Optional[Dict[str, Any]] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    created_at: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    _KNOWN = {
        "id", "experiment_id", "project_id", "lab_id", "vessel_id",
        "name", "description", "lead", "status", "mode", "scale",
        "organism", "medium", "is_reference", "final_titer", "tags",
        "initial_conditions", "set_points", "start_time", "end_time",
        "created_at",
    }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperimentDTO":
        if not data:
            return cls()
        extras = {k: v for k, v in data.items() if k not in cls._KNOWN}
        return cls(
            id=data.get("id"),
            experiment_id=data.get("experiment_id"),
            project_id=data.get("project_id"),
            lab_id=data.get("lab_id"),
            vessel_id=data.get("vessel_id"),
            name=data.get("name"),
            description=data.get("description"),
            lead=data.get("lead"),
            status=data.get("status"),
            mode=data.get("mode"),
            scale=data.get("scale"),
            organism=data.get("organism"),
            medium=data.get("medium"),
            is_reference=data.get("is_reference"),
            final_titer=data.get("final_titer"),
            tags=data.get("tags"),
            initial_conditions=data.get("initial_conditions"),
            set_points=data.get("set_points"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            created_at=data.get("created_at"),
            extra=extras,
        )

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {k: getattr(self, k) for k in self._KNOWN}
        out.update(self.extra)
        return {k: v for k, v in out.items() if v is not None}
