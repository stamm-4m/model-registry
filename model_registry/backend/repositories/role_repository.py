
from model_registry.backend.models.permission import Permission
from model_registry.backend.models.role import Role
from model_registry.backend.models.role_permission import RolePermission
from model_registry.backend.repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository):
    def get_first_role_id_for_permission(self, role_ids, permission_id):
        """Devuelve el primer role_id de la lista que concede el permiso dado."""
        row = (
            self.db.query(RolePermission.role_id)
            .filter(RolePermission.role_id.in_(role_ids))
            .filter(RolePermission.permission_id == permission_id)
            .first()
        )
        return row[0] if row else None

    def get_all(self) -> list[Role]:
        return self.db.query(Role).all()

    def get_by_id(self, role_id) -> Role | None:
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

    # get permissions for role ids
    def get_permissions_by_ids(self, permission_ids):
        return self.db.query(Permission).filter(Permission.id.in_(permission_ids)).all()

    def get_role_ids_by_permission_ids(self, permission_ids):
        """Return distinct role IDs that grant any of the given permission IDs."""
        if not permission_ids:
            return []
        rows = (
            self.db.query(RolePermission.role_id)
            .filter(RolePermission.permission_id.in_(permission_ids))
            .distinct()
            .all()
        )
        return [r[0] for r in rows]

    def get_permissions_by_role_ids(self, role_ids):
        """Devuelve todos los permisos asociados a una lista de role_ids."""
        from model_registry.backend.models.permission import Permission
        from model_registry.backend.models.role_permission import RolePermission

        if not role_ids:
            return []
        rows = (
            self.db.query(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .filter(RolePermission.role_id.in_(role_ids))
            .all()
        )
        return rows
