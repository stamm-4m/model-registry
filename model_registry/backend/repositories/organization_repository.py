from model_registry.backend.repositories.base_repository import BaseRepository
from model_registry.backend.models.organization import Organization
from model_registry.backend.models.organization_departament import OrganizationDepartment
from model_registry.backend.models.departament_laboratory import DepartmentLaboratory
from model_registry.backend.models.laboratory_user import LaboratoryUser
from sqlalchemy.sql import func


class OrganizationRepository(BaseRepository):

    def get_all(self):
        return self.db.query(Organization).all()

    def get_by_id(self, organization_id):
        return (
            self.db.query(Organization)
            .filter(Organization.id == organization_id)
            .first()
        )

    def create(self, name, location):
        organization = Organization(
            name=name,
            location=location
        )
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)
        return organization

    def delete(self, organization_id):
        org = self.get_by_id(organization_id)
        if org:
            self.db.delete(org)
            self.db.commit()
    def update(self, organization_id, name=None, location=None):
        org = self.get_by_id(organization_id)
        if not org:
            return None

        if name is not None:
            org.name = name
        if location is not None:
            org.location = location

        self.db.commit()
        self.db.refresh(org)
        return org
    def has_related_data(self, organization_id):

        #deptos related to the organization
        departments = (
            self.db.query(OrganizationDepartment.department_id)
            .filter(OrganizationDepartment.organization_id == organization_id)
            .all()
        )

        if not departments:
            return False

        dept_ids = [d[0] for d in departments]
        #laboratories related to those departments
        laboratories = (
            self.db.query(DepartmentLaboratory.laboratory_id)
            .filter(DepartmentLaboratory.department_id.in_(dept_ids))
            .all()
        )
        lab_ids = [l[0] for l in laboratories]
        #users related to those laboratories
        users = (
            self.db.query(LaboratoryUser)
            .filter(LaboratoryUser.laboratory_id.in_(lab_ids))
            .first()
        )

        return bool(users or departments)
    def get_dependency_counts(self, organization_id):
        dept_count = (
            self.db.query(func.count(OrganizationDepartment.department_id))
            .filter(OrganizationDepartment.organization_id == organization_id)
            .scalar()
        )

        # 🔹 obtener ids de departamentos
        dept_ids = (
            self.db.query(OrganizationDepartment.department_id)
            .filter(OrganizationDepartment.organization_id == organization_id)
            .all()
        )

        dept_ids = [d[0] for d in dept_ids]

        user_count = 0

        if dept_ids:
            lab_count = (
                self.db.query(func.count(DepartmentLaboratory.laboratory_id))
                .filter(DepartmentLaboratory.department_id.in_(dept_ids))
                .scalar()
            )
        if lab_count:
            lab_ids = (
                self.db.query(DepartmentLaboratory.laboratory_id)
                .filter(DepartmentLaboratory.department_id.in_(dept_ids))
                .all()
            )

            lab_ids = [l[0] for l in lab_ids]

            user_count = (
                self.db.query(func.count(LaboratoryUser.user_id))
                .filter(LaboratoryUser.laboratory_id.in_(lab_ids))
                .scalar()
            )

        return {
            "departments": dept_count or 0,
            "laboratories": lab_count or 0,
            "users": user_count or 0
        }