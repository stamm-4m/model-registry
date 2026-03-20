
from model_registry.api.utils.project_loader import get_project_paths


def get_path_models_folder(project_id: str | None = None) -> str:
    """
    Return the path to the models folder.

    If a project_id is provided, the models directory for that project is returned.
    Otherwise, the base models directory is returned.
    """
    if project_id:
        paths = get_project_paths(project_id)
        return paths.get("MODEL_DIR", "")

    return ""

def get_path_config_folder(project_id: str | None = None) -> str:
    """
    Return the path to the config folder.

    If a project_id is provided, the config directory for that project is returned.
    Otherwise, the base config directory is returned.
    """
    if project_id:
        paths = get_project_paths(project_id)
        return paths.get("CONFIG_DIR", "")

    return ""
