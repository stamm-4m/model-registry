from model_registry.backend.models.departament_laboratory import DepartmentLaboratory
from model_registry.backend.models.laboratory_user import LaboratoryUser
from model_registry.backend.models.organization_departament import OrganizationDepartment
from model_registry.backend.models.project import Project
from model_registry.backend.models.laboratory_project import LaboratoryProject
from model_registry.backend.repositories.base_repository import BaseRepository
from model_registry.backend.models.laboratory import Laboratory
from model_registry.backend.models.department import Department
from model_registry.backend.models.organization import Organization
from model_registry.backend.core.exceptions import ProjectInUseException

class ProjectRepository(BaseRepository):

    
    def create(self, project: Project):
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update(self, project_id, name=None, description=None, external_id=None):
        project = self.db.query(Project).filter(Project.id == project_id).first()

        if not project:
            return None

        if name:
            project.name = name
        if description:
            project.description = description
        if external_id:
            project.external_id = external_id

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

    def delete_if_no_lab_users(self, project_id):
        # Get all laboratory assignments for this project
        lab_projects = self.db.query(LaboratoryProject).filter(LaboratoryProject.project_id == project_id).all()
        for lab_proj in lab_projects:
            # For each lab, check if there are users assigned
            user_count = self.db.query(LaboratoryUser).filter(LaboratoryUser.laboratory_id == lab_proj.laboratory_id).count()
            if user_count > 0:
                raise ProjectInUseException(f"Cannot delete project: laboratory has assigned users.")
        # If no users, delete all LaboratoryProject relations
        for lab_proj in lab_projects:
            self.db.delete(lab_proj)
        # Now delete the project itself
        project = self.get_by_id(project_id)
        if project:
            self.db.delete(project)
            self.db.commit()
        else:
            raise Exception("Project not found.")

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
            .join(DepartmentLaboratory, DepartmentLaboratory.laboratory_id == LaboratoryProject.laboratory_id)
            .join(Department, Department.id == DepartmentLaboratory.department_id)
            .join(OrganizationDepartment, OrganizationDepartment.department_id == Department.id)
            .join(Organization, Organization.id == OrganizationDepartment.organization_id)
            .filter(Project.id == project_id)
            .first()
        )

        return result  # (project, lab, dept, org)