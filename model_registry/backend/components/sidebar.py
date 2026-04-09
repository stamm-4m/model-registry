import dash_bootstrap_components as dbc
from dash import dcc, html
from model_registry.backend.utils.utils_sidebar import get_user_role
import logging

logger = logging.getLogger(__name__)

def sidebar(session_data = None):
    if not session_data or not session_data.get("authenticated"):
        role, username = None, None
        is_authenticated = False
    else:
        role, username = get_user_role(session_data)
        is_authenticated = True

    is_admin = role and role[0] == "admin"
    # add nvigation items based on user role
    # Admin users see all links, regular users see only home and models, unauthenticated users see only help
    nav_items = [
            html.H4(f"Welcome, {username}",style={"color": "white"}) if is_authenticated else None,
            html.Hr(),
            dbc.NavLink(
                html.Span([html.Span("ML Soft Sensors", className="nav-text")], className="nav-item-content"),
                href="/",
                className="sidebar-link",
                active="exact",
            ),
            dbc.NavLink(
                html.Span([html.Span("Model Explainability", className="nav-text")], className="nav-item-content"),
                href="/model-explainability",
                className="sidebar-link",
                active="exact",
            ),
            html.Hr(),
            dbc.NavLink("Help", href="/help", className="sidebar-link", active="exact"),
            
        ]   
    # Admin users get an extra link to the admin page    
    if is_admin:
        nav_items.append(
            dbc.NavLink("Admin", href="/admin", className="sidebar-link", active="exact") 
        )

    return html.Div([
        
        dbc.Button(
            "☰",
            id="toggle-sidebar",
            className="toggle-btn",
            n_clicks=0
        ),
        html.Hr(),
        html.A(
            html.Img(
                src="/assets/ml_repo_logo.png",
                className="logo-slider"
            ),
            href="/"
        ),        
        dbc.Nav(
            [   
                item for item in nav_items if item is not None
            ],
            vertical=True,  # Ensures links are displayed one below the other
        )])
