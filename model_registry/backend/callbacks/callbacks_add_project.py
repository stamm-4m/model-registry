import logging
import re

from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate

from model_registry.backend.models.user_model import list_users
from model_registry.backend.services.laboratory_service import LaboratoryService
from model_registry.backend.services.project_service import ProjectService
from model_registry.backend.utils.utils_projects import create_project_structure

logger = logging.getLogger(__name__)


def register_add_project_callbacks(app):
    @app.callback(
        Output("assigned-users", "options"),
        Input("assigned-users", "id"),
    )
    def load_users(_):
        try:
            users = list_users("user")
        except Exception as exc:  # legacy sqlite source -- non-fatal
            logger.warning("load_users failed: %s", exc)
            return []
        return [{"label": u["username"], "value": u["id"]} for u in users]

    @app.callback(
        Output("assigned-laboratory", "options"),
        Output("user-session", "data", allow_duplicate=True),
        Input("assigned-laboratory", "id"),
        State("user-session", "data"),
        prevent_initial_call="initial_duplicate",
    )
    def load_laboratories(_, session_data):
        if not session_data or not session_data.get("authenticated"):
            return [], no_update
        labs, session_data = LaboratoryService().get_laboratory_all(session_data)
        options = [{"label": lab.name, "value": str(lab.id)} for lab in (labs or [])]
        return options, session_data or no_update

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
        State("assigned-laboratory", "value"),
        prevent_initial_call=True,
    )
    def validate_project(n_clicks, project_id, name, start, end, lab_id):
        if not project_id or not name:
            return "Project ID and Project Name are required.", True, False, "", ""

        if not re.match(r"^P\d{4}$", project_id):
            return "Project ID must follow the format P0001.", True, False, "", ""

        if start and end and start > end:
            return "Start date must be earlier than end date.", True, False, "", ""

        if not lab_id:
            return (
                "You must assign the project to a laboratory so it appears "
                "in the project list.",
                True,
                False,
                "",
                "",
            )

        return (
            "",
            False,
            True,
            "Confirm Project Creation",
            "Are you sure you want to create this project?",
        )

    @app.callback(
        Output("project-form-alert", "children", allow_duplicate=True),
        Output("project-form-alert", "is_open", allow_duplicate=True),
        Output("confirm-project-modal", "is_open", allow_duplicate=True),
        Output("url", "pathname", allow_duplicate=True),
        Output("user-session", "data", allow_duplicate=True),
        Input("project-modal-ok", "n_clicks"),
        State("project-id", "value"),
        State("project-name", "value"),
        State("project-description", "value"),
        State("assigned-laboratory", "value"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def confirm_and_create(n_clicks, pid, name, desc, lab_id, session_data):
        if not n_clicks:
            raise PreventUpdate

        if not session_data or not session_data.get("authenticated"):
            return (
                "Your session expired. Please log in again.",
                True,
                False,
                no_update,
                no_update,
            )

        if not pid or not name or not lab_id:
            raise PreventUpdate  # validate_project already surfaced the error

        service = ProjectService()

        # 1) Persist in the API database (Postgres via FastAPI).
        project_dto, session_data = service.create_project(
            session_data,
            name=name,
            description=desc,
            project_id=pid,
        )
        if project_dto is None:
            logger.error("create_project failed for pid=%s name=%s", pid, name)
            return (
                f"Failed to create project '{pid}' in the registry. "
                "Check that the Project ID is unique.",
                True,
                False,
                no_update,
                session_data or no_update,
            )

        # 2) Link the project to the chosen laboratory so it shows up in
        #    /list_projects/ (which filters by user lab access).
        link, session_data = service.assign_project_to_lab(
            session_data,
            project_dto.id,
            lab_id,
        )
        if link is None:
            logger.error(
                "assign_project_to_lab failed for project=%s lab=%s",
                project_dto.id,
                lab_id,
            )
            return (
                "Project saved, but assigning it to the laboratory failed. "
                "Edit the project to fix the laboratory link.",
                True,
                False,
                no_update,
                session_data or no_update,
            )

        # 3) Materialize the on-disk folder structure + project_info.yaml
        #    so the YAML loader can serve metadata for this project.
        try:
            create_project_structure(pid, name, desc or "")
        except Exception as exc:
            logger.exception("create_project_structure failed: %s", exc)
            return (
                "Project registered in the database, but the on-disk folder "
                f"could not be created: {exc}",
                True,
                False,
                no_update,
                session_data or no_update,
            )

        return "", False, False, "/", session_data or no_update
