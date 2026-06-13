from model_registry.backend.repositories.soft_sensors_repository import SoftSensorsRepository

class SoftSensorsService:
    def __init__(self):
        self.repo = SoftSensorsRepository()
        self.db = self.repo.db

    def get_by_id(self, soft_sensor_id):
        return self.repo.get_by_id(soft_sensor_id)

    def get_all(self):
        return self.repo.get_all()

    def get_by_project(self, project_id):
        return self.repo.get_by_project(project_id)
