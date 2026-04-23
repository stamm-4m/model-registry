from model_registry.backend.repositories.user_repository import UserRepository
from model_registry.backend.core.exceptions import UserHasRolesException, UserEmailAlreadyExistsException
from model_registry.backend.models.users import User
from model_registry.backend.models.laboratory_user import LaboratoryUser
from model_registry.backend.utils.security import hash_password
from sqlalchemy.exc import IntegrityError


import uuid


class UserService:

    def __init__(self):
        self.user_repo = UserRepository()
        self.db = self.user_repo.db  
        
    def create_user(self, name, email, password, lab_id):

        try:
            password_hash = hash_password(password) if password else None

            user = User(
                full_name=name,
                email=email,
                password_hash=password_hash
            )

            self.db.add(user)
            self.db.flush()

            rel = LaboratoryUser(
                user_id=user.id,
                laboratory_id=uuid.UUID(lab_id)
            )

            self.db.add(rel)

            self.db.commit()
            self.db.refresh(user)

            return user

        except IntegrityError as e:
            self.db.rollback()

            if "users_email_key" in str(e.orig):
                raise UserEmailAlreadyExistsException(email)

            raise

        finally:
            self.user_repo.close()

    def get_user(self, user_id):
        user = self.user_repo.get_by_id(user_id)
        self.user_repo.close()
        return user

    def get_all_users(self):
        users = self.user_repo.get_all()
        self.user_repo.close()
        return users

    def delete_user(self, user_id):
        try:
            roles_count = self.user_repo.count_user_roles(user_id)

            if roles_count > 0:
                raise UserHasRolesException(roles_count)

            self.user_repo.delete(user_id)
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

        finally:
            self.user_repo.close()

    def update_user(self, user_id, name, email, password, lab_id):

        user_id = uuid.UUID(user_id)

        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            self.user_repo.close()
            return None

        user.full_name = name
        user.email = email

        if password:
            user.password_hash = hash_password(password)
        # if exists, update lab association
        self.db.query(LaboratoryUser).filter(
            LaboratoryUser.user_id == user_id
        ).update({
            "laboratory_id": uuid.UUID(lab_id)
        })
        #else, create new association
        if not self.db.query(LaboratoryUser).filter(
            LaboratoryUser.user_id == user_id
        ).first():
            rel = LaboratoryUser(
                user_id=user_id,
                laboratory_id=uuid.UUID(lab_id)
            )
            self.db.add(rel)

        self.db.commit()
        self.user_repo.close()

        return user

    def get_user_with_laboratory(self, user_id):

        user_id = uuid.UUID(user_id)

        result = (
            self.db.query(User, LaboratoryUser.laboratory_id)
            .join(LaboratoryUser, LaboratoryUser.user_id == User.id)
            .filter(User.id == user_id)
            .first()
        )

        self.user_repo.close()

        if result:
            return result

        return None, None
    
    def get_lab_id_by_user_id(self, user_id):
        user_id = uuid.UUID(user_id)
        lab_id = self.user_repo.get_lab_id_by_user_id(user_id)
        return lab_id
    
    def get_dept_id_by_user_id(self, user_id):
        user_id = uuid.UUID(user_id)
        dept_id = self.user_repo.get_dept_id_by_user_id(user_id)
        return dept_id
    
    def get_all_roles_by_user_id(self, user_id):
        user_id = uuid.UUID(user_id)
        roles = self.user_repo.get_all_roles_by_user_id(user_id)
        return roles
    
    def assign_roles_to_user(self, user_id, role_ids, laboratory_id=None):
        
        self.user_repo.delete_roles_by_user(user_id)

        for role_id in role_ids:
            self.user_repo.create_add_role_to_user(user_id, role_id, laboratory_id)