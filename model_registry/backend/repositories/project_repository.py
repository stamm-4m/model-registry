from model_registry.backend.models.project import Project
from model_registry.backend.models.laboratory_project import LaboratoryProject
from model_registry.backend.repositories.base_repository import BaseRepository
from model_registry.backend.models.laboratory import Laboratory
from model_registry.backend.models.department import Department
from model_registry.backend.models.organization import Organization

class ProjectRepository(BaseRepository):

    
    def create(self, project: Project):
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update(self, project_id, name=None, description=None):
        project = self.db.query(Project).filter(Project.id == project_id).first()

        if not project:
            return None

        if name:
            project.name = name
        if description:
            project.description = description

        self.db.commit()
        self.db.refresh(project)
        return project

    def get_by_id(self, project_id):
        return self.db.query(Project).filter(Project.id == project_id).first()

    def get_all(self):
        return self.db.query(Project).all()

    def delete(self, project_id):
        project = self.get_by_id(project_id)
        if project:
            self.db.delete(project)
            self.db.commit()

    def assign_to_lab(self, project_id, lab_id):
        relation = LaboratoryProject(
            project_id=project_id,
            laboratory_id=lab_id
        )
        self.db.add(relation)
        self.db.commit()
        return relation

    def update_project_lab(self, project_id, lab_id):
        rel = (
            self.db.query(LaboratoryProject)
            .filter(LaboratoryProject.project_id == project_id)
            .first()
        )

        if rel:
            rel.laboratory_id = lab_id
        else:
            rel = LaboratoryProject(
                project_id=project_id,
                laboratory_id=lab_id
            )
            self.db.add(rel)

        self.db.commit()
        return rel

    def get_full_project(self, project_id):
    

        result = (
            self.db.query(Project, Laboratory, Department, Organization)
            .join(LaboratoryProject, LaboratoryProject.project_id == Project.id)
            .join(Laboratory, Laboratory.id == LaboratoryProject.laboratory_id)
            .join(Department, Department.id == Laboratory.department_id)
            .join(Organization, Organization.id == Department.organization_id)
            .filter(Project.id == project_id)
            .first()
        )

        return result  # (project, lab, dept, org)