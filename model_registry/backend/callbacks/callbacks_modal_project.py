from dash import Output, Input, State, ALL
import dash
from dash.exceptions import PreventUpdate

from model_registry.backend.services.laboratory_service import LaboratoryService
from model_registry.backend.services.organization_service import OrganizationService
from model_registry.backend.services.department_service import DepartmentService
import logging

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
        prevent_initial_call=True
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
                True
            )
        return "", False, "", "primary", False

    @app.callback(
        Output("project-modal", "is_open"),
        Input("btn-open-proj-modal", "n_clicks"),
        Input("btn-close-proj-modal", "n_clicks"),
        Input("btn-save-proj", "n_clicks"),
        State("project-modal", "is_open"),
        prevent_initial_call=True
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
        Input("project-modal", "is_open"),
        prevent_initial_call=True
    )
    def load_organizations(is_open):
        if not is_open:
            raise PreventUpdate
        service = OrganizationService()
        orgs = service.get_all_organizations()
        options = [{"label": o.name, "value": str(o.id)} for o in orgs]
        return options

    @app.callback(
        Output("proj-dept-dropdown", "options", allow_duplicate=True),
        Output("proj-dept-dropdown", "disabled", allow_duplicate=True),
        Output("proj-dept-dropdown", "value", allow_duplicate=True),
        Output("proj-lab-dropdown", "value", allow_duplicate=True),
        Output("proj-lab-dropdown", "options", allow_duplicate=True),
        Output("proj-lab-dropdown", "disabled", allow_duplicate=True),
        Input("proj-org-dropdown", "value"),
        Input("proj-edit-id", "data"),
        State("proj-dept-dropdown", "value"),
        prevent_initial_call=True
    )
    def load_departments(org_id, edit_id, current_dept):
        if not org_id:
            return [], True, None, None, [], True
        service = DepartmentService()
        depts = service.get_by_organization(org_id)
        options = [{"label": d.name, "value": str(d.id)} for d in depts]
        # If editing, keep the current value
        return options, False, current_dept, None, [], True
    
    @app.callback(
        Output("proj-lab-dropdown", "options", allow_duplicate=True),
        Output("proj-lab-dropdown", "disabled", allow_duplicate=True),
        Output("proj-lab-dropdown", "value", allow_duplicate=True),
        Input("proj-dept-dropdown", "value"),
        Input("proj-edit-id", "data"),
        State("proj-lab-dropdown", "value"),
        prevent_initial_call=True
    )
    def load_labs(dept_id, edit_id, current_lab):
        if not dept_id:
            return [], True, None
        service = LaboratoryService()
        labs = service.get_by_department(dept_id)
        options = [{"label": l.name, "value": str(l.id)} for l in labs]
        # If editing, keep the current value
        return options, False, current_lab

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
        Input("btn-save-proj", "n_clicks"),
        State("proj-name-input", "value"),
        State("proj-description-input", "value"),
        State("proj-external-id", "value"),
        State("proj-lab-dropdown", "value"),
        State("proj-edit-id", "data"),
        prevent_initial_call=True
    )
    def save_project(n, name, description, external_id, lab_id, proj_id):
        if not n:
            raise PreventUpdate
        if not name or not lab_id:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                "Project name and laboratory are required.", True, "Error", "danger"
        service = ProjectService()
        from uuid import UUID
        try:
            if proj_id:
                logger.debug(f"Editing project {proj_id}")
                service.update_project(
                    project_id=proj_id,
                    name=name,
                    description=description,
                    external_id=external_id
                )
                # Update lab assignment if lab_id is provided
                if lab_id:
                    service.update_project_lab(proj_id, lab_id)
                toast_msg = "Project updated successfully."
                toast_header = "Success"
                toast_icon = "success"
            else:
                logger.debug("Creating project")
                project = service.create_project(
                    name=name,
                    description=description,
                    project_id=external_id
                )
                service.assign_project_to_lab(
                    project.id,
                    UUID(lab_id)
                )
                create_project_structure(
                    project_id=external_id,
                    project_name=name,
                    description=description
                )
                toast_msg = "Project created successfully."
                toast_header = "Success"
                toast_icon = "success"
            return "", "", "", None, None, None, None, n, toast_msg, True, toast_header, toast_icon
        except Exception as e:
            logger.error(f"Error saving project: {e}")
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
                f"Error: {str(e)}", True, "Error", "danger"
    
    @app.callback(
        Output("project-modal", "is_open", allow_duplicate=True),
        Output("proj-name-input", "value", allow_duplicate=True),
        Output("proj-description-input", "value", allow_duplicate=True),
        Output("proj-external-id", "value", allow_duplicate=True),
        Output("proj-org-dropdown", "value", allow_duplicate=True),
        Output("proj-dept-dropdown", "value", allow_duplicate=True),
        Output("proj-lab-dropdown", "value", allow_duplicate=True),
        Output("proj-edit-id", "data"),
        Input({"type": "btn-edit-proj", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def open_edit_project(n_clicks_list):

        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate

        if not any(n and n > 0 for n in n_clicks_list):
            raise PreventUpdate

        proj_id = ctx.triggered_id["index"]

        service = ProjectService()

        project, lab, dept, org = service.get_full_project(proj_id)

        logger.debug(f"Editing project {project.name}")

        return (
            True,
            project.name,
            project.description,
            project.project_id,
            str(org.id),
            str(dept.id),
            str(lab.id),
            str(proj_id)
        )

