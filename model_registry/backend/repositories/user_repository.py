import uuid

from model_registry.backend.models.department import Department
from model_registry.backend.models.departament_laboratory import DepartmentLaboratory
from model_registry.backend.models.user_role import UserRole
from model_registry.backend.repositories.base_repository import BaseRepository
from model_registry.backend.models.users   import User
from model_registry.backend.models.laboratory_user import LaboratoryUser
from model_registry.backend.models.laboratory import Laboratory
from model_registry.backend.models.role import Role

from sqlalchemy.sql import func

import logging
logger = logging.getLogger(__name__)

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
        if not isinstance(user_id, uuid.UUID):
            user_id = uuid.UUID(str(user_id))
        result = (
            self.db.query(UserRole)
            .filter(UserRole.user_id == user_id)
            .all()
        )
        return result
    
    def delete_roles_by_user(self, user_id, permission_id=None, real_resource_id=None):
        query = self.db.query(UserRole).filter(UserRole.user_id == user_id)
        if permission_id is not None:
            query = query.filter(UserRole.permission_id == permission_id)
        if real_resource_id is not None:
            query = query.filter(UserRole.real_resource_id == real_resource_id)
        query.delete()
        self.db.commit()

    def create_add_role_to_user(self, user_id, role_id, permission_id=None, real_resource_id=None):
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            permission_id=permission_id,
            real_resource_id=real_resource_id
        )
        self.db.add(user_role)
        self.db.commit()
    
    def get_all_users_with_department_and_laboratory(self):
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
    def assign_user_roles(self, user_id, role_ids):
        """Asigna solo los roles seleccionados al usuario (roles generales)."""
        self.delete_roles_by_user(user_id, permission_id=None, real_resource_id=None)
        for role_id in role_ids:
            self.create_add_role_to_user(user_id, role_id)
        self.db.commit()
        self.close()


    def assign_user_model_roles(self, user_id, role_ids, model_id):
        """Asigna solo los roles seleccionados para un modelo específico."""
        self.delete_roles_by_user(user_id, permission_id=None, real_resource_id=model_id)
        for role_id in role_ids:
            self.create_add_role_to_user(user_id, role_id, real_resource_id=model_id)
        self.db.commit()
        self.close()

    def assign_user_model_permissions(self, user_id, role_ids, permission_ids, model_id):
        """
        Asigna permisos sobre un modelo específico, usando los roles generales del usuario como base.
        Para cada permiso, busca el primer rol general del usuario que lo concede y crea la fila en UserRole con el rol general, el permiso y el model_id como real_resource_id.
        """
        self.delete_roles_by_user(user_id, permission_id=None, real_resource_id=model_id)
        logger.info(f"Asignando permisos sobre modelo {model_id} para user {user_id} con roles generales {role_ids}")
        for perm_id in permission_ids:
            if role_ids:
                self.create_add_role_to_user(user_id, role_ids[0], permission_id=perm_id, real_resource_id=model_id)
            else:
                logger.warning(f"No se encontró role_id para permiso {perm_id} entre los roles generales del usuario")
        self.db.commit()
        self.close()
