from dash import Input, Output, State
from model_registry.backend.pages.home import home_layout
from model_registry.backend.layouts.auth_layout import login_form
from model_registry.backend.pages.not_found import not_found_layout
from model_registry.backend.pages.model_upload import model_upload_layout
from model_registry.backend.pages.model_explainability import model_explainability_layout
from model_registry.backend.pages.edit_model import edit_model_layout

import logging

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
            return login_form()
        if pathname == "/" or pathname == "/home":
            return home_layout()
        elif pathname == "/model-upload":
            return model_upload_layout()
        elif pathname == "/model-explainability":
            return model_explainability_layout()
        elif pathname.startswith("/edit-model"):
            parts = pathname.strip("/").split("/")
            if len(parts) != 3:
                return not_found_layout()
            _, project_id, model_id = parts

            return edit_model_layout(project_id, model_id)
        else:
            return not_found_layout()
        
    @app.callback(
        Output("sidebar", "className"),
        Output("page-content", "className"),
        Output("main-content", "className"),
        Input("toggle-sidebar", "n_clicks"),
    )
    def toggle_sidebar(n_clicks):
        if n_clicks and n_clicks % 2 == 1:
            return "sidebar hidden", "content expanded", "main-content expanded"
        return "sidebar", "content", "content"
