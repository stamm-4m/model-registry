"""ApiClient for ``/api/v1/users/``, ``/api/v1/user_role/`` and ``/api/v1/roles/``."""

from .base_api_client import BaseApiClient


class UsersApiClient(BaseApiClient):
    resource_path = "users"


class UserRolesApiClient(BaseApiClient):
    """Per-user role / permission assignments."""

    resource_path = "user_role"


class RolesApiClient(BaseApiClient):
    """Catalogue of available roles."""

    resource_path = "roles"
