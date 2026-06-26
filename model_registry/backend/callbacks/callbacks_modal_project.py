import logging

import dash
from dash import ALL, Input, Output, State
from dash.exceptions import PreventUpdate

from model_registry.backend.services.department_service import DepartmentService
from model_registry.backend.services.laboratory_service import LaboratoryService
from model_registry.backend.services.organization_service import OrganizationService
from model_registry.backend.services.project_service import ProjectService
from model_registry.backend.utils.utils_projects import create_project_structure

logger = logging.getLogger(__name__)


def register_project_modal_callbacks(app):
    @app.callback(
        Output("proj-toast", "children"),
        Output("proj-toast", "is_open"),
        Output("proj-toast", "header"),
        Output("proj-toast", "icon"),
        Output("btn-save-proj", "disabled"),
        Input("proj-external-id", "n_blur"),
        State("proj-external-id", "value"),
        prevent_initial_call=True,
    )
    def validate_external_id(n_blur, external_id):
        logger.debug(f"Validating external ID: {external_id}")
        import re

        if not external_id or not re.fullmatch(r"P\d{3,}", external_id):
            return (
                "Format invalid, project ID should be in the format P001, P002, ...",
                True,
                "Format invalid",
                "danger",
                True,
            )
        return "", False, "", "primary", False

    @app.callback(
        Output("project-modal", "is_open"),
        Input("btn-open-proj-modal", "n_clicks"),
        Input("btn-close-proj-modal", "n_clicks"),
        Input("btn-save-proj", "n_clicks"),
        State("project-modal", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_project_modal(open_click, close_click, save_click, is_open):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        trigger = ctx.triggered_id

        if trigger == "btn-open-proj-modal":
            return True

        elif trigger in ["btn-close-proj-modal", "btn-save-proj"]:
            return False

        return is_open

    # Load organizations for dropdown when modal opens
    @app.callback(
        Output("proj-org-dropdown", "options"),
        Output("user-session", "data", allow_duplicate=True),
        Input("project-modal", "is_open"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def load_organizations(is_open, session_data):
        if not is_open:
            raise PreventUpdate
        service = OrganizationService()
        orgs, session_data = service.get_all_organizations(session_data)
        options = [{"label": o.name, "value": str(o.id)} for o in orgs]
        return options, session_data

    @app.callback(
        Output("proj-dept-dropdown", "options", allow_duplicate=True),
        Output("proj-dept-dropdown", "disabled", allow_duplicate=True),
        Output("proj-dept-dropdown", "value", allow_duplicate=True),
        Output("proj-lab-dropdown", "value", allow_duplicate=True),
        Output("proj-lab-dropdown", "options", allow_duplicate=True),
        Output("proj-lab-dropdown", "disabled", allow_duplicate=True),
        Output("user-session", "data", allow_duplicate=True),
        Input("proj-org-dropdown", "value"),
        Input("proj-edit-id", "data"),
        State("proj-dept-dropdown", "value"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def load_departments(org_id, edit_id, current_dept, session_data):
        if not org_id:
            return [], True, None, None, [], True, session_data
        service = DepartmentService()
        depts, session_data = service.get_departments_by_organization(
            session_data, org_id
        )
        options = [{"label": d.name, "value": str(d.id)} for d in depts]
        return options, False, current_dept, None, [], True, session_data

    @app.callback(
        Output("proj-lab-dropdown", "options", allow_duplicate=True),
        Output("proj-lab-dropdown", "disabled", allow_duplicate=True),
        Output("proj-lab-dropdown", "value", allow_duplicate=True),
        Output("user-session", "data", allow_duplicate=True),
        Input("proj-dept-dropdown", "value"),
        Input("proj-edit-id", "data"),
        State("proj-lab-dropdown", "value"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def load_labs(dept_id, edit_id, current_lab, session_data):
        if not dept_id:
            return [], True, None, session_data
        service = LaboratoryService()
        labs, session_data = service.get_by_department(session_data, dept_id)
        options = [{"label": l.name, "value": str(l.id)} for l in labs]
        # If editing, keep the current value
        return options, False, current_lab, session_data

    @app.callback(
        Output("proj-name-input", "value", allow_duplicate=True),
        Output("proj-description-input", "value", allow_duplicate=True),
        Output("proj-external-id", "value", allow_duplicate=True),
        Output("proj-org-dropdown", "value", allow_duplicate=True),
        Output("proj-dept-dropdown", "value", allow_duplicate=True),
        Output("proj-lab-dropdown", "value", allow_duplicate=True),
        Output("proj-edit-id", "data", allow_duplicate=True),
        Output("proj-refresh-trigger", "data", allow_duplicate=True),
        Output("proj-toast", "children", allow_duplicate=True),
        Output("proj-toast", "is_open", allow_duplicate=True),
        Output("proj-toast", "header", allow_duplicate=True),
        Output("proj-toast", "icon", allow_duplicate=True),
        Output("user-session", "data", allow_duplicate=True),
        Input("btn-save-proj", "n_clicks"),
        State("proj-name-input", "value"),
        State("proj-description-input", "value"),
        State("proj-external-id", "value"),
        State("proj-lab-dropdown", "value"),
        State("proj-edit-id", "data"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def save_project(n, name, description, external_id, lab_id, proj_id, session_data):
        if not n:
            raise PreventUpdate
        if not name or not lab_id:
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                "Project name and laboratory are required.",
                True,
                "Error",
                "danger",
                session_data,
            )
        service = ProjectService()
        from uuid import UUID

        try:
            if proj_id:
                logger.debug(f"Editing project {proj_id}")
                _, session_data = service.update_project(
                    session_data,
                    project_id=proj_id,
                    name=name,
                    description=description,
                    external_id=external_id,
                )
                # Update lab assignment if lab_id is provided
                if lab_id:
                    _, session_data = service.update_project_lab(
                        session_data, proj_id, lab_id
                    )
                toast_msg = "Project updated successfully."
                toast_header = "Success"
                toast_icon = "success"
            else:
                logger.debug("Creating project")
                project, session_data = service.create_project(
                    session_data,
                    name=name,
                    description=description,
                    project_id=external_id,
                )
                if project is None or project.id is None:
                    raise Exception(
                        "Project creation failed (API returned no payload)."
                    )
                _, session_data = service.assign_project_to_lab(
                    session_data, project.id, UUID(lab_id)
                )
                create_project_structure(
                    project_id=external_id, project_name=name, description=description
                )
                toast_msg = "Project created successfully."
                toast_header = "Success"
                toast_icon = "success"
            return (
                "",
                "",
                "",
                None,
                None,
                None,
                None,
                n,
                toast_msg,
                True,
                toast_header,
                toast_icon,
                session_data,
            )
        except Exception as e:
            logger.error(f"Error saving project: {e}")
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                f"Error: {str(e)}",
                True,
                "Error",
                "danger",
                session_data,
            )

    @app.callback(
        Output("project-modal", "is_open", allow_duplicate=True),
        Output("proj-name-input", "value", allow_duplicate=True),
        Output("proj-description-input", "value", allow_duplicate=True),
        Output("proj-external-id", "value", allow_duplicate=True),
        Output("proj-org-dropdown", "value", allow_duplicate=True),
        Output("proj-dept-dropdown", "value", allow_duplicate=True),
        Output("proj-lab-dropdown", "value", allow_duplicate=True),
        Output("proj-edit-id", "data"),
        Output("user-session", "data", allow_duplicate=True),
        Input({"type": "btn-edit-proj", "index": ALL}, "n_clicks"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def open_edit_project(n_clicks_list, session_data):
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        if not any(n and n > 0 for n in n_clicks_list):
            raise PreventUpdate

        proj_id = ctx.triggered_id["index"]

        service = ProjectService()

        full, session_data = service.get_full_project(session_data, proj_id)

        if full is None:
            raise PreventUpdate

        project = full.project
        lab = full.laboratory
        dept = full.department
        org = full.organization

        logger.debug(f"Editing project {project.name}")

        return (
            True,
            project.name,
            project.description,
            project.project_id,
            str(org.id) if org and org.id else None,
            str(dept.id) if dept and dept.id else None,
            str(lab.id) if lab and lab.id else None,
            str(proj_id),
            session_data,
        )
