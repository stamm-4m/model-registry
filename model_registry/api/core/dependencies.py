
from typing import List

from requests import Session
from model_registry.api.core.database import get_db
from model_registry.api.core.security import get_current_user
from model_registry.api.models.laboratory_project import LaboratoryProject
from fastapi import Depends, HTTPException
import logging

from model_registry.api.models.project import Project

logger = logging.getLogger(__name__)

def require_permissions(perms: list):
    def checker(user = Depends(get_current_user)):
        logger.debug(f"Checking permissions for user: {user.email}, Required: {perms}, User's permissions: {user.permissions}")
        if not any(p in user.permissions for p in perms):
            raise HTTPException(403, "Not enough permissions")
        return user
    return checker

def require_roles(roles: list):
    def checker(user = Depends(get_current_user)):
        if not any(r in user.roles_names for r in roles):
            raise HTTPException(403, "Not enough roles")
        return user
    return checker

def require_lab_permission(permission: str, lab_id: int):
    def checker(user = Depends(get_current_user)):
        
        for ur in user.roles:
            if ur.laboratory.id == lab_id:
                if any(p.name == permission for p in ur.role.permissions):
                    return user

        raise HTTPException(403, "Not allowed in this lab")

    return checker

def require_permissions_projects(perms: list):
    def checker( project_id: str,
        user=Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        logger.debug(f"Checking permissions for user: {user.email}, Required: {perms}, User's permissions: {user.permissions}")
        if not any(p in user.permissions for p in perms):
            raise HTTPException(403, "Not enough permissions")
        
        validate_project_access(user, db, project_id)

        return user
    return checker

def validate_project_access(user, db, project_id: str):
    """
    Validate if user has access to a project via laboratory.
    """
    # Get  project
    project_db = (
            db.query(Project)
            .filter(Project.project_id == project_id)
            .first()
    )
    if not project_db:
        raise HTTPException(status_code=404, detail=f"Project ID {project_id} not found in database")
    
    user_lab_ids = [ur.laboratory_id for ur in user.roles]

    if not user_lab_ids:
        raise HTTPException(403, "No lab access")

    exists = (
        db.query(LaboratoryProject)
        .filter(
            LaboratoryProject.project_id == project_db.id,
            LaboratoryProject.laboratory_id.in_(user_lab_ids)
        )
        .first()
    )

    if not exists:
        raise HTTPException(403, "Not allowed for this project")