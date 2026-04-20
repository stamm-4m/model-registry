from dash import Output, Input, State, ALL
import dash
from dash.exceptions import PreventUpdate
from model_registry.backend.core.exceptions import DepartmentInUseException
from model_registry.backend.services.department_service import DepartmentService
import logging
logger = logging.getLogger(__name__)

def register_delete_department_modal_callbacks(app):
    @app.callback(
        Output("delete-dept-modal", "is_open"),
        Output("dept-delete-id", "data"),
        Input({"type": "btn-delete-dept", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def open_delete_modal_dept(n_clicks_list):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        if not any(n and n > 0 for n in n_clicks_list):
            raise PreventUpdate

        dept_id = ctx.triggered_id["index"]

        return True, dept_id
    
    @app.callback(
        Output("delete-dept-modal", "is_open",allow_duplicate=True),
        Output("dept-refresh-trigger", "data", allow_duplicate=True),
        Output("dept-toast", "is_open", allow_duplicate=True),
        Output("dept-toast", "children", allow_duplicate=True),
        Output("dept-toast", "icon", allow_duplicate=True),
        Input("btn-confirm-delete", "n_clicks"),
        State("dept-delete-id", "data"),
        prevent_initial_call=True
    )
    def confirm_delete_dept(n_clicks, dept_id):
        if not n_clicks or not dept_id:
            raise PreventUpdate

        service = DepartmentService()

        try:
            service.delete_department(dept_id)

            return (
                False,              # cerrar modal
                n_clicks,           # refresh tabla
                True,               # mostrar toast
                "Department deleted successfully",
                "success"
            )
        
        except DepartmentInUseException as e:
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
                f"Error deleting organization: {str(e)}",
                "danger"
            )
    
    @app.callback(
        Output("delete-dept-modal", "is_open", allow_duplicate=True),
        Input("btn-cancel-delete", "n_clicks"),
        prevent_initial_call=True
    )
    def cancel_delete(n):
        return False