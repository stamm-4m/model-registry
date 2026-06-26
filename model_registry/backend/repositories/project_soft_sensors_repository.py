from model_registry.backend.models.project_soft_sensors import ProjectSoftSensor
from model_registry.backend.repositories.base_repository import BaseRepository


class ProjectSoftSensorsRepository(BaseRepository):
    def get_by_project(self, project_id):
        return (
            self.db.query(ProjectSoftSensor)
            .filter(ProjectSoftSensor.project_id == project_id)
            .all()
        )

    def get_by_soft_sensor(self, soft_sensor_id):
        return (
            self.db.query(ProjectSoftSensor)
            .filter(ProjectSoftSensor.soft_sensor_id == soft_sensor_id)
            .all()
        )
