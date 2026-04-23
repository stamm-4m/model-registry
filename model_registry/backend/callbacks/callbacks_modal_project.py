from dash import Output, Input, State, ALL
import dash
from dash.exceptions import PreventUpdate

from model_registry.backend.services.laboratory_service import LaboratoryService
from model_registry.backend.services.organization_service import OrganizationService
from model_registry.backend.services.department_service import DepartmentService
import logging

from model_registry.backend.services.project_service import ProjectService
logger = logging.getLogger(__name__)



def register_project_modal_callbacks(app):

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

    @app.callback(
        Output("proj-dept-dropdown", "options", allow_duplicate=True),
        Output("proj-dept-dropdown", "disabled",allow_duplicate=True),
        Output("proj-dept-dropdown", "value", allow_duplicate=True),
        Output("proj-lab-dropdown", "value", allow_duplicate=True),
        Output("proj-lab-dropdown", "options", allow_duplicate=True),
        Output("proj-lab-dropdown", "disabled", allow_duplicate=True),
        Input("proj-org-dropdown", "value"),
        prevent_initial_call=True
    )
    def load_departments(org_id):
        if not org_id:
            return [], True, None, None, [], True

        service = DepartmentService()
        depts = service.get_by_organization(org_id)

        options = [{"label": d.name, "value": str(d.id)} for d in depts]

        return options, False, None, None, [], True
    
    @app.callback(
        Output("proj-lab-dropdown", "options", allow_duplicate=True),
        Output("proj-lab-dropdown", "disabled", allow_duplicate=True),
        Output("proj-lab-dropdown", "value", allow_duplicate=True),
        Input("proj-dept-dropdown", "value"),
        prevent_initial_call=True
    )
    def load_labs(dept_id):
        if not dept_id:
            return [], True, None

        service = LaboratoryService()
        labs = service.get_by_department(dept_id)

        options = [{"label": l.name, "value": str(l.id)} for l in labs]

        return options, False, None

    @app.callback(
        Output("proj-name-input", "value", allow_duplicate=True),
        Output("proj-description-input", "value", allow_duplicate=True),
        Output("proj-org-dropdown", "value", allow_duplicate=True),
        Output("proj-dept-dropdown", "value", allow_duplicate=True),
        Output("proj-lab-dropdown", "value", allow_duplicate=True),
        Output("proj-edit-id", "data", allow_duplicate=True),
        Output("proj-refresh-trigger", "data", allow_duplicate=True),
        Input("btn-save-proj", "n_clicks"),
        State("proj-name-input", "value"),
        State("proj-description-input", "value"),
        State("proj-lab-dropdown", "value"),
        State("proj-edit-id", "data"),
        prevent_initial_call=True
    )
    def save_project(n, name, description, lab_id, proj_id):

        if not n:
            raise PreventUpdate

        if not name or not lab_id:
            raise PreventUpdate

        service = ProjectService()

        from uuid import UUID

        if proj_id:
            logger.debug(f"Editing project {proj_id}")
            service.update_project(
                project_id=UUID(proj_id),
                name=name,
                description=description
            )
        else:
            logger.debug("Creating project")
            project = service.create_project(
                name=name,
                description=description
            )

            service.assign_project_to_lab(
                project.id,
                UUID(lab_id)
            )

        return "", "", None, None, None, None, n
    
    @app.callback(
        Output("project-modal", "is_open", allow_duplicate=True),
        Output("proj-name-input", "value", allow_duplicate=True),
        Output("proj-description-input", "value", allow_duplicate=True),
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
            str(org.id),
            str(dept.id),
            str(lab.id),
            str(proj_id)
        )
    
