"""ApiClient for ``/api/v1/departments/`` and the dept<->lab link table."""

from .base_api_client import BaseApiClient


class DepartmentsApiClient(BaseApiClient):
    resource_path = "departments"


class DepartmentLaboratoryApiClient(BaseApiClient):
    """Link table between departments and laboratories."""
    resource_path = "department_laboratory"
