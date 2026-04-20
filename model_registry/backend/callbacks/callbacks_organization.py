from dash import Output, Input, html
import dash_bootstrap_components as dbc


from model_registry.backend.services.organization_service import OrganizationService
from model_registry.backend.services.department_service import DepartmentService
from model_registry.backend.services.user_service import UserService
from model_registry.backend.utils.utils_organization import build_table
from model_registry.backend.utils.utils_department import build_table_departments
from model_registry.backend.utils.utils_users import build_table_users


def register_organizations_table_callbacks(app):

    # Callback load organizations and departments
    @app.callback(
        Output("organizations-table", "children"),
        Input("org-refresh-trigger", "data")
    )
    def load_organizations(refresh_data):
        service = OrganizationService()
        organizations = service.get_all_organizations()

        if not organizations:
            return html.Div("No organizations found.")

        
        return build_table(organizations)
    
    @app.callback(
        Output("departments-table", "children"),
        Input("dept-refresh-trigger", "data")
    )
    def load_departments(_):
        service = DepartmentService()
        rows = service.get_department_all()

        if not rows:
            return "No departments found."

        return build_table_departments(rows)
    

    @app.callback(
        Output("users-table", "children"),
        Input("user-refresh-trigger", "data")
    )
    def load_users(_):
        service = UserService()
        rows = service.get_all_users()

        if not rows:
            return "No users found."

        return build_table_users(rows)