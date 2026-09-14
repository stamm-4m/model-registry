"""ApiClient for ``/api/v1/equipments/``."""

from .base_api_client import BaseApiClient


class EquipmentsApiClient(BaseApiClient):
    resource_path = "equipments"
