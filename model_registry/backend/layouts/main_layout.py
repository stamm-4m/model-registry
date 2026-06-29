import dash_bootstrap_components as dbc
from dash import dcc, html

from model_registry.backend.components.sidebar import sidebar


# Partner logos shown in the persistent footer. INRAE colours / brand.
# All render uniformly white on the dark slate band via a CSS filter, so the
# source files can be light or colour versions.
_PARTNER_LOGOS = [
    {"src": "/assets/inrae.webp", "alt": "INRAE", "href": "https://www.inrae.fr"},
    {"src": "/assets/tbi.png", "alt": "Toulouse Biotechnology Institute",
     "href": "https://www.toulouse-biotechnology-institute.fr"},
    {"src": "/assets/bioind4-dark.png", "alt": "Bioindustry 4.0", "href": None},
]


def app_footer():
    """Persistent footer: partner logos + Mathematics cell credit."""
    logos = []
    for lg in _PARTNER_LOGOS:
        img = html.Img(src=lg["src"], alt=lg["alt"], title=lg["alt"],
                       className="app-footer-logo")
        logos.append(html.A(img, href=lg["href"], target="_blank") if lg["href"] else img)

    return html.Footer(
        [
            html.Div(logos, className="app-footer-logos"),
            html.Div(
                "Mathematics cell — Toulouse Biotechnology Institute (TBI)",
                className="app-footer-credit",
            ),
            html.Div("© 2026 STAMM — Model Registry", className="app-footer-copy"),
        ],
        className="app-footer",
    )


def main_layout(session_data=None):
    return dbc.Container([
        # Location component to monitor the URL
        #dcc.Location(id="url", refresh=False),  # Captures changes in the URL
        dbc.Row([
            dbc.Col(sidebar(session_data), className="sidebar", id="sidebar"),
            dbc.Col(
                [
                    html.Div(id="main-content", className="content"),
                    app_footer(),
                ]
            ),
        ])
    ], fluid=True)


def app_layout():
    return html.Div([
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
        html.Div(id="app-root")
    ])
