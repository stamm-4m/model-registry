import sqlite3
import re
from dash import html, dcc, Input, Output, State
import dash
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import logging
from model_registry.backend.models.project_model import insert_project
from model_registry.backend.models.user_model import list_users
from model_registry.backend.models.user_project_model import assign_user_to_project
logger = logging.getLogger(__name__)
def register_add_project_callbacks(app):
   
    @app.callback(
        Output("assigned-users", "options"),
        Input("assigned-users", "id"),
    )
    def load_users(_):
        users = list_users("user")
        logger.debug(f"Loaded users for assignment: {users}")
        return [{"label": u["username"], "value": u["id"]} for u in users]

    @app.callback(
        Output("project-form-alert", "children"),
        Output("project-form-alert", "is_open"),
        Output("confirm-project-modal", "is_open"),
        Output("project-modal-title", "children", allow_duplicate=True),
        Output("project-modal-body", "children", allow_duplicate=True),
        Input("open-confirm-modal", "n_clicks"),
        State("project-id", "value"),
        State("project-name", "value"),
        State("project-start-date", "value"),
        State("project-end-date", "value"),
        prevent_initial_call=True,
    )
    def validate_project(n_clicks, project_id, name, start, end):
        if not project_id or not name:
            return "Project ID and Project Name are required.", True, False, "", ""

        if not re.match(r"^P\d{4}$", project_id):
            return "Project ID must follow the format P0001.", True, False, "", ""

        if start and end and start > end:
            return "Start date must be earlier than end date.", True, False,"", ""

        return ("", False, True,
        "Confirm Project Creation",
        "Are you sure you want to create this project?")

    @app.callback(
        Output("confirm-project-modal", "is_open", allow_duplicate=True),
        Output("project-modal-title", "children"),
        Output("project-modal-body", "children"),
        Input("confirm-project", "n_clicks"),
        State("project-id", "value"),
        State("project-name", "value"),
        State("project-description", "value"),
        State("project-coordinator", "value"),
        State("project-start-date", "value"),
        State("project-end-date", "value"),
        State("assigned-users", "value"),
        prevent_initial_call=True,
    )
    def save_project_and_show_dialog(
        confirm,
        pid, name, desc, coord, start, end, users
    ):
        if not confirm:
            raise PreventUpdate

        insert_project(pid, name, desc, coord, start, end)

        for user_id in users or []:
            assign_user_to_project(user_id, pid)

        return (
            True,
            "Project Created",
            "The project was created successfully."
        )

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Input("project-modal-ok", "n_clicks"),
        prevent_initial_call=True,
    )
    def redirect_to_home(n):
        if n:
            return "/"
        raise PreventUpdate
