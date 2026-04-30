from model_registry.backend.models.soft_sensors import SoftSensor
from model_registry.backend.repositories.base_repository import BaseRepository

class SoftSensorsRepository(BaseRepository):
    def get_by_id(self, soft_sensor_id):
        return self.db.query(SoftSensor).filter(SoftSensor.id == soft_sensor_id).first()

    def get_all(self):
        return self.db.query(SoftSensor).all()

    def get_by_project(self, project_id):
        from model_registry.backend.models.project_soft_sensors import ProjectSoftSensor
        return (
            self.db.query(SoftSensor)
            .join(ProjectSoftSensor, ProjectSoftSensor.soft_sensor_id == SoftSensor.id)
            .filter(ProjectSoftSensor.project_id == project_id)
            .all()
        )
