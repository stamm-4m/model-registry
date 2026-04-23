from model_registry.backend.repositories.base_repository import BaseRepository
from model_registry.backend.models.organization_departament import OrganizationDepartment
from model_registry.backend.models.department import Department
from model_registry.backend.models.organization import Organization

class DepartmentRepository(BaseRepository):
    def get_with_organization(self, dept_id):
        result = (
            self.db.query(
                Department,
                OrganizationDepartment.organization_id
            )
            .join(OrganizationDepartment, OrganizationDepartment.department_id == Department.id)
            .filter(Department.id == dept_id)
            .first()
        )

        if result:
            dept, org_id = result
            return dept, org_id

        return None, None
    
    def get_all(self):
        return (
            self.db.query(
                Department,
                Organization.name.label("organization_name")
            )
            .join(OrganizationDepartment, OrganizationDepartment.department_id == Department.id)
            .join(Organization, Organization.id == OrganizationDepartment.organization_id)
            .all()
        )

    def get_by_id(self, department_id):
        return (
            self.db.query(Department)
            .filter(Department.id == department_id)
            .first()
        )

    def create(self, name, organization_id):
        department = Department(name=name)
        self.db.add(department)
        self.db.commit()
        self.db.refresh(department)

        org_dept = OrganizationDepartment(
            organization_id=organization_id,
            department_id=department.id
        )
        self.db.add(org_dept)
        self.db.commit()

        return department

    def delete(self, department_id):
        dept = self.get_by_id(department_id)
        if dept:
            self.db.delete(dept)
            self.db.commit()

    def update(self, department_id, name=None):
        dept = self.get_by_id(department_id)
        if not dept:
            return None

        if name is not None:
            dept.name = name

        self.db.commit()
        self.db.refresh(dept)
        return dept
