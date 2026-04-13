import logging

import dash
from dash import ALL, Input, Output, State, html

from model_registry.backend.layouts.auth_layout import login_form
from model_registry.backend.layouts.main_layout import main_layout
from model_registry.backend.services.auth_service import login_request

logger = logging.getLogger(__name__)

def register_auth_callbacks(app):

    @app.callback(
        Output("app-root", "children"),
        Output("user-session", "data"),
        Input("url", "pathname"),
        Input({"type": "logout-button", "index": ALL}, "n_clicks"),
        Input("user-session", "data"),
        prevent_initial_call=True
    )
    def display_main_page(pathname, logout_clicks, session_data):
        logger.debug(f"URL changed to {pathname} with session {session_data} and logout clicks {logout_clicks}")
        ctx = dash.callback_context

        if not ctx.triggered:
            #raise dash.exceptions.PreventUpdate
            if not session_data or not session_data.get("authenticated"):
                return login_form(), {}
            return main_layout(session_data), session_data

        trigger = ctx.triggered_id

        if isinstance(trigger, dict) and trigger.get("type") == "logout-button":
            print(">> Logout ejecutado")
            return login_form(), {}

        # Si no está autenticado
        if not session_data or not session_data.get("authenticated"):
            return login_form(), {}

        # Navegación normal, permanece en layout principal
        return main_layout(session_data), session_data

    @app.callback(
        Output("user-session", "data",allow_duplicate=True),
        Output("app-root", "children",allow_duplicate=True),
        Output("login-message", "children"),
        Input("login-button", "n_clicks"),
        State("login-username", "value"),
        State("login-password", "value"),
        prevent_initial_call=True
    )
    def handle_login(n_clicks, username, password):
        logger.debug(f"Login attempt with username={username} and password={'*' * len(password) if password else None}")
        if not username or not password:
            return {}, login_form(), "Username or password none"

        username = username.strip()
        password = password.strip()
        auth_response  = login_request(username, password)

        if auth_response:
            #session_data = {
            #    "authenticated": True, "user": auth_response["username"], "role": auth_response["role"]
            #}
            session_data = {
                "authenticated": True,
                "access_token": auth_response["access_token"],
                "refresh_token": auth_response["refresh_token"]
            }
            return session_data, main_layout(session_data), ""
        
        return {}, login_form(), "Username o password incorrects"


    @app.callback(
        Output("login-password", "type"),
        Output("toggle-password", "children"),
        Input("toggle-password", "n_clicks"),
        State("login-password", "type"),
    )
    def toggle_password_visibility(n_clicks, current_type):
        if n_clicks == 0:
            raise dash.exceptions.PreventUpdate

        # Toggle password visibility
        new_type = "text" if current_type == "password" else "password"
        new_icon = html.I(className="bi bi-eye-slash-fill") if new_type == "text" else html.I(className="bi bi-eye-fill")

        return new_type, new_icon
