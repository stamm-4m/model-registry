"""
Admin → Organizations / Departments / Laboratories.

Three-column tree layout (Organizations → Departments → Laboratories),
styled after FermOps Admin. Users are managed in the dedicated
``/users`` page; this page deals only with the org tree.

IMPORTANT: All component IDs are preserved verbatim from the previous
implementation so that the callbacks in:

  * callbacks_organization.py      (renders org/dept/lab tables)
  * callbacks_add_organization.py  (organization modal)
  * callbacks_modal_departament.py (department modal)
  * callbacks_modal_laboratory.py  (laboratory modal)
  * callbacks_delete_organization.py / _department.py / _user.py

keep working without any modification:

    org-edit-id, org-delete-id, org-refresh-trigger
    dept-edit-id, dept-delete-id, dept-refresh-trigger
    lab-edit-id, lab-delete-id, lab-refresh-trigger
    btn-open-org-modal,  organizations-table
    btn-open-dept-modal, departments-table
    btn-open-lab-modal,  laboratories-table
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from model_registry.backend.pages.add_organization import organization_modal
from model_registry.backend.pages.department_modal import department_modal
from model_registry.backend.pages.laboratory_modal import laboratory_modal
from model_registry.backend.utils.utils_department import toast_confirm_delete_dept
from model_registry.backend.utils.utils_laboratory import toast_confirm_delete_lab
from model_registry.backend.utils.utils_organization import toast_confirm_delete
from model_registry.backend.utils.utils_sidebar import get_user_role

# --------------------------------------------------------------------- column


def _tree_column(title, btn_label, btn_id, table_div_id, toast):
    """
    A single column in the org-tree: header + list/table + add-button.

    The table content itself is rendered by the existing
    ``callbacks_organization.py`` callbacks into ``table_div_id``.
    """
    return html.Div(
        [
            html.Div(
                [
                    html.Span(title, className="tree-col-title"),
                    html.Span("", className="tree-col-count"),
                ],
                className="tree-col-head",
            ),
            html.Div(
                [
                    toast,
                    html.Div(id=table_div_id, className="tree-col-body"),
                ],
            ),
            html.Div(
                dbc.Button(
                    btn_label,
                    id=btn_id,
                    color="primary",
                    size="sm",
                    className="w-100",
                ),
                className="tree-col-add",
            ),
        ],
        className="tree-col",
    )


# --------------------------------------------------------------------- layout


def organizations_layout(session_data=None):
    role, _ = get_user_role(session_data)
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
                            "Organizations / Departments / Laboratories",
                        ]
                    ),
                    html.Div(
                        "Tree: Organization → Department → Laboratory. "
                        "Each column lets you create new entries and edit "
                        "existing ones.",
                        className="page-sub",
                    ),
                ]
            ),
            html.Div(
                dcc.Link(
                    "← Back to Admin",
                    href="/admin",
                    className="btn btn-outline-secondary btn-sm",
                ),
                className="page-actions",
            ),
        ],
        className="page-title-row",
    )

    columns = dbc.Row(
        [
            dbc.Col(
                _tree_column(
                    title="Organizations",
                    btn_label="+ New Organization",
                    btn_id="btn-open-org-modal",
                    table_div_id="organizations-table",
                    toast=toast_confirm_delete(),
                ),
                xs=12,
                md=4,
            ),
            dbc.Col(
                _tree_column(
                    title="Departments",
                    btn_label="+ New Department",
                    btn_id="btn-open-dept-modal",
                    table_div_id="departments-table",
                    toast=toast_confirm_delete_dept(),
                ),
                xs=12,
                md=4,
            ),
            dbc.Col(
                _tree_column(
                    title="Laboratories",
                    btn_label="+ New Laboratory",
                    btn_id="btn-open-lab-modal",
                    table_div_id="laboratories-table",
                    toast=toast_confirm_delete_lab(),
                ),
                xs=12,
                md=4,
            ),
        ],
        className="g-3",
    )

    return dbc.Container(
        [
            # Page-local stores
            dcc.Store(id="org-edit-id"),
            dcc.Store(id="org-delete-id"),
            dcc.Store(id="dept-edit-id"),
            dcc.Store(id="dept-delete-id"),
            dcc.Store(id="lab-edit-id"),
            dcc.Store(id="lab-delete-id"),
            header,
            columns,
            # Modals (unchanged, in their own files for modularity).
            organization_modal(),
            department_modal(),
            laboratory_modal(),
        ],
        fluid=True,
        style={"padding": "20px 28px"},
    )
