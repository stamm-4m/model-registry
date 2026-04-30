from typing import List

from requests import Session
from model_registry.api.core.database import get_db
from model_registry.api.core.security import get_current_user
from fastapi import Depends, HTTPException
import logging

from model_registry.api.models.permission import Permission as PermissionModel
from model_registry.api.models.resource import Resource

logger = logging.getLogger(__name__)

# Dependency for resource-based permission check
def require_permission_resource(permission_name: str, resource_name: str):
    def checker(user=Depends(get_current_user), db: Session = Depends(get_db)):
        # Find resource by name
        resource = db.query(Resource).filter(Resource.name == resource_name.capitalize()).first()
        if not resource:
            raise HTTPException(403, f"Resource '{resource_name}' not found")
        # Allow list or string
        if isinstance(permission_name, str):
            permission_names = [permission_name]
        else:
            permission_names = list(permission_name)
        # Fetch all permissions
        permissions = db.query(PermissionModel).filter(PermissionModel.name.in_(permission_names)).all()
        if not permissions:
            raise HTTPException(403, f"None of the permissions {permission_names} found")
        permission_ids = {p.id for p in permissions}
        # Check if user has a role with any of these permissions and the resource
        has_permission = False
        for ur in user.roles:
            for rp in ur.role.permissions:
                if rp.permission_id in permission_ids and rp.resource_id == resource.id:
                    has_permission = True
                    break
            if has_permission:
                break
        #logger.debug(f"Permissions necessary for endpoint: {permission_names} on resource '{resource_name}'")
        #logger.debug(f"Permissions of user '{user.email}': {[rp.permission.name for ur in user.roles for rp in ur.role.permissions if rp.resource_id == resource.id]}")
        if not has_permission:
            raise HTTPException(403, f"Not enough permissions for resource '{resource_name}' and permissions {permission_names}")
        return user
    return checker