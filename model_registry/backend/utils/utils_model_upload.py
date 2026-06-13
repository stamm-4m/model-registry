import logging

from model_registry.api.utils.project_loader import get_project_paths
from model_registry.backend.services.project_service import ProjectService

logger = logging.getLogger(__name__)


def get_path_models_folder(
    project_id: str | None = None, session_data=None,
) -> str:
    """
    Return the path to the models folder.

    Uses ``project_id`` to fetch the project info from the API, extracts
    the project name, and passes that value to ``get_project_paths``.
    """
    if project_id:
        #project_name = _resolve_project_name(project_id, session_data)
        #lookup_key = project_name or project_id
        #logger.info(f"Using lookup key: {lookup_key}")
        paths = get_project_paths(project_id)
        return paths.get("MODEL_DIR", "")

    return ""

def get_path_config_folder(
    project_id: str | None = None, session_data=None,
) -> str:
    """
    Return the path to the config folder.

    Uses ``project_id`` to fetch the project info from the API, extracts
    the project name, and passes that value to ``get_project_paths``.
    """
    if project_id:
        #project_name = _resolve_project_name(project_id, session_data)
        #lookup_key = project_name or project_id
        #paths = get_project_paths(lookup_key)
        paths = get_project_paths(project_id)
        return paths.get("CONFIG_DIR", "")

    return ""
