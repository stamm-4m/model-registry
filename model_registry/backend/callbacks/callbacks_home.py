import logging
import dash
import requests
from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from model_registry.backend.config.settings import settings
from model_registry.backend.services.model_service import ModelService
from model_registry.backend.services.project_service import list_projects
from model_registry.backend.utils.utils_home import delete_model_from_registry, _format_date_ddmmyyyy

logger = logging.getLogger(__name__)

def register_home_callbacks(app):
    @app.callback(
        Output("models-grid", "rowData"),
        Output("models-grid-data", "data"),
        Output("user-session", "data", allow_duplicate=True),
        Input("filter-project", "value"),
        State("user-session", "data"),
        prevent_initial_call="initial_duplicate",
    )
    def update_models_table(project_id, session_data):
        """
        Fetch all models from the API and filter based on dropdowns.
        """
        logger.debug(f"Updating models table for project_id={project_id} with session session_data")
        projects = []
        if project_id:
            projects = [project_id]
        # List all projects si no hay filtro    
        else:
            try:
                projects_response, session_data = list_projects(session_data)
                projects = [p["project_ID"] for p in projects_response]
            except Exception as e:
                print(f"Error fetching projects: {e}")
                return [], [], session_data

        # Recolectar todos los modelos (Postgres-backed) de los proyectos
        table_data = []
        model_service = ModelService()
        for pid in projects:
            try:
                models_response, session_data = model_service.list_db_models_for_project(
                    session_data, pid
                )
                logger.debug(f"count DB models for project {pid}: {len(models_response)}")
            except Exception as e:
                logger.warning(f"Error fetching DB models for project {pid}: {e}")
                continue

            for m in models_response:
                meta = m.get("metadata", {})
                row = {
                    "model_name": f"{m.get('model_name')} - {m.get('model_ID')}",
                    "authors": meta.get("authors"),
                    "creation_data": _format_date_ddmmyyyy(meta.get("created_at")),
                    "version": meta.get("version"),
                    "status": meta.get("is_active", False),
                    "project_id": pid,
                    "model_id": meta.get("ID"),        # slug — used for routing
                    "db_uuid":  meta.get("db_uuid"),   # Postgres UUID — used for API ops
                    "actions": "edit"
                }
                # Aplicar filtros de dropdown
                if project_id and project_id != row["project_id"]:
                    continue
               
                table_data.append(row)

        return table_data, table_data, session_data

    @app.callback(
        Output("url", "pathname"),
        Output("confirm-delete-model", "displayed"),
        Output("model-to-delete", "data"),
        Input("models-grid", "cellClicked"),
        State("models-grid-data", "data"),
        prevent_initial_call=True
    )
    def on_grid_click(event, rows_data):
        logger.debug(f"Grid cell clicked: {event}")
        if not event:
            raise PreventUpdate

        col_id = event.get("colId")
        row_id = event.get("rowId") 
        logger.debug(f"Grid click event: {event}")
        if not row_id:
            raise PreventUpdate

        # Find model_id real
        row = next(
            (r for r in rows_data if str(r["model_id"]) == str(row_id)),
            None
        )

        if not row:
            raise PreventUpdate
        logger.debug(f"Grid clicked: row_index={row_id} col={col_id}, row={row}")
        # ===== EDIT =====
        if col_id == "edit":
            return (
                f"/edit-model/{row['project_id']}/{row['model_id']}",
                False,
                None
            )
        if col_id == "details":
            return (
                f"/details-model/{row['project_id']}/{row['model_id']}",
                False,
                None
            )
    
        if col_id == "xai":
            return (
                f"/model-explainability/{row['project_id']}/{row['model_id']}",
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
                    "model_id":   row["model_id"],
                    "db_uuid":    row.get("db_uuid"),  # UUID for API delete
                }
            )

        raise PreventUpdate
    
    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Output("models-grid-data", "data", allow_duplicate=True),
        Output("user-session", "data", allow_duplicate=True),
        Input("confirm-delete-model", "submit_n_clicks"),
        State("model-to-delete", "data"),
        State("models-grid-data", "data"),
        State("user-session", "data"),
        prevent_initial_call=True
    )
    def delete_model(submit, model_info, rows_data, session_data):
        logger.debug(f"Delete model submit clicked {submit} with model_info={model_info}")
        if not submit or not model_info:
            raise PreventUpdate

        project_id = model_info["project_id"]
        model_id   = model_info["model_id"]
        db_uuid    = model_info.get("db_uuid")

        # --- DB delete via API (use UUID if available, slug as fallback) ---
        delete_id = db_uuid or model_id
        try:
            from model_registry.backend.services.api_clients.models_api_client import ModelsApiClient
            status_code, session_data = ModelsApiClient().delete_model_row(delete_id, session_data)
            if status_code not in (200, 204, None):
                logger.warning("API delete returned %s for model %s", status_code, delete_id)
            else:
                logger.info("Model %s deleted via API (id=%s)", model_id, delete_id)
        except Exception as exc:
            logger.warning("API delete failed for model %s: %s", delete_id, exc)

        # --- Artifact file cleanup (best-effort, file-backed legacy models) ---
        try:
            delete_model_from_registry(project_id, model_id)
        except Exception as exc:
            logger.debug("File cleanup skipped for %s: %s", model_id, exc)

        # Remove from grid immediately so the UI reflects the deletion
        updated_rows = [
            r for r in (rows_data or [])
            if not (r.get("project_id") == project_id and r.get("model_id") == model_id)
        ]

        return "/home", updated_rows, session_data

    
    @app.callback(
        Output("project-required-modal", "is_open", allow_duplicate=True),
        Output("url", "pathname", allow_duplicate=True),
        Input("add-model", "n_clicks"),
        State("filter-project", "value"),
        State("project-required-modal", "is_open"),
        prevent_initial_call=True,
    )
    def go_back_to_list(n_clicks, project_id, is_open):
        logger.debug(f"Add model clicked {n_clicks} times with project_id={project_id} and modal open={is_open}")
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
        logger.debug(f"Close project modal clicked {n_clicks} times with modal open={is_open}")
        return not is_open
    

