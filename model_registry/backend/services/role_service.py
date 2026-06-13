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
    def get_permissions_by_ids(self, permission_ids):
        logger.info(f"Getting permissions for permission IDs: {permission_ids}")
        if not permission_ids:
            return []
        valid_ids = []
        for p in permission_ids:
            try:
                valid_ids.append(UUID(str(p)))
            except:
                continue

        if not valid_ids:
            return []
        permissions = self.role_repo.get_permissions_by_ids(valid_ids)
        self.role_repo.close()
        return permissions

    def get_role_ids_by_permission_ids(self, permission_ids):
        logger.info(f"Getting role IDs for permission IDs: {permission_ids}")
        if not permission_ids:
            return []
        valid_ids = []
        for p in permission_ids:
            try:
                valid_ids.append(UUID(str(p)))
            except Exception:
                continue
        if not valid_ids:
            return []
        role_ids = self.role_repo.get_role_ids_by_permission_ids(valid_ids)
        self.role_repo.close()
        return [str(r) for r in role_ids]
    
    def get_permissions_by_role_ids(self, role_ids):
        """Devuelve todos los permisos asociados a una lista de role_ids."""
        if not role_ids:
            return []
        valid_ids = []
        from uuid import UUID
        for rid in role_ids:
            try:
                valid_ids.append(UUID(str(rid)))
            except Exception:
                continue
        permissions = self.role_repo.get_permissions_by_role_ids(valid_ids)
        self.role_repo.close()
        return permissions