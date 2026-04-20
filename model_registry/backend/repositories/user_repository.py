from model_registry.backend.models.user_role import UserRole
from model_registry.backend.repositories.base_repository import BaseRepository
from model_registry.backend.models.users   import User
from model_registry.backend.models.departament_user import DepartmentUser
from model_registry.backend.models.departament import Department
from sqlalchemy.sql import func


class UserRepository(BaseRepository):
    def get_all(self):
        return (
            self.db.query(
                User,
                Department.name.label("organization_name")
            )
            .join(DepartmentUser, DepartmentUser.user_id == User.id)
            .join(Department, Department.id == DepartmentUser.department_id)
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