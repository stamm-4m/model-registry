import dash_bootstrap_components as dbc
from dash import dcc, html

from model_registry.backend.components.sidebar import sidebar


def main_layout(session_data=None):
    return dbc.Container(
        [
            # Location component to monitor the URL
            # dcc.Location(id="url", refresh=False),  # Captures changes in the URL
            dbc.Row(
                [
                    dbc.Col(sidebar(session_data), className="sidebar", id="sidebar"),
                    dbc.Col(html.Div(id="main-content", className="content")),
                ]
            )
        ],
        fluid=True,
    )


def app_layout():
    return html.Div(
        [
            dcc.Location(id="url", refresh=False),
            dcc.Store(id="models-grid-data"),
            dcc.Store(id="user-session", storage_type="session"),
            # Refresh triggers (kept always-mounted so callbacks targeting them
            # don't fail when the corresponding page isn't currently displayed).
            dcc.Store(id="org-refresh-trigger"),
            dcc.Store(id="dept-refresh-trigger"),
            dcc.Store(id="lab-refresh-trigger"),
            dcc.Store(id="user-refresh-trigger"),
            dcc.Store(id="proj-refresh-trigger"),
            dcc.Store(id="exp-refresh-trigger"),
            # Stores data
            html.Div(id="app-root"),
        ]
    )
