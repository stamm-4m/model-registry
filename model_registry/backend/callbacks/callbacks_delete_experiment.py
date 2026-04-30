from dash import Output, Input, State, ALL
import dash
from dash.exceptions import PreventUpdate
from model_registry.backend.core.exceptions import DepartmentInUseException
from model_registry.backend.services.experiment_service import ExperimentService
import logging
logger = logging.getLogger(__name__)

def register_delete_experiment_modal_callbacks(app):
    @app.callback(
        Output("delete-exp-modal", "is_open"),
        Output("exp-delete-id", "data"),
        Input({"type": "btn-delete-exp", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def open_delete_modal_exp(n_clicks_list):
        logger.debug(f"Delete buttons clicked: {n_clicks_list}")
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        if not any(n and n > 0 for n in n_clicks_list):
            raise PreventUpdate
        exp_id = ctx.triggered_id["index"]
        return True, exp_id

    @app.callback(
        Output("delete-exp-modal", "is_open", allow_duplicate=True),
        Output("exp-refresh-trigger", "data", allow_duplicate=True),
        Output("exp-toast", "is_open", allow_duplicate=True),
        Output("exp-toast", "children", allow_duplicate=True),
        Output("exp-toast", "icon", allow_duplicate=True),
        Input("btn-confirm-delete", "n_clicks"),
        State("exp-delete-id", "data"),
        prevent_initial_call=True
    )
    def confirm_delete_exp(n_clicks, exp_id):
        if not n_clicks or not exp_id:
            raise PreventUpdate
        service = ExperimentService()
        try:
            service.delete_experiment(exp_id)
            return (
                False,              # cerrar modal
                n_clicks,           # refresh tabla
                True,               # mostrar toast
                "Experiment deleted successfully",
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
                f"Error deleting experiment: {str(e)}",
                "danger"
            )

    @app.callback(
        Output("delete-exp-modal", "is_open", allow_duplicate=True),
        Input("btn-cancel-delete", "n_clicks"),
        prevent_initial_call=True
    )
    def cancel_delete(n):
        return False