import re
from dash import html, dcc, Input, Output, State
import dash
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import logging
import os
from model_registry.api.utils.project_loader import load_model
from model_registry.backend.services.model2seek_service import upload_model_to_seek
from model_registry.backend.utils.utils_model_upload import get_path_config_folder,get_path_models_folder
from model_registry.backend.utils.utils_upload_model_ibisba import get_available_models_options

logger = logging.getLogger(__name__)

def register_upload_model_ibisba_callbacks(app):
    @app.callback(
        Output("models-dropdown-collapse", "is_open"),
        Output("available-models-dropdown", "options"),
        Input("projects-dropdown", "value")
    )
    def on_project_selected(project_id):
        if not project_id:
            return False, []
        options = get_available_models_options(project_id)
        #logger.debug(f"Available models for project {project_id}: {options}")
        return True, options
    
    @app.callback(
        Output("upload-form-collapse", "is_open"),
        Output("metadata-yaml-path", "value"),
        Output("model-file-name", "value"),
        Output("model-file-path", "value"),
        Output("model-title", "value"),
        Input("available-models-dropdown", "value"),
        State("projects-dropdown", "value")
    )
    def on_model_selected(model_id, project_id):
        if not model_id:
            return False, "", "", "", ""
        # Here you would typically fetch model details based on model_id
        # For demonstration, we will use placeholder values
        info_model = load_model(project_id, model_id)

        metadata_yaml_path = os.path.join(
            get_path_config_folder(project_id),
            model_id + ".yaml",
        )
        model_file = info_model.get("ml_model_configuration", {}).get("model_description", {}).get("config_files", {}).get("model_file", "")
        model_file_name = info_model.get("ml_model_configuration", {}).get("model_identification", {}).get("ID", "")
        model_file_path = os.path.join(
            get_path_models_folder(project_id),
            model_file,
        )
        model_title = f"Model {model_id} Title"
        return True, metadata_yaml_path, model_file_name, model_file_path, model_title   
    
    @app.callback(
        Output("upload-status", "children"),
        Input("upload-model-btn", "n_clicks"),
        State("metadata-yaml-path", "value"),
        State("model-file-name", "value"),
        State("model-file-path", "value"),
        State("model-project-id-ibisba", "value"),
        State("model-title", "value"),
        State("model-creators", "value"),
        prevent_initial_call=True
    )
    def save_model(
        n_clicks,
        yaml_path,
        model_file_name,
        model_file_path,
        project_id_ibisba,
        model_title,
        model_creators
    ):
        if not n_clicks:
            raise PreventUpdate
        if not model_creators:
            raise ValueError("Model creators cannot be empty")

        if isinstance(model_creators, str):
            model_creators_list = [
                int(c.strip())
                for c in model_creators.split(",")
                if c.strip()
            ]
        elif isinstance(model_creators, list):
            model_creators_list = model_creators
        else:
            raise ValueError("Invalid format for model creators")

        if not model_creators_list:
            raise ValueError("Model creators list is empty")
        
        try:
            #logger.debug(f"model_creators: {model_creators}")
            #logger.debug(f"project id ibisba: {project_id_ibisba}")
            upload_model_to_seek(
                yaml_path,
                model_file_name,
                model_file_path,
                project_id_ibisba,
                model_title,
                model_creators_list
            )
            return "✅ Model successfully uploaded to IBISBA"

        except Exception as e:
            return f"❌ Upload failed: {str(e)}"
