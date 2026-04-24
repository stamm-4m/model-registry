from dash import Output, Input, State, ALL
import dash
from dash.exceptions import PreventUpdate
from model_registry.backend.core.exceptions import ProjectInUseException
import logging

from model_registry.backend.services.project_service import ProjectService
logger = logging.getLogger(__name__)

def register_delete_project_modal_callbacks(app):
    @app.callback(
        Output("delete-proj-modal", "is_open"), 
        Output("proj-delete-id", "data"),
        Input({"type": "btn-delete-proj", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def open_delete_modal_project(n_clicks_list):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        if not any(n and n > 0 for n in n_clicks_list):
            raise PreventUpdate

        proj_id = ctx.triggered_id["index"]

        return True, proj_id
    
    @app.callback(
        Output("delete-proj-modal", "is_open",allow_duplicate=True),
        Output("proj-refresh-trigger", "data", allow_duplicate=True),
        Output("proj-toast", "is_open", allow_duplicate=True),
        Output("proj-toast", "children", allow_duplicate=True),
        Output("proj-toast", "icon", allow_duplicate=True),
        Input("btn-confirm-delete_project", "n_clicks"),
        State("proj-delete-id", "data"),
        prevent_initial_call=True
    )
    def confirm_delete_project(n_clicks, proj_id):
        if not n_clicks or not proj_id:
            raise PreventUpdate

        service = ProjectService()

        try:
            service.delete_project(proj_id)

            return (
                False,              # cerrar modal
                n_clicks,           # refresh tabla
                True,               # mostrar toast
                "Project deleted successfully",
                "success"
            )
        
        except ProjectInUseException as e:
            return (
                False,
                dash.no_update,
                True,
                str(e),  
                "warning"
            )

        except Exception as e:
            return (
                False,
                dash.no_update,
                True,
                f"Error deleting project: {str(e)}",
                "danger"
            )
    
    @app.callback(
        Output("delete-proj-modal", "is_open", allow_duplicate=True),
        Input("btn-cancel-delete_project", "n_clicks"),
        prevent_initial_call=True
    )
    def cancel_delete(n):
        return False