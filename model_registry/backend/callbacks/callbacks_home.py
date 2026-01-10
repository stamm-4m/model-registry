from dash import Input, Output, State,html, callback_context,ALL
import dash_ag_grid as dag
from dash.exceptions import PreventUpdate
from model_registry.backend.config.settings import API_BASE_URL
import requests
import logging
import json
logger = logging.getLogger(__name__)
def register_home_callbacks(app):
    @app.callback(
        Output("models-grid", "rowData"),
        Output("models-grid-data", "data"),
        Input("filter-project", "value"),
        Input("filter-model", "value"),
        Input("filter-author", "value")
    )
    def update_models_table(project_id, model_filter, author_filter):
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
                    "status": m.get("metadata", {}).get("status", "offline"),
                    "project_id": pid,
                    "model_id": m.get("metadata", {}).get("ID"),
                    "actions": "edit"  # 👈 dummy value (obligatorio)
                }
                # Aplicar filtros de dropdown
                if model_filter and model_filter.lower() not in row["model_name"].lower():
                    continue
                if author_filter and author_filter.lower() not in row["authors"].lower():
                    continue
                table_data.append(row)

        return table_data, table_data

    @app.callback(
        Output("url", "pathname"),
        Input("models-grid", "cellClicked"),
         State("models-grid-data", "data"),
        prevent_initial_call=True
    )
    def on_grid_click(event,rows_data):
        if not event:
            raise PreventUpdate

        # Solo reaccionar si hacen click en Actions
        if event["colId"] != "edit":
            raise PreventUpdate
        #logger.debug(f"Clicked on edit icon for row: {event}")
        row_index = event.get("rowIndex")
        if row_index is None:
            raise PreventUpdate

        row = rows_data[row_index]

        return f"/edit-model/{row['project_id']}/{row['model_id']}"

