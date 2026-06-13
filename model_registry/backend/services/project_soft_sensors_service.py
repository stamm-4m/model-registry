from model_registry.backend.repositories.project_soft_sensors_repository import ProjectSoftSensorsRepository

class ProjectSoftSensorsService:
    def __init__(self):
        self.repo = ProjectSoftSensorsRepository()
        self.db = self.repo.db

    def get_by_project(self, project_id):
        return self.repo.get_by_project(project_id)

    def get_by_soft_sensor(self, soft_sensor_id):
        return self.repo.get_by_soft_sensor(soft_sensor_id)
