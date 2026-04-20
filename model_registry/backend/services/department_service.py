from model_registry.backend.repositories.department_repository import DepartmentRepository
from model_registry.backend.core.exceptions import OrganizationInUseException
from model_registry.backend.models.organization_departament import OrganizationDepartment
from model_registry.backend.models.departament import Department
from model_registry.backend.models.departament_user import DepartmentUser


class DepartmentService:

    def create_department(self, name, organization_id):
        repo = DepartmentRepository()
        dept = repo.create(name, organization_id)
        repo.close()
        return dept
    def get_department_all(self):
        repo = DepartmentRepository()
        depts = repo.get_all()
        repo.close()
        return depts
    def get_department_with_org(self, department_id):
        repo = DepartmentRepository()
        result = repo.get_with_organization(department_id)
        repo.close()
        return result
    def update_department(self, department_id, name=None, organization_id=None):
        repo = DepartmentRepository()
        dept = repo.get_by_id(department_id)
        if not dept:
            repo.close()
            return None

        if name is not None:
            dept.name = name
        if organization_id is not None:
            # Update the organization association
            org_dept = (
                repo.db.query(OrganizationDepartment)
                .filter(OrganizationDepartment.department_id == department_id)
                .first()
            )
            if org_dept:
                org_dept.organization_id = organization_id

        repo.db.commit()
        repo.db.refresh(dept)
        repo.close()
        return dept
    
    def delete_department(self, department_id):
        repo = DepartmentRepository()

        users_count = (
            repo.db.query(DepartmentUser)
            .filter(DepartmentUser.department_id == department_id)
            .count()
        )

        if users_count > 0:
            repo.close()
            raise OrganizationInUseException(users=users_count)

        result = repo.delete(department_id)
        repo.close()

        return result
