from dash import Output, Input, State, ALL
import dash
from dash.exceptions import PreventUpdate
from model_registry.backend.core.exceptions import OrganizationInUseException
from model_registry.backend.services.organization_service import OrganizationService
import logging
logger = logging.getLogger(__name__)

def register_delete_organization_modal_callbacks(app):
    @app.callback(
        Output("delete-org-modal", "is_open"),
        Output("org-delete-id", "data"),
        Input({"type": "btn-delete-org", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def open_delete_modal(n_clicks_list):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        if not any(n and n > 0 for n in n_clicks_list):
            raise PreventUpdate

        org_id = ctx.triggered_id["index"]

        return True, org_id
    
    @app.callback(
        Output("delete-org-modal", "is_open",allow_duplicate=True),
        Output("org-refresh-trigger", "data", allow_duplicate=True),
        Output("org-toast", "is_open", allow_duplicate=True),
        Output("org-toast", "children", allow_duplicate=True),
        Output("org-toast", "icon", allow_duplicate=True),
        Input("btn-confirm-delete", "n_clicks"),
        State("org-delete-id", "data"),
        prevent_initial_call=True
    )
    def confirm_delete(n_clicks, org_id):
        if not n_clicks or not org_id:
            raise PreventUpdate

        service = OrganizationService()

        try:
            service.delete_organization(org_id)

            return (
                False,              # cerrar modal
                n_clicks,           # refresh tabla
                True,               # mostrar toast
                "Organization deleted successfully",
                "success"
            )
        
        except OrganizationInUseException as e:
            return (
                False,
                dash.no_update,
                True,
                str(e),   # 🔥 mensaje dinámico
                "warning"
            )

        except Exception as e:
            return (
                False,
                dash.no_update,
                True,
                f"Error deleting organization: {str(e)}",
                "danger"
            )
    
    @app.callback(
        Output("delete-org-modal", "is_open", allow_duplicate=True),
        Input("btn-cancel-delete", "n_clicks"),
        prevent_initial_call=True
    )
    def cancel_delete(n):
        return False