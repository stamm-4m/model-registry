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
        Input("btn-open-dept-modal", "n_clicks"),
        Input({"type": "btn-edit-dept", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def load_organizations_dropdown(n, n_list):
        service = OrganizationService()
        orgs = service.get_all_organizations()
        logger.debug(f"Loaded organizations for dropdown: {orgs}")
        return [
            {"label": org.name, "value": str(org.id)}
            for org in orgs
    ]

    @app.callback(
        Output("dept-name-input", "value"),
        Output("dept-org-dropdown", "value"),
        Output("dept-edit-id", "data",allow_duplicate=True),
        Output("dept-refresh-trigger", "data", allow_duplicate=True),
        Input("btn-save-dept", "n_clicks"),
        State("dept-name-input", "value"),
        State("dept-org-dropdown", "value"),
        State("dept-edit-id", "data"), 
        prevent_initial_call=True
    )
    def save_department(n, name, org_id, dept_id):

        if not n:
            raise PreventUpdate

        if not name or not org_id:
            raise PreventUpdate

        service = DepartmentService()

        if dept_id:
            logger.debug(f"Editing department with ID: {dept_id}")
            service.update_department(dept_id, name, org_id)
        else:
            logger.debug("Creating new department")
            service.create_department(name, org_id)

        logger.debug(f"Saved department: {name}, org_id: {org_id}")

        return "", None, None, n
    
    @app.callback(
        Output("department-modal", "is_open", allow_duplicate=True),
        Output("dept-name-input", "value", allow_duplicate=True),
        Output("dept-org-dropdown", "value", allow_duplicate=True),
        Output("dept-edit-id", "data"),
        Input({"type": "btn-edit-dept", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def open_edit_department(n_clicks_list):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        if not any(n and n > 0 for n in n_clicks_list):
            raise PreventUpdate

        dept_id = ctx.triggered_id["index"]

        service = DepartmentService()
        dept, org_id = service.get_department_with_org(dept_id)
        logger.debug(f"Editing department with ID: {dept_id}, name: {dept.name}, org_id: {org_id}")

        return True, dept.name, str(org_id), str(dept_id)