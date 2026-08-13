"""ApiClient for ``/api/v1/runs/``."""

from .base_api_client import BaseApiClient


class RunsApiClient(BaseApiClient):
    resource_path = "runs"
