import dash_bootstrap_components as dbc
from dash import dcc, html
from model_registry.backend.utils.utils_sidebar import get_user_role, get_user_permissions
import logging

logger = logging.getLogger(__name__)

def sidebar(session_data = None):
    if not session_data or not session_data.get("authenticated"):
        role, username = None, None
        is_authenticated = False
        permissions = set()
    else:
        role, username = get_user_role(session_data)
        permissions = get_user_permissions(session_data)
        is_authenticated = True

    is_super_admin = role and "super_admin" in role
    # Protege rutas según permisos
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
            html.Span([html.Span("Dynamic Models", className="nav-text")], className="nav-item-content"),
            href="/dynamic-models",
            className="sidebar-link",
            active="exact",
        ),
        html.Hr(),
        dbc.NavLink("Help", href="/help", className="sidebar-link", active="exact"),
    ]
    # Solo Super Admin ve opciones de Admin
    if is_super_admin:
        nav_items.extend([
            dbc.NavLink(
                html.Span(
                    html.Span("Admin", className="nav-text"),
                    className="nav-item-content"
                ),
                href="#",
                className="sidebar-link",
                id="admin-toggle",
            ),
            dbc.Collapse(
                [
                    dbc.NavLink("Organization & People", href="/organizations", className="sidebar-link ms-4", id="organization-link"),
                    dbc.NavLink("Projects", href="/projects", className="sidebar-link ms-4", id="project-link")
                ],
                id="admin-collapse",
                is_open=False
            )
        ])
    if is_authenticated:
        nav_items.append(
            dbc.NavLink(
                "Logout",
                id={"type": "logout-button", "index": 0},
                className="sidebar-link",
                href="",
                n_clicks=0
            )
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
