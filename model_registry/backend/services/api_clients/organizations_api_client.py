"""ApiClient for ``/api/v1/organizations/`` and the org<->dept link table."""

from .base_api_client import BaseApiClient


class OrganizationsApiClient(BaseApiClient):
    resource_path = "organizations"


class OrganizationsDepartmentsApiClient(BaseApiClient):
    """Link table between organizations and departments."""
    resource_path = "organizations_departments"
