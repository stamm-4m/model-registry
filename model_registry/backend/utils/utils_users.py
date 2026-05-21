from dash import html
import dash_bootstrap_components as dbc

_DASH = "\u2014"


def _fmt_date(value):
    if not value:
        return ""
    try:
        return value.strftime("%Y-%m-%d")
    except AttributeError:
        return str(value)[:10]


def _role_class(role_name: str) -> str:
    """Map raw role name to a CSS pill class (defined in style.css)."""
    if not role_name:
        return "role-user"
    slug = role_name.lower().replace(" ", "_").replace("-", "_")
    # Known buckets from style.css: super_admin, admin, operator, engineer,
    # ml, qa, user. Anything else falls back to the generic ``role-user``
    # pill so it still looks consistent.
    if slug in {
        "super_admin", "admin", "operator", "engineer",
        "ml", "qa", "user",
    }:
        return f"role-{slug}"
    if "admin" in slug:
        return "role-admin"
    return "role-user"


def _role_pills(role_names):
    if not role_names:
        return html.Span(_DASH, style={"color": "var(--ink-faint)"})
    return html.Div(
        [
            html.Span(
                rn.upper(),
                className=f"role-pill {_role_class(rn)}",
            )
            for rn in role_names
        ],
        style={"display": "flex", "gap": "4px", "flexWrap": "wrap"},
    )


def build_table_users(users):
    """FermOps-style admin table for users.

    Accepts either the legacy tuples ``(user, lab_name, dept_name)`` or
    the enriched tuples ``(user, lab_name, dept_name, [role_names])`` from
    ``UserService.get_all_users_full`` so the same renderer works during
    the migration period.

    Edit / Roles / Delete buttons keep their pattern-matching IDs so the
    existing callbacks continue to fire untouched.
    """
    header = html.Thead(
        html.Tr(
            [
                html.Th("Name"),
                html.Th("Email"),
                html.Th("Role"),
                html.Th("Laboratory"),
                html.Th("Department"),
                html.Th("Active"),
                html.Th("Created"),
                html.Th(""),
            ]
        )
    )

    body_rows = []
    for row in users:
        if len(row) == 4:
            user, lab_name, dept_name, role_names = row
        else:
            user, lab_name, dept_name = row
            role_names = []

        body_rows.append(
            html.Tr(
                [
                    html.Td(user.full_name or _DASH),
                    html.Td(
                        user.email or _DASH,
                        style={
                            "fontSize": "11.5px",
                            "color": "var(--ink-muted)",
                        },
                    ),
                    html.Td(_role_pills(role_names)),
                    html.Td(lab_name or _DASH),
                    html.Td(dept_name or _DASH),
                    html.Td(
                        "\u2713" if user.is_active else _DASH,
                        style={
                            "color": (
                                "var(--green)" if user.is_active
                                else "var(--ink-faint)"
                            ),
                            "fontWeight": 700,
                            "textAlign": "center",
                        },
                    ),
                    html.Td(_fmt_date(user.created_at)),
                    html.Td(
                        html.Div(
                            [
                                html.Button(
                                    "Edit",
                                    id={
                                        "type": "btn-edit-user",
                                        "index": str(user.id),
                                    },
                                    className="tree-btn",
                                    n_clicks=0,
                                ),
                                html.Button(
                                    "Roles",
                                    id={
                                        "type": "btn-manage-roles",
                                        "index": str(user.id),
                                    },
                                    className="tree-btn",
                                    n_clicks=0,
                                ),
                                html.Button(
                                    "Delete",
                                    id={
                                        "type": "btn-delete-user",
                                        "index": str(user.id),
                                    },
                                    className="tree-btn danger",
                                    n_clicks=0,
                                ),
                            ],
                            className="tree-actions",
                        )
                    ),
                ],
                className="admin-row",
            )
        )

    if not body_rows:
        body_rows = [
            html.Tr(
                html.Td(
                    "No users match the current filters.",
                    colSpan=8,
                    style={
                        "textAlign": "center",
                        "color": "var(--ink-faint)",
                        "padding": "20px",
                        "fontStyle": "italic",
                    },
                )
            )
        ]

    return html.Table(
        [header, html.Tbody(body_rows)],
        className="admin-table",
    )


def toast_confirm_delete_user():
    return html.Div([
        dbc.Toast(
            id="user-toast",
            header="Notification",
            is_open=False,
            dismissable=True,
            duration=4000,
            icon="primary",
            style={
                "position": "fixed",
                "top": 10,
                "right": 10,
                "width": 350,
                "zIndex": 9999
            }
        ),
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Confirm Delete")),
            dbc.ModalBody("Are you sure you want to delete this user?"),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="btn-cancel-delete-user", color="secondary"),
                dbc.Button("Delete", id="btn-confirm-delete-user", color="danger")
            ])
        ], id="delete-user-modal", is_open=False),
    ])
