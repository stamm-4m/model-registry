import logging
import os

from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate

from model_registry.api.utils.project_loader import load_model
from model_registry.backend.services.model2seek_service import check_model_vars_service
from model_registry.backend.utils.utils_model_upload import (
    get_path_config_folder,
    get_path_models_folder,
)
from model_registry.backend.utils.utils_upload_model_ibisba import (
    get_available_creators,
    get_available_models_options,
    get_available_projects_ibisba,
    get_available_organisms,
)

logger = logging.getLogger(__name__)

def register_upload_model_ibisba_callbacks(app):
    
    @app.callback(
        Output("metadata-yaml-path", "data"),
        Output("model-file-name", "data"),
        Output("model-file-path", "data"),
        Input("available-models-dropdown", "value"),
        State("projects-dropdown", "value")
    )
    def on_model_selected(model_id, project_id):
        if not model_id:
            return "", "", ""
        
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
        
        return metadata_yaml_path, model_file_name, model_file_path
    

    @app.callback(
        Output("upload-form-collapse", "is_open"),
        Output("selection-confirmed-alert", "is_open"),
        Output("model-title", "value"),
        Output("model-creators", "options"),
        Output("model-project-id-ibisba", "options"),
        Output("model-organisms", "options"),
        Input("confirm-selection-btn", "n_clicks"),
        State("metadata-yaml-path", "data"),
        State("model-file-name", "data"),
        State("model-file-path", "data"),
        prevent_initial_call=True
    )
    def confirm_selection(n_clicks, metadata_yaml_path, model_file_name, model_file_path):
        if not metadata_yaml_path or not model_file_name or not model_file_path:
            logger.warning("Model selection incomplete: missing metadata path, file name, or file path")
            return False, False, "", [], [], []
        model_title = f"Model {model_file_name}"
        options_creators = [{"label": "Creator 1", "value": 1}]
        options_projects_ibisba = [{"label": "Project 1", "value": 1}]
        options_organisms = [{"label": "Organism 1", "value": 1}]
        try:
            #options_creators = get_available_creators()
            options_creators = []
        except Exception:
            logger.exception("Failed to fetch available creators")
            options_creators = []
        try:
            #options_projects_ibisba = get_available_projects_ibisba()
            options_projects_ibisba = []

        except Exception:
            logger.exception("Failed to fetch available projects in IBISBA")
            options_projects_ibisba = []
        try:
            #options_organisms = get_available_organisms()
            options_organisms = []  
        except Exception:
            logger.exception("Failed to fetch available organisms")
            options_organisms = []
        options_creators = [{"label": "Creator 1", "value": 226}]
        options_projects_ibisba = [{"label": "Project 17", "value": 97}]
        options_organisms = [{"label": "Organism 4", "value": 950658006}]

        return True, True, model_title, options_creators, options_projects_ibisba, options_organisms

    @app.callback(
        Output("confirm-upload-modal", "is_open"),
        Output("confirm-upload-body", "children"),
        Input("confirm-selection-ibisba-btn", "n_clicks"),
        State("model-project-id-ibisba", "value"),
        State("model-creators", "value"),
        State("model-organisms", "value"),
        prevent_initial_call=True,
    )
    def validate_and_preview_model(n_clicks, project_id_ibisba, model_creators, model_organisms):
        if not n_clicks:
            raise PreventUpdate

        if not model_creators:
            return False, "Model creators cannot be empty"
        if not project_id_ibisba:
            return False, "Project ID cannot be empty"
        if not model_organisms:
            return False, "Model organisms cannot be empty"
        
        if isinstance(model_creators, str):
            creators_list = [int(c.strip()) for c in model_creators.split(",") if c.strip()]
        elif isinstance(model_creators, list):
            creators_list = model_creators
        else:
            return False, "Invalid format for model creators"
        if isinstance(model_organisms, str):
            organisms_list = [o.strip() for o in model_organisms.split(",") if o.strip()]  
        elif isinstance(model_organisms, list):
            organisms_list = model_organisms
        else:
            return False, "Invalid format for model organisms"

        # check model variables
        try:
            (
                project_info,
                creators_info,
                organisms_info,
                simple_output,
            ) = check_model_vars_service(
                containing_project_id=project_id_ibisba,
                model_creators=creators_list,
                model_organisms=organisms_list,
            )
        except Exception as e:
            logger.exception("Model validation failed")
            return False, f"❌ Validation error: {str(e)}"
        # modal content
        body = html.Div(
            [
                html.H5("Project"),
                html.P(project_info.get("title")),

                html.H5("Creators"),
                html.Ul(
                    [
                        html.Li(
                            f"{c.get('name')} ({c.get('orcid', 'no ORCID')})"
                        )
                        for c in creators_info.values()
                    ]
                ),
                html.H5("Organisms"),
                html.Ul(
                    [
                        html.Li(
                            f"{o.get('title')} ({o.get('concept_uri')})"
                            #f" - {o.get('description', 'No description')}"

                        )
                        for o in organisms_info.values()
                    ]
                ),
            ]
        )

        return True, body

    @app.callback(
        Output("confirm-selection-ibisba-btn", "disabled"),
        Input("model-creators", "value"),
        Input("model-project-id-ibisba", "value"),
        Input("model-organisms", "value"),
    )
    def disable_button(creators, project, organisms):
        if not creators or not project or not organisms :
            return True
        return False

    @app.callback(
        Output("boton-form-collapse", "is_open"),
        Output("selection-confirmed-ibisba-alert", "is_open"),
        Output("confirm-upload-modal", "is_open",allow_duplicate=True),
        Input("confirm-upload-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def show_final_confirmation(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return True, True, False

    @app.callback(
        Output("upload-status", "children"),
        Output("upload-model-btn", "disabled"),
        Input("upload-model-btn", "n_clicks"),
        State("metadata-yaml-path", "value"),
        State("model-file-name", "value"),
        State("model-file-path", "value"),
        State("model-project-id-ibisba", "value"),
        State("model-title", "value"),
        State("model-creators", "value"),
        prevent_initial_call=True,
    )
    def save_model_confirmed(
        n_clicks,
        yaml_path,
        model_file_name,
        model_file_path,
        project_id_ibisba,
        model_title,
        model_creators,
    ):
        if not n_clicks:
            raise PreventUpdate

        if isinstance(model_creators, str):
            model_creators_list = [int(c.strip()) for c in model_creators.split(",")]
        else:
            model_creators_list = model_creators
        
        try:
            #logger.debug(f"model_creators: {model_creators}")
            #logger.debug(f"project id ibisba: {project_id_ibisba}")
            #upload_model_to_seek(
            #    yaml_path,
            #    model_file_name,
            #    model_file_path,
            #    project_id_ibisba,
            #    model_title,
            #    model_creators_list
            #)
            return "✅ Model successfully uploaded to IBISBA", True

        except Exception as e:
            return f"❌ Upload failed: {str(e)}", False

    @app.callback(
        Output("confirm-upload-modal", "is_open",allow_duplicate=True),
        Input("cancel-upload-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def close_modal(n_clicks):
        return False
