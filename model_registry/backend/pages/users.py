"""
Admin → Users.

Dedicated page for user management, styled after FermOps Admin Users.
Functionally identical to the previous "Users" tab on ``/organizations``:
the same user table is rendered by ``callbacks_organization.py`` (output
``users-table``), the same ``user_modal()`` and ``roles_modal()`` are
used for create/edit/assign-roles, and the same toast / stores drive
delete and refresh.

IMPORTANT: All previously used component IDs are preserved so the
following callbacks keep working without modification:

  * callbacks_modal_user.py        (open / close / save user modal)
  * callbacks_modal_user_roles.py  (roles modal)
  * callbacks_delete_user.py       (delete-user toast)
  * callbacks_organization.py      (renders ``users-table`` div)

Preserved IDs::

    user-edit-id, user-delete-id, user-refresh-trigger
    btn-open-user-modal, users-table
    user-modal, user-name-input, user-email-input, user-password-input,
    user-dept-dropdown, user-lab-dropdown, lab-label,
    btn-close-user-modal, btn-save-user
    roles-modal and all role-modal IDs (rendered by ``roles_modal()``)
"""

from dash import dcc, html
import dash_bootstrap_components as dbc

from model_registry.backend.pages.user_modal import user_modal
from model_registry.backend.pages.user_modal_roles import roles_modal
from model_registry.backend.services.user_service import UserService
from model_registry.backend.utils.utils_users import toast_confirm_delete_user
from model_registry.backend.utils.utils_sidebar import get_user_role


def _role_filter_options(session_data):
    """Fetch the role catalogue via the API (with permissions)."""
    try:
        roles, _ = UserService().get_all_roles(session_data or {})
    except Exception:
        roles = []
    options = [{"label": "All roles", "value": "__all__"}]
    for r in roles or []:
        name = r.get("name") if isinstance(r, dict) else None
        if not name:
            continue
        options.append({"label": name.upper(), "value": name})
    return options


def users_layout(session_data=None):
    role, _ = get_user_role(session_data or {})
    if not role or "super_admin" not in role:
        return dbc.Container(
            [
                html.H3("Access Denied", className="text-danger mt-4"),
                html.P("You do not have permission to view this page."),
            ]
        )

    header = html.Div(
        [
            html.Div(
                [
                    html.H2(
                        [
                            dcc.Link(
                                "Admin",
                                href="/admin",
                                style={"color": "var(--ink-faint)"},
                            ),
                            html.Span(
                                " / ",
                                style={"color": "var(--ink-faint)"},
                            ),
                            "Users",
                        ]
                    ),
                    html.Div(
                        "Invite, edit and manage user accounts, roles "
                        "and lab / project memberships.",
                        className="page-sub",
                    ),
                ]
            ),
            html.Div(
                [
                    dcc.Link(
                        "\u2190 Back to Admin",
                        href="/admin",
                        className="btn btn-outline-secondary btn-sm me-2",
                    ),
                    dbc.Button(
                        "+ Add user",
                        id="btn-open-user-modal",
                        color="primary",
                        size="sm",
                    ),
                ],
                className="page-actions",
            ),
        ],
        className="page-title-row",
    )

    filter_bar = html.Div(
        [
            html.Span(
                "Filter by role:",
                className="admin-filter-label",
                style={"marginRight": "8px"},
            ),
            dbc.Select(
                id="user-role-filter",
                options=_role_filter_options(session_data),
                value="__all__",
                size="sm",
                style={
                    "width": "200px",
                    "display": "inline-block",
                    "marginRight": "12px",
                },
            ),
            dbc.Input(
                id="user-search-input",
                value="",
                size="sm",
                placeholder="Search by name or email\u2026",
                debounce=True,
                style={"width": "260px", "display": "inline-block"},
            ),
        ],
        className="admin-filter-bar",
        style={"marginBottom": "12px"},
    )

    users_panel = html.Div(
        [
            toast_confirm_delete_user(),
            html.Div(id="users-table"),
        ],
        className="admin-list-panel",
    )

    return dbc.Container(
        [
            # Stores (kept verbatim so callbacks continue to fire).
            dcc.Store(id="user-edit-id"),
            dcc.Store(id="user-delete-id"),
            dcc.Store(id="user-refresh-trigger"),

            header,
            filter_bar,
            users_panel,

            # Modals (unchanged, in their own files for modularity).
            user_modal(),
            roles_modal(),
        ],
        fluid=True,
        style={"padding": "20px 28px"},
    )

