
# Class to manage permissions, loading them from the database and caching them for efficient access.
from model_registry.api.core.database import SessionLocal
from model_registry.api.models.permission import Permission as PermissionModel

class PermissionManager:
    _permissions = None

    @classmethod
    def load_permissions(cls):
        """Loads all permissions from the database and caches them."""
        session = SessionLocal()
        try:
            perms = session.query(PermissionModel).all()
            cls._permissions = {p.name: p for p in perms}
        finally:
            session.close()

    @classmethod
    def get(cls, name):
        """Gets a permission by name."""
        if cls._permissions is None:
            cls.load_permissions()
        return cls._permissions.get(name)

    @classmethod
    def all(cls):
        """Gets all permissions."""
        if cls._permissions is None:
            cls.load_permissions()
        return list(cls._permissions.values())