"""ApiClient for ``/api/v1/laboratories/`` and the lab<->user link table."""

from .base_api_client import BaseApiClient


class LaboratoriesApiClient(BaseApiClient):
    resource_path = "laboratories"


class LaboratoryUserApiClient(BaseApiClient):
    """Link table between laboratories and users.

    Note: the API exposes the table at ``/api/v1/laboratory_user/``
    (singular ``user``, matching the SQLAlchemy ``__tablename__``).
    """

    resource_path = "laboratory_user"
