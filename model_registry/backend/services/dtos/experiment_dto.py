"""DTOs for the Experiment domain."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExperimentDTO:
    id: str | None = None
    experiment_id: str | None = None
    project_id: str | None = None
    lab_id: str | None = None
    vessel_id: str | None = None
    name: str | None = None
    description: str | None = None
    lead: str | None = None
    status: str | None = None
    mode: str | None = None
    scale: str | None = None
    organism: str | None = None
    medium: str | None = None
    is_reference: bool | None = None
    final_titer: float | None = None
    tags: list[str] | None = None
    initial_conditions: dict[str, Any] | None = None
    set_points: dict[str, Any] | None = None
    start_time: str | None = None
    end_time: str | None = None
    created_at: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    _KNOWN = {
        "id",
        "experiment_id",
        "project_id",
        "lab_id",
        "vessel_id",
        "name",
        "description",
        "lead",
        "status",
        "mode",
        "scale",
        "organism",
        "medium",
        "is_reference",
        "final_titer",
        "tags",
        "initial_conditions",
        "set_points",
        "start_time",
        "end_time",
        "created_at",
    }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExperimentDTO":
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

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {k: getattr(self, k) for k in self._KNOWN}
        out.update(self.extra)
        return {k: v for k, v in out.items() if v is not None}
