import dash_bootstrap_components as dbc
from dash import dcc, html


def sidebar(session_data = None):
    is_admin = session_data and session_data.get("role") == "admin"
    is_authenticated = session_data and session_data.get("authenticated")

    return html.Div([
        # Stores data
        dcc.Store(id="user-session", data=session_data),
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
        html.Hr() if is_authenticated else None,
        html.H4(f"Welcome, {session_data.get('user')}",style={"color": "white"}) if is_authenticated else None,
        dbc.Nav(
            [   
                dbc.NavLink(
                    html.Span([html.Span("Models", className="nav-text")], className="nav-item-content"),
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
                dbc.NavLink("About us", href="/about-us", className="sidebar-link", active="exact"),
                dbc.NavLink("Help", href="/help", className="sidebar-link", active="exact"),
        
            ],
            vertical=True,  # Ensures links are displayed one below the other
        )])
