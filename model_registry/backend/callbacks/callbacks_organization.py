from dash import Output, Input, html, State, ALL
import dash_bootstrap_components as dbc


from model_registry.backend.services.organization_service import OrganizationService
from model_registry.backend.services.department_service import DepartmentService
from model_registry.backend.services.user_service import UserService
from model_registry.backend.services.laboratory_service import LaboratoryService
from model_registry.backend.utils.utils_laboratory import build_table_laboratories
from model_registry.backend.utils.utils_organization import build_table
from model_registry.backend.utils.utils_department import build_table_departments
from model_registry.backend.utils.utils_users import build_table_users
import logging
logger = logging.getLogger(__name__)


def register_organizations_table_callbacks(app):

    # Callback load organizations and departments
    @app.callback(
        Output("organizations-table", "children"),
        Input("org-refresh-trigger", "data"),
        State("user-session", "data"),
    )
    def load_organizations(refresh_data, session_data):
        service = OrganizationService()
        organizations, _ = service.get_all_organizations(session_data)
        logger.debug(f"Loaded organizations for table: {organizations}")

        if not organizations:
            return html.Div("No organizations found.")
        return build_table(organizations)
    
    @app.callback(
        Output("departments-table", "children"),
        Input("dept-refresh-trigger", "data"),
        State("user-session", "data"),
    )
    def load_departments(refresh_data, session_data):
        service = DepartmentService()
        departments, _ = service.get_all_departments_with_org(session_data)
        logger.debug(f"Loaded departments for table: {departments}")
        if not departments:
            return "No departments found."
        return build_table_departments(departments)
    
    @app.callback(
        Output("laboratories-table", "children"),
        Input("lab-refresh-trigger", "data"),
        State("user-session", "data"),
    )
    def load_laboratories(refresh_data, session_data):
        service = LaboratoryService()
        rows, _ = service.get_laboratory_all_with_dept(session_data)
        logger.debug(f"Loaded laboratories for table: {rows}")

        if not rows:
            return "No laboratories found."

        return build_table_laboratories(rows)
    

    @app.callback(
        Output("users-table", "children"),
        Input("user-refresh-trigger", "data"),
        State("user-session", "data"),
    )
    def load_users(refresh_data, session_data):
        service = UserService()
        rows, _ = service.get_all_users_with_department_and_laboratory(session_data)
        logger.debug(f"Loaded users for table: {rows}")
        if not rows:
            return "No users found."
        return build_table_users(rows)