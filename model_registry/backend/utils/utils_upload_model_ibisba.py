import logging

import requests

from model_registry.api.utils.project_loader import list_models_by_id, list_projects
from model_registry.backend.vendor.metadata_tools.fairdom_seek.seek import seek

from model_registry.backend.config.settings import (
        API_BASE_URL,
        MODEL2SEEK_API_TOKEN,
        MODEL2SEEK_BASE_URL,
)
logger = logging.getLogger(__name__)

def get_available_models_options(project_id="P0001"):    
    models = list_models_by_id(project_id)
    options = [{"label": keys + " - " + values, "value": keys} for keys, values in models.items()]
    return options

def get_available_projects():
    projects = list_projects()
    return [{"label": p["name"], "value": p["id"]} for p in projects]

def get_available_creators():
    try:
        seek_py = seek(base_url=MODEL2SEEK_BASE_URL, token=MODEL2SEEK_API_TOKEN)
        seek_py.start_session()

        people = seek_py.get_known_assets(
            seek_url_for_asset="people",
            store_info=True
        )

        logger.info(f"Found {len(people)} creators in SEEK")

        return [
            {"label": creator["name"], "value": creator["id"]}
            for creator in people.values()
        ]

    except Exception as e:
        logger.error(f"Error loading creators from SEEK: {e}")
        return []
def get_available_projects_ibisba(): 
    try:
        seek_py = seek(base_url=MODEL2SEEK_BASE_URL, token=MODEL2SEEK_API_TOKEN)
        seek_py.start_session()                 
        projects = seek_py.get_known_assets(
            seek_url_for_asset="projects",
            store_info=True
        )   
        logger.info(f"Found {len(projects)} projects in SEEK")
        return [
            {"label": project["name"], "value": project["id"]}
            for project in projects.values()
        ]   
    except Exception as e:
        logger.error(f"Error loading projects from SEEK: {e}")
        return []
    
def get_available_organisms():
    try:
        seek_py = seek(base_url=MODEL2SEEK_BASE_URL, token=MODEL2SEEK_API_TOKEN)
        seek_py.start_session()

        people = seek_py.get_known_assets(
            seek_url_for_asset="organisms",
            store_info=True
        )

        logger.info(f"Found {len(people)} organisms in SEEK")

        return [
            {"label": organism["name"], "value": organism["id"]}
            for organism in people.values()
        ]

    except Exception as e:
        logger.error(f"Error loading organisms from SEEK: {e}")
        return []

def get_information_model(project_id, model_id):
    model_info = None
    try:
        response = requests.get(
            f"{API_BASE_URL}{project_id}/metadata/{model_id}"
        )
        model = response.json()
        model_info = model["model_identification"]
    except Exception as e:
        logger.error(f"Error fetching model information for project {project_id} and model {model_id}: {e}")
    return model_info

