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
            logger.debug(f"Resource '{resource_name}' not found for permission check. User: {getattr(user, 'email', None)}")
            raise HTTPException(403, f"Resource '{resource_name}' not found")
        # Allow list or string
        if isinstance(permission_name, str):
            permission_names = [permission_name]
        else:
            permission_names = list(permission_name)
        # Fetch all permissions
        permissions = db.query(PermissionModel).filter(PermissionModel.name.in_(permission_names)).all()
        if not permissions:
            logger.debug(f"None of the required permissions {permission_names} found in DB for resource '{resource_name}'. User: {getattr(user, 'email', None)}")
            raise HTTPException(403, f"None of the permissions {permission_names} found")
        permission_ids = {p.id for p in permissions}
        # Gather user permissions for this resource
        user_permission_names = [rp.permission.name for ur in user.roles for rp in ur.role.permissions if rp.resource_id == resource.id]
        logger.debug(f"Checking permissions for user '{getattr(user, 'email', None)}' on resource '{resource_name}': required={permission_names}, user_has={user_permission_names}")
        # Check if user has a role with any of these permissions and the resource
        has_permission = False
        for ur in user.roles:
            for rp in ur.role.permissions:
                if rp.permission_id in permission_ids and rp.resource_id == resource.id:
                    has_permission = True
                    break
            if has_permission:
                break
        if not has_permission:
            logger.debug(f"Permission denied for user '{getattr(user, 'email', None)}' on resource '{resource_name}'. Required: {permission_names}, User has: {user_permission_names}")
            raise HTTPException(403, f"Not enough permissions for resource '{resource_name}' and permissions {permission_names}")
        logger.debug(f"Permission granted for user '{getattr(user, 'email', None)}' on resource '{resource_name}'. Required: {permission_names}, User has: {user_permission_names}")
        return user
    return checker