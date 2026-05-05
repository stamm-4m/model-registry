"""ApiClient for ``/api/v1/users/`` and ``/api/v1/user_role/``."""

from .base_api_client import BaseApiClient


class UsersApiClient(BaseApiClient):
    resource_path = "users"


class UserRolesApiClient(BaseApiClient):
    """Per-user role / permission assignments."""
    resource_path = "user_role"
