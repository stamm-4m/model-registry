from dash import Output, Input, State, ALL
import dash
from dash.exceptions import PreventUpdate

from model_registry.backend.services.organization_service import OrganizationService
from model_registry.backend.services.department_service import DepartmentService
import logging
logger = logging.getLogger(__name__)



def register_department_modal_callbacks(app):

    @app.callback(
        Output("department-modal", "is_open"),
        Input("btn-open-dept-modal", "n_clicks"),
        Input("btn-close-dept-modal", "n_clicks"),
        Input("btn-save-dept", "n_clicks"),
        State("department-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_department_modal(open_click, close_click, save_click, is_open):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        trigger = ctx.triggered_id

        if trigger == "btn-open-dept-modal":
            return True

        elif trigger in ["btn-close-dept-modal", "btn-save-dept"]:
            return False

        return is_open

    @app.callback(
        Output("dept-org-dropdown", "options"),
        Output("user-session", "data", allow_duplicate=True),
        Input("btn-open-dept-modal", "n_clicks"),
        Input({"type": "btn-edit-dept", "index": ALL}, "n_clicks"),
        State("user-session", "data"),
        prevent_initial_call=True
    )
    def load_organizations_dropdown(n, n_list, session_data):
        service = OrganizationService()
        orgs, session_data = service.get_all_organizations(session_data)
        logger.debug(f"Loaded organizations for dropdown: {orgs}")
        return [
            {"label": org.name, "value": str(org.id)}
            for org in orgs
    ], session_data

    @app.callback(
        Output("dept-name-input", "value"),
        Output("dept-org-dropdown", "value"),
        Output("dept-edit-id", "data",allow_duplicate=True),
        Output("dept-refresh-trigger", "data", allow_duplicate=True),
        Output("user-session", "data", allow_duplicate=True),
        Input("btn-save-dept", "n_clicks"),
        State("dept-name-input", "value"),
        State("dept-org-dropdown", "value"),
        State("dept-edit-id", "data"),
        State("user-session", "data"),
        prevent_initial_call=True
    )
    def save_department(n, name, org_id, dept_id, session_data):

        if not n:
            raise PreventUpdate

        if not name or not org_id:
            raise PreventUpdate

        service = DepartmentService()
        if dept_id:
            logger.debug(f"Editing department with ID: {dept_id}")
            _, session_data = service.update_department(session_data, dept_id, name, org_id)
        else:
            logger.debug("Creating new department")
            _, session_data = service.create_department(session_data, name, org_id)
        logger.debug(f"Saved department: {name}, org_id: {org_id}")
        return "", None, None, n, session_data
    
    @app.callback(
        Output("department-modal", "is_open", allow_duplicate=True),
        Output("dept-name-input", "value", allow_duplicate=True),
        Output("dept-org-dropdown", "value", allow_duplicate=True),
        Output("dept-edit-id", "data"),
        Output("user-session", "data", allow_duplicate=True),
        Input({"type": "btn-edit-dept", "index": ALL}, "n_clicks"),
        State("user-session", "data"),
        prevent_initial_call=True
    )
    def open_edit_department(n_clicks_list, session_data):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        if not any(n and n > 0 for n in n_clicks_list):
            raise PreventUpdate

        dept_id = ctx.triggered_id["index"]

        service = DepartmentService()
        dept, session_data = service.get_department(session_data, dept_id)
        if dept is None:
            raise PreventUpdate
        org_id, session_data = service.get_organization_id_for_department(session_data, dept_id)
        logger.debug(f"Editing department with ID: {dept_id}, name: {dept.name}, org_id: {org_id}")
        return True, dept.name, str(org_id) if org_id else None, str(dept_id), session_data