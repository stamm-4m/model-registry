from model_registry.backend.models.department import Department
from model_registry.backend.models.departament_laboratory import DepartmentLaboratory
from model_registry.backend.models.user_role import UserRole
from model_registry.backend.repositories.base_repository import BaseRepository
from model_registry.backend.models.users   import User
from model_registry.backend.models.laboratory_user import LaboratoryUser
from model_registry.backend.models.laboratory import Laboratory
from sqlalchemy.sql import func


class UserRepository(BaseRepository):
    def get_all(self):
        return (
        self.db.query(
            User,
            Laboratory.name.label("laboratory_name"),
            Department.name.label("department_name")
        )
        .outerjoin(LaboratoryUser, LaboratoryUser.user_id == User.id)
        .outerjoin(Laboratory, Laboratory.id == LaboratoryUser.laboratory_id)
        .outerjoin(DepartmentLaboratory, DepartmentLaboratory.laboratory_id == Laboratory.id)
        .outerjoin(Department, Department.id == DepartmentLaboratory.department_id)
        .all()
    )
    def get_by_id(self, user_id):
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def create(self, full_name, email, password_hash=None, external_provider=None, external_id=None):
        user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            external_provider=external_provider,
            external_id=external_id
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id):
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
    
    def count_user_roles(self, user_id):
        return (
            self.db.query(UserRole)
            .filter(UserRole.user_id == user_id)
            .count()
        )
    def get_dept_id_by_user_id(self, user_id):
        result = (
            self.db.query(Department.id)
            .join(DepartmentLaboratory, DepartmentLaboratory.department_id == Department.id)
            .join(Laboratory, Laboratory.id == DepartmentLaboratory.laboratory_id)
            .join(LaboratoryUser, LaboratoryUser.laboratory_id == Laboratory.id)
            .filter(LaboratoryUser.user_id == user_id)
            .first()
        )
        return result[0] if result else None
    
    def get_lab_id_by_user_id(self, user_id):
        result = (
            self.db.query(Laboratory.id)
            .join(LaboratoryUser, LaboratoryUser.laboratory_id == Laboratory.id)
            .filter(LaboratoryUser.user_id == user_id)
            .first()
        )
        return result[0] if result else None
    # get all roles by user id from user_role table join with role table to get role names
    def get_all_roles_by_user_id(self, user_id):
        return (
            self.db.query(UserRole)
            .filter(UserRole.user_id == user_id)
            .all()
        )
    def delete_roles_by_user(self, user_id):
        self.db.query(UserRole).filter(UserRole.user_id == user_id).delete()
        self.db.commit()
    def create_add_role_to_user(self, user_id, role_id, laboratory_id):
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            laboratory_id=laboratory_id,
            updated_at=func.now(),
        )
        self.db.add(user_role)
        self.db.commit()