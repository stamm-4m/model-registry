import dash_bootstrap_components as dbc
from dash import dcc, html
from model_registry.backend.utils.utils_sidebar import get_user_role, get_user_permissions
import logging

logger = logging.getLogger(__name__)


def _nav_link(label, href, icon=None, link_id=None, indent=False):
    """Helper to build a styled nav link with optional icon."""
    children = []
    if icon:
        children.append(html.I(className=f"bi {icon} sidebar-icon"))
    children.append(html.Span(label, className="nav-text"))
    kwargs = dict(
        href=href,
        className="sidebar-link" + (" sidebar-link-sub" if indent else ""),
        active="exact",
    )
    if link_id is not None:
        kwargs["id"] = link_id
    return dbc.NavLink(html.Span(children, className="nav-item-content"), **kwargs)


def sidebar(session_data=None):
    if not session_data or not session_data.get("authenticated"):
        role, username = None, None
        is_authenticated = False
        permissions = set()
    else:
        role, username = get_user_role(session_data)
        permissions = get_user_permissions(session_data)
        is_authenticated = True

    is_super_admin = role and "super_admin" in role

    # Normalize role to a display string (role can be list or str)
    if isinstance(role, (list, tuple, set)):
        role_display = ", ".join(str(r).replace("_", " ").title() for r in role)
    elif role:
        role_display = str(role).replace("_", " ").title()
    else:
        role_display = ""

    # ---------- Header (logo + user) ----------
    header = html.Div(
        [
            html.A(
                html.Img(src="/assets/ml_repo_logo.png", className="sidebar-logo"),
                href="/",
                className="sidebar-logo-link",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.I(className="bi bi-person-circle sidebar-user-avatar"),
                            html.Div(
                                [
                                    html.Div(username, className="sidebar-user-name"),
                                    html.Div(
                                        role_display,
                                        className="sidebar-user-role",
                                    ),
                                ],
                                className="sidebar-user-info",
                            ),
                        ],
                        className="sidebar-user",
                    )
                ]
                if is_authenticated
                else [],
            ),
        ],
        className="sidebar-header",
    )

    # ---------- Sections ----------
    nav_items = []

    # Models section
    nav_items.append(html.Div("Models", className="sidebar-section-title"))
    nav_items.append(_nav_link("ML Soft Sensors", "/", icon="bi-cpu"))
    nav_items.append(_nav_link("Dynamic Models", "/dynamic-models", icon="bi-graph-up"))
    nav_items.append(_nav_link("Drift Detectors", "/drift-detectors", icon="bi-shield-check"))

    # Admin section
    if is_super_admin:
        nav_items.append(html.Div("Administration", className="sidebar-section-title"))
        nav_items.append(
            dbc.NavLink(
                html.Span(
                    [
                        html.I(className="bi bi-gear-fill sidebar-icon"),
                        html.Span("Admin", className="nav-text"),
                        html.I(className="bi bi-chevron-down sidebar-chevron"),
                    ],
                    className="nav-item-content",
                ),
                href="/admin",
                className="sidebar-link",
                id="admin-toggle",
            )
        )
        nav_items.append(
            dbc.Collapse(
                [
                    _nav_link(
                        "Organizations / Departments / Labs",
                        "/organizations",
                        icon="bi-people-fill",
                        link_id="organization-link",
                        indent=True,
                    ),
                    _nav_link(
                        "Projects & Experiments",
                        "/projects",
                        icon="bi-folder-fill",
                        link_id="project-link",
                        indent=True,
                    ),
                    _nav_link(
                        "Users",
                        "/users",
                        icon="bi-person-badge-fill",
                        link_id="users-link",
                        indent=True,
                    ),
                ],
                id="admin-collapse",
                is_open=False,
            )
        )

    # Support section
    nav_items.append(html.Div("Support", className="sidebar-section-title"))
    nav_items.append(_nav_link("Help", "/help", icon="bi-question-circle"))

    # ---------- Footer (logout) ----------
    footer = html.Div(
        [
            dbc.Button(
                html.Span(
                    [
                        html.I(className="bi bi-box-arrow-right sidebar-icon"),
                        html.Span("Logout", className="nav-text"),
                    ],
                    className="nav-item-content",
                ),
                id={"type": "logout-button", "index": 0},
                className="sidebar-link sidebar-logout",
                color="link",
                n_clicks=0,
            )
        ]
        if is_authenticated
        else [],
        className="sidebar-footer",
    )

    return html.Div(
        [
            dbc.Button("☰", id="toggle-sidebar", className="toggle-btn", n_clicks=0),
            header,
            dbc.Nav(nav_items, vertical=True, className="sidebar-nav"),
            footer,
        ],
        className="sidebar-inner",
    )
