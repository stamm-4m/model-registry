import logging
import dash
from dash import Input, Output, State

from model_registry.backend.layouts.auth_layout import login_form
from model_registry.backend.pages.add_project import add_project_layout
from model_registry.backend.pages.details_model import details_model_layout
from model_registry.backend.pages.edit_model import edit_model_layout
from model_registry.backend.pages.help import help_layout
from model_registry.backend.pages.home import home_layout
from model_registry.backend.pages.dynamic_models import dynamic_models_layout
from model_registry.backend.pages.departments import departments_layout
from model_registry.backend.pages.organizations import organizations_layout
from model_registry.backend.pages.users import users_layout
from model_registry.backend.pages.model_explainability import (
    model_explainability_layout,
)
from model_registry.backend.pages.model_upload import model_upload_layout
from model_registry.backend.pages.not_found import not_found_layout
from model_registry.backend.pages.upload_model_ibisba import (
    add_upload_model_ibisba_layout,
)
from model_registry.backend.services.project_service import list_projects

logger = logging.getLogger(__name__)

def register_sidebar_callbacks(app):

    @app.callback(
        Output("main-content", "children"),
        Input("url", "pathname"),
        State("user-session", "data")
    )
    def display_page(pathname, session_data):
        logger.debug(f"Navigating to {pathname} with session {session_data}")
        if not session_data or not session_data.get("authenticated"):
            logger.debug("User not authenticated, redirecting to login")
            return login_form()
        
        if pathname == "/" or pathname == "/home":
            projects_options, session_data = list_projects(session_data)
            if projects_options is None:
                return login_form()
            return home_layout(projects_options)
        
        if pathname.startswith("/model-upload-ibisba"):
            parts = pathname.strip("/").split("/")
            if len(parts) != 3:
                return not_found_layout()
            _, project_id, model_id = parts
            return add_upload_model_ibisba_layout(project_id, model_id)
        
        elif pathname.startswith("/model-upload"):
            parts = pathname.strip("/").split("/")
            if len(parts) != 2:
                return not_found_layout()
            _, project_id = parts
            return model_upload_layout(project_id)
        
        elif pathname == "/model-explainability":
            return model_explainability_layout()
        
        elif pathname == "/dynamic-models":
            return dynamic_models_layout()
        
        elif pathname == "/departments":
            return departments_layout()
        
        elif pathname == "/users":
            return users_layout()
        
        elif pathname == "/organizations":
            return organizations_layout()
        
        elif pathname.startswith("/edit-model"):
            parts = pathname.strip("/").split("/")
            if len(parts) != 3:
                return not_found_layout()
            _, project_id, model_id = parts

            return edit_model_layout(project_id, model_id)
        
        elif pathname == "/add-project":
            return add_project_layout()
        
        elif pathname.startswith("/details-model"):
            parts = pathname.strip("/").split("/")
            if len(parts) != 3:
                return not_found_layout()
            _, project_id, model_id = parts
            return details_model_layout(project_id, model_id)
        
        elif pathname == "/help":
            return help_layout()
        
        else:
            return not_found_layout()

    @app.callback(
        Output("sidebar", "className"),
        Output("app-root", "className"),
        Output("main-content", "className"),
        Input("toggle-sidebar", "n_clicks"),
    )
    def toggle_sidebar(n_clicks):
        logger.debug(f"Toggle sidebar clicked {n_clicks} times")
        if n_clicks and n_clicks % 2 == 1:
            return "sidebar hidden", "content expanded", "main-content expanded"
        return "sidebar", "content", "content"
    
    @app.callback(
        Output("admin-collapse", "is_open"),
        Input("admin-toggle", "n_clicks"),
        Input("url", "pathname"),
        State("admin-collapse", "is_open"),
    )
    def toggle_admin_menu(n, pathname, is_open):
        ctx = dash.callback_context
        trigger = ctx.triggered_id

        admin_routes = ["/organizations", "/departments", "/users"]
        # Si la ruta es una de las rutas admin, abrir el menú
        if pathname in admin_routes:
            return True

        # Si el trigger es el toggle del admin, alternar el estado
        if trigger == "admin-toggle":
            if not n:
                return is_open
            return not is_open

        return is_open

    @app.callback(
    [
        Output("organization-link", "className"), 
        Output("department-link", "className"),
        Output("users-link", "className"),
    ], 
    Input("url", "pathname"),
    )
    def update_admin_links(pathname):
        base = "sidebar-link ms-4"

        return (
            f"{base} active" if pathname == "/organizations" else base,
            f"{base} active" if pathname == "/departments" else base,
            f"{base} active" if pathname == "/users" else base,
        )