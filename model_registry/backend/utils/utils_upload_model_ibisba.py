import logging

from model_registry.api.utils.project_loader import list_models_by_id, list_projects

logger = logging.getLogger(__name__)

def get_available_models_options(project_id="P0001"):    
    models = list_models_by_id(project_id)
    options = [{"label": keys + " - " + values, "value": keys} for keys, values in models.items()]
    return options

def get_available_projects():
    projects = list_projects()
    return [{"label": p["name"], "value": p["id"]} for p in projects]