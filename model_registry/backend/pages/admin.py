"""
Admin Panel landing page — card grid, styled like FermOps.

This page only renders navigation cards toward existing admin sections;
no business logic is performed here, and no existing functionality is
modified. Access control mirrors the other admin pages: only users with
the ``super_admin`` role can see it.
"""

from dash import dcc, html

from model_registry.backend.utils.utils_sidebar import get_user_role


def _admin_card(title, blurb, href, tag_label="READY", ready=True):
    """Render a single clickable admin card (mirrors FermOps layout)."""
    tag_class = "ready" if ready else "soon"
    card_class = "admin-card" if ready else "admin-card disabled"

    return dcc.Link(
        html.Div(
            [
                html.Div(
                    [
                        html.Span(title, className="admin-card-title"),
                        html.Span(
                            tag_label,
                            className=f"admin-card-tag {tag_class}",
                        ),
                    ],
                    style={"display": "flex", "alignItems": "center"},
                ),
                html.Div(blurb, className="admin-card-blurb"),
                html.Div("Click to manage", className="admin-card-count"),
            ],
            className=card_class,
        ),
        href=href if ready else "#",
        style={"textDecoration": "none", "color": "inherit"},
    )


def admin_layout(session_data=None):
    """Card-grid landing page for the Administration section."""
    role, username = get_user_role(session_data or {})
    is_super_admin = role and "super_admin" in role

    if not is_super_admin:
        return html.Div(
            [
                html.Div(
                    [
                        html.H2("Admin Panel"),
                        html.Div(
                            "You don't have admin permissions.",
                            style={
                                "color": "var(--red)",
                                "marginTop": "24px",
                            },
                        ),
                        dcc.Link(
                            "← Back to Home",
                            href="/",
                            className="btn btn-secondary btn-sm",
                            style={"marginTop": "12px"},
                        ),
                    ],
                    style={"padding": "40px"},
                ),
            ]
        )

    header = html.Div(
        [
            html.Div(
                [
                    html.H2(
                        [
                            "Admin Panel ",
                            html.Span(
                                "super-admin",
                                className="admin-role-pill",
                            ),
                        ]
                    ),
                    html.Div(
                        f"Logged in as {username}" if username else "",
                        className="page-sub",
                    ),
                ]
            ),
        ],
        className="page-title-row",
    )

    cards = html.Div(
        [
            _admin_card(
                "Organization & People",
                "Manage organizations, departments and laboratories. "
                "Add organisational structure and assign people.",
                "/organizations",
            ),
            _admin_card(
                "Projects",
                "Create new projects, edit objectives and leads, "
                "archive completed work.",
                "/projects",
            ),
            _admin_card(
                "Users",
                "Invite users, assign roles and lab / project "
                "memberships, deactivate accounts.",
                "/users",
            ),
        ],
        className="admin-card-grid",
    )

    return html.Div(
        [header, cards],
        style={"padding": "20px 28px"},
    )
