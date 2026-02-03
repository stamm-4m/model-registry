import os

from model_registry.api.utils.project_loader import (
    get_project_paths,
    list_projects_by_id,
    load_project_info,
)


def get_option_projects_dropdown():
    project_map = list_projects_by_id()
    options = []
    for project_id, folder_name in project_map.items():
        info = load_project_info(project_id)
        project_name = info.get("project_name", folder_name) if info else folder_name
        options.append({"label": project_id + " - " + project_name, "value": project_id})
    return options

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
