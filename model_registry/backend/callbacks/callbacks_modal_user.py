from dash import Output, Input, State, ALL
import dash
from dash.exceptions import PreventUpdate
from dash import no_update
from model_registry.backend.core.exceptions import UserEmailAlreadyExistsException
from model_registry.backend.services.user_service import UserService
from model_registry.backend.services.department_service import DepartmentService
import logging
import time
logger = logging.getLogger(__name__)



def register_user_modal_callbacks(app):

    @app.callback(
        Output("user-modal", "is_open"),
        Input("btn-open-user-modal", "n_clicks"),
        Input("btn-close-user-modal", "n_clicks"),
        Input("btn-save-user", "n_clicks"),
        State("user-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_user_modal(open_click, close_click, save_click, is_open):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        trigger = ctx.triggered_id

        if trigger == "btn-open-user-modal":
            return True

        elif trigger in ["btn-close-user-modal", "btn-save-user"]:
            return False

        return is_open

    @app.callback(
        Output("user-dept-dropdown", "options"),
        Input("btn-open-user-modal", "n_clicks"),
        Input({"type": "btn-edit-dept", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def load_departments_dropdown(n, n_list):
        service = DepartmentService()
        departments = service.get_department_all()
        logger.debug(f"Loaded departments for dropdown: {departments}")
        return [
            {"label": dept.name, "value": str(dept.id)}
            for dept, _ in departments
        ]

    @app.callback(
        Output("user-name-input", "value"),
        Output("user-email-input", "value"),
        Output("user-password-input", "value"),
        Output("user-dept-dropdown", "value"),
        Output("user-lab-dropdown", "value"),
        Output("user-edit-id", "data", allow_duplicate=True),
        Output("user-refresh-trigger", "data", allow_duplicate=True),
        Output("user-toast", "is_open", allow_duplicate=True),
        Output("user-toast", "children", allow_duplicate=True),
        Output("user-toast", "icon", allow_duplicate=True),
        Input("btn-save-user", "n_clicks"),
        State("user-name-input", "value"),
        State("user-email-input", "value"),
        State("user-password-input", "value"),
        State("user-dept-dropdown", "value"),
        State("user-lab-dropdown", "value"),
        State("user-edit-id", "data"),
        prevent_initial_call=True
    )
    def save_user(n, name, email, password, dept_id, lab_id, user_id):

        if not n:
            raise PreventUpdate

        if not name or not email or not password or not dept_id or not lab_id:
            return (
                no_update, no_update, no_update, no_update, no_update, no_update, no_update,
                True,
                "All fields are required",
                "warning"
            )

        service = UserService()
        try:
            if user_id:
                logger.debug(f"Editing user with ID: {user_id}")
                service.update_user(user_id, name, email, password, lab_id)
            else:
                logger.debug("Creating new user")
                service.create_user(name, email, password, lab_id)

            logger.debug(f"Saved user: {name}, email: {email}")

            return ("", "", "", None, None, None, time.time(),
                    True,
                    "User saved successfully",
                    "success"
                )
        except UserEmailAlreadyExistsException as e:
            logger.warning(f"Email already exists: {e}")
            return (
                no_update, no_update, no_update, no_update, no_update, no_update, no_update,
                True,
                str(e),
                "warning"
            )
        except Exception as e:
            logger.error(f"Error saving user: {e}")
            return (
                no_update, no_update, no_update, no_update, no_update, no_update, no_update,
                True,
                "Unexpected error saving user",
                "danger"
            )
    
    @app.callback(
        Output("user-modal", "is_open", allow_duplicate=True),
        Output("user-name-input", "value", allow_duplicate=True),
        Output("user-email-input", "value", allow_duplicate=True),
        Output("user-dept-dropdown", "value", allow_duplicate=True),
        Output("user-edit-id", "data"),
        Input({"type": "btn-edit-user", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def open_edit_user(n_clicks_list):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        if not any(n and n > 0 for n in n_clicks_list):
            raise PreventUpdate

        user_id = ctx.triggered_id["index"]

        service = UserService()
        user = service.get_user(user_id)
        logger.debug(f"Editing user with ID: {user_id}, name: {user.full_name}, email: {user.email}")
        lab_id = service.get_lab_id_by_user_id(user_id)
        dept_id = service.get_dept_id_by_user_id(user_id)

        return True, user.full_name, user.email, str(dept_id), user_id