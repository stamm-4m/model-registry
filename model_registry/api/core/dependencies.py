from typing import List

from requests import Session
from model_registry.api.core.database import get_db
from model_registry.api.core.security import get_current_user
from model_registry.api.models.laboratory_project import LaboratoryProject
from fastapi import Depends, HTTPException
import logging

from model_registry.api.models.project import Project
from model_registry.api.models.role_permission import RolePermission
from model_registry.api.models.permission import Permission as PermissionModel
from model_registry.api.models.resource import Resource

logger = logging.getLogger(__name__)

# New dependency for resource-based permission check
def require_permission_resource(permission_name: str, resource_name: str):
    def checker(user=Depends(get_current_user), db: Session = Depends(get_db)):
        # Find resource by name
        resource = db.query(Resource).filter(Resource.name == resource_name).first()
        if not resource:
            raise HTTPException(403, f"Resource '{resource_name}' not found")
        # Find permission by name
        permission = db.query(PermissionModel).filter(PermissionModel.name == permission_name).first()
        if not permission:
            raise HTTPException(403, f"Permission '{permission_name}' not found")
        # Check if user has a role with this permission and resource
        has_permission = False
        for ur in user.roles:
            for rp in ur.role.permissions:
                if rp.permission_id == permission.id and rp.resource_id == resource.id:
                    has_permission = True
                    break
            if has_permission:
                break
        if not has_permission:
            raise HTTPException(403, f"Not enough permissions for resource '{resource_name}' and permission '{permission_name}'")
        return user
    return checker