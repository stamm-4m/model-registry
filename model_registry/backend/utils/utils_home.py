import os

import requests
from model_registry.backend.config.settings import settings

from model_registry.api.utils.project_loader import (
    get_project_paths,
    list_projects_by_id,
    load_project_info,
)


def get_option_projects_dropdown(session_data=None):
    headers = {
        "Authorization": f"Bearer {session_data['access_token']}"
    }

    response = requests.get(f"{settings.API_BASE_URL}/list_projects/", headers=headers) 
    project_map = {}
    
    if response.status_code == 200:
        for p in response.json():
            project_map[p["project_ID"]] = p.get("project_name", p["project_ID"])
        options = []
        for project_id, project_name in project_map.items():
            options.append({"label": project_id + " - " + project_name, "value": project_id})
        return options
    
    if response.status_code != 200:
        print(f"Error fetching projects: {response.status_code} - {response.text}")
        return []

    

def delete_model_from_registry(project_id: str, model_id: str):
    """Delete a model from the registry given its project_ID and model_ID."""   
    paths = get_project_paths(project_id)
    model_file = os.path.join(paths["MODEL_DIR"], f"{model_id}.pkl")
    config_file = os.path.join(paths["CONFIG_DIR"], f"{model_id}.yaml")
    # Delete model file
    if os.path.exists(model_file):  
        os.remove(model_file)
    # Delete config file        
    if os.path.exists(config_file):
        os.remove(config_file)      
    return True 
