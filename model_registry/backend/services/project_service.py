from uuid import UUID
from model_registry.backend.repositories.project_repository import ProjectRepository
from model_registry.backend.models.project import Project
from model_registry.backend.core.exceptions import ProjectInUseException
from model_registry.backend.models.laboratory_project import LaboratoryProject
from model_registry.backend.models.laboratory_user import LaboratoryUser

class ProjectService:

    def __init__(self):
        self.repo = ProjectRepository()
        self.db = self.repo.db

    # 🔹 CREATE
    def create_project(self, name, description=None, project_id=None):
        project = Project(
            name=name,
            description=description,
            project_id=project_id
        )
        return self.repo.create(project)

    # 🔹 UPDATE
    def update_project(self, project_id, name=None, description=None, external_id=None):
        return self.repo.update(project_id, name, description, external_id)

    # 🔹 ASSIGN LAB
    def assign_project_to_lab(self, project_id, lab_id):
        return self.repo.assign_to_lab(project_id, lab_id)

    # 🔹 UPDATE LAB
    def update_project_lab(self, project_id, lab_id):
        return self.repo.update_project_lab(project_id, lab_id)

    # 🔹 GET FULL PROJECT
    def get_full_project(self, project_id):
        result = self.repo.get_full_project(UUID(project_id))

        if not result:
            return None, None, None, None

        return result  # (project, lab, dept, org)

    # 🔹 GET ALL
    def get_all_projects(self):
        return self.repo.get_all()

    # 🔹 DELETE
    def delete_project(self, project_id):
        # Ensure project_id is UUID
        project_uuid = UUID(str(project_id))
        try:
            self.repo.delete_if_no_lab_users(project_uuid)
        except ProjectInUseException as e:
            raise ProjectInUseException(str(e))
        except Exception as e:
            raise Exception(f"Error deleting project: {str(e)}")
