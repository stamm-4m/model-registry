from dash import Output, Input, State, ALL
import dash
from dash.exceptions import PreventUpdate
import logging

from model_registry.backend.core.exceptions import UserHasRolesException
from model_registry.backend.services.user_service import UserService

logger = logging.getLogger(__name__)


def register_delete_user_modal_callbacks(app):

    
    @app.callback(
        Output("delete-user-modal", "is_open"),
        Output("user-delete-id", "data"),
        Input({"type": "btn-delete-user", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def open_delete_modal_user(n_clicks_list):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        if not any(n and n > 0 for n in n_clicks_list):
            raise PreventUpdate

        user_id = ctx.triggered_id["index"]

        return True, str(user_id)  

    @app.callback(
        Output("delete-user-modal", "is_open", allow_duplicate=True),
        Output("user-refresh-trigger", "data", allow_duplicate=True),
        Output("user-toast", "is_open", allow_duplicate=True),
        Output("user-toast", "children", allow_duplicate=True),
        Output("user-toast", "icon", allow_duplicate=True),
        Input("btn-confirm-delete-user", "n_clicks"),  
        State("user-delete-id", "data"),
        prevent_initial_call=True
    )
    def confirm_delete_user(n_clicks, user_id):

        if not n_clicks or not user_id:
            raise PreventUpdate

        service = UserService()

        try:
            service.delete_user(user_id)

            return (
                False,              # cerrar modal
                n_clicks,           # refresh tabla
                True,               # mostrar toast
                "User deleted successfully",
                "success"
            )

        except UserHasRolesException as e:
            logger.warning(f"User has roles: {e}")
            return (
                False,
                dash.no_update,
                True,
                str(e),
                "warning"
            )

        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return (
                False,
                dash.no_update,
                True,
                "Unexpected error deleting user",
                "danger"
            )

    @app.callback(
        Output("delete-user-modal", "is_open", allow_duplicate=True),
        Input("btn-cancel-delete-user", "n_clicks"),  
        prevent_initial_call=True
    )
    def cancel_delete_user(n):

        if not n:
            raise PreventUpdate

        return False