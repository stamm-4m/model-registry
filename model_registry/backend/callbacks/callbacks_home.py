import logging

import dash
import requests
from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from model_registry.backend.config.settings import API_BASE_URL
from model_registry.backend.utils.utils_home import delete_model_from_registry

logger = logging.getLogger(__name__)
def register_home_callbacks(app):
    @app.callback(
        Output("models-grid", "rowData"),
        Output("models-grid-data", "data"),
        Input("filter-project", "value")
    )
    def update_models_table(project_id):
        """
        Fetch all models from the API and filter based on dropdowns.
        """
        # 1. List all projects si no hay filtro
        projects = []
        if project_id:
            projects = [project_id]
        else:
            try:
                projects_response = requests.get(f"{API_BASE_URL}/list_projects/")
                projects_response.raise_for_status()
                projects = [p["project_ID"] for p in projects_response.json()]
            except Exception as e:
                print(f"Error fetching projects: {e}")
                return [],[]

        # 2. Recolectar todos los modelos de los proyectos
        table_data = []
        for pid in projects:
            try:
                models_response = requests.get(f"{API_BASE_URL}{pid}/list_models/")
                models_response.raise_for_status()
                models = models_response.json()
                #logger.debug(f"count models for project {pid}: {models.__len__()}")
            except Exception as e:
                print(f"Error fetching models for project {pid}: {e}")
                continue

            for m in models:
                row = {
                    "model_name": m.get("model_name"),
                    "authors": m.get("metadata", {}).get("author"),
                    "creation_data": m.get("metadata", {}).get("creation_date"),
                    "version": m.get("metadata", {}).get("version"),
                    "status": m.get("metadata", {}).get("status", "offline"),
                    "project_id": pid,
                    "model_id": m.get("metadata", {}).get("ID"),
                    "actions": "edit"
                }
                # Aplicar filtros de dropdown
                if project_id and project_id != row["project_id"]:
                    continue
               
                table_data.append(row)

        return table_data, table_data

    @app.callback(
        Output("url", "pathname"),
        Output("confirm-delete-model", "displayed"),
        Output("model-to-delete", "data"),
        Input("models-grid", "cellClicked"),
        State("models-grid-data", "data"),
        prevent_initial_call=True
    )
    def on_grid_click(event, rows_data):
        
        if not event:
            raise PreventUpdate

        col_id = event.get("colId")
        row_index = event.get("rowIndex")

        if row_index is None:
            raise PreventUpdate

        row = rows_data[row_index]

        # ===== EDIT =====
        if col_id == "edit":
            return (
                f"/edit-model/{row['project_id']}/{row['model_id']}",
                False,
                None
            )
        
        # ===== REGISTER TO =====
        if col_id == "register_to":
            return (
                f"/model-upload-ibisba/{row['project_id']}/{row['model_id']}",
                False,
                None
            )

        # ===== DELETE =====
        if col_id == "delete":
            return (
                dash.no_update,
                True,
                {
                    "project_id": row["project_id"],
                    "model_id": row["model_id"]
                }
            )

        raise PreventUpdate
    
    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Output("models-grid-data", "data", allow_duplicate=True),
        Input("confirm-delete-model", "submit_n_clicks"),
        State("model-to-delete", "data"),
        State("models-grid-data", "data"),
        prevent_initial_call=True
    )
    def delete_model(submit, model_info, rows_data):
        if not submit or not model_info:
            raise PreventUpdate

        project_id = model_info["project_id"]
        model_id = model_info["model_id"]

        # Delete model from disk and registry
        delete_model_from_registry(project_id, model_id)

        # Quitar el modelo de la grilla
        updated_rows = [
            r for r in rows_data
            if not (
                r["project_id"] == project_id
                and r["model_id"] == model_id
            )
        ]

        return "/home", updated_rows

    
    @app.callback(
        Output("project-required-modal", "is_open", allow_duplicate=True),
        Output("url", "pathname", allow_duplicate=True),
        Input("add-model", "n_clicks"),
        State("filter-project", "value"),
        State("project-required-modal", "is_open"),
        prevent_initial_call=True,
    )
    def go_back_to_list(n_clicks, project_id, is_open):
        if not n_clicks:
            raise PreventUpdate

        if not project_id:
            return True, dash.no_update

        return False, f"/model-upload/{project_id}"
    
    @app.callback(
        Output("project-required-modal", "is_open", allow_duplicate=True),
        Input("close-project-modal", "n_clicks"),
        State("project-required-modal", "is_open"),
        prevent_initial_call=True,
    )
    def close_modal(n_clicks, is_open):
        return not is_open
    
    @app.callback(
        Output("url","pathname", allow_duplicate=True),
        Input("add-project", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_add_project(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        logger.debug(f"Add project clicked {n_clicks} times")
        return "/add-project"
    


