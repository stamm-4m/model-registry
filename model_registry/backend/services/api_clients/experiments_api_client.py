"""ApiClient for ``/api/v1/experiments/``."""

from .base_api_client import BaseApiClient


class ExperimentsApiClient(BaseApiClient):
    resource_path = "experiments"
