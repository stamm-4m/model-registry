from uuid import UUID

from model_registry.backend.repositories.role_repository import RoleRepository
import logging
logger = logging.getLogger(__name__)

class RoleService:

    def __init__(self):
        self.role_repo = RoleRepository()
        self.db = self.role_repo.db  
        
    def get_all_roles(self):
        roles = self.role_repo.get_all()
        self.role_repo.close()
        return roles
    def get_permissions_by_role_ids(self, role_ids):
        logger.info(f"Getting permissions for role IDs: {role_ids}")
        if not role_ids:
            return []
        valid_ids = []
        for r in role_ids:
            try:
                valid_ids.append(UUID(str(r)))
            except:
                continue

        if not valid_ids:
            return []
        permissions = self.role_repo.get_permissions_by_role_ids(valid_ids)
        self.role_repo.close()
        return permissions