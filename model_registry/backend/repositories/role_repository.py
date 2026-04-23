from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

from model_registry.backend.models.permission import Permission
from model_registry.backend.models.role_permission import RolePermission
from model_registry.backend.models.role import Role
from model_registry.backend.repositories.base_repository import BaseRepository

class RoleRepository(BaseRepository):
    def get_all(self) -> List[Role]:
        return self.db.query(Role).all()

    def get_by_id(self, role_id) -> Optional[Role]:
        return self.db.query(Role).filter(Role.id == role_id).first()

    def create(self, name, description=None) -> Role:
        role = Role(name=name, description=description)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def delete(self, role_id):
        role = self.get_by_id(role_id)
        if role:
            self.db.delete(role)
            self.db.commit()
    # get permissions by role id from role_permissions table join with permissions table to get permission names        
    def get_permissions_by_role_ids(self, role_ids):
        return (
            self.db.query(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .filter(RolePermission.role_id.in_(role_ids))
            .all()
        )