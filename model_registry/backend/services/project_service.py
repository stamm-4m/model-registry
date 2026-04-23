from uuid import UUID
from model_registry.backend.repositories.project_repository import ProjectRepository
from model_registry.backend.models.project import Project


class ProjectService:

    def __init__(self):
        self.repo = ProjectRepository(self.db)
        self.db = self.repo.db

    # 🔹 CREATE
    def create_project(self, name, description=None):
        project = Project(
            name=name,
            description=description
        )
        return self.repo.create(project)

    # 🔹 UPDATE
    def update_project(self, project_id, name=None, description=None):
        return self.repo.update(project_id, name, description)

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
        return self.repo.delete(UUID(project_id))

    def close(self):
        self.db.close()