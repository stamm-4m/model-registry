import dash_bootstrap_components as dbc
from dash import dcc, html

from model_registry.backend.pages.modal_project import project_modal
from model_registry.backend.utils.utils_projects import toast_confirm_delete_proj
from model_registry.backend.utils.utils_sidebar import get_user_role


def _tree_column(title, btn_label, btn_id, btn_color, table_div_id, toast):
    """FermOps-style column with header, scrollable body and an add bar."""
    return html.Div(
        [
            html.Div(
                [
                    html.Span(title, className="tree-col-title"),
                ],
                className="tree-col-head",
            ),
            html.Div(
                [
                    toast,
                    html.Div(id=table_div_id),
                ],
                className="tree-col-body",
            ),
            html.Div(
                dbc.Button(
                    btn_label,
                    id=btn_id,
                    color=btn_color,
                    size="sm",
                ),
                className="tree-col-add",
            ),
        ],
        className="tree-col",
    )


def projects_layout(session_data=None):
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
                            "Projects",
                        ]
                    ),
                    html.Div(
                        "Manage projects ",
                        className="page-sub",
                    ),
                ]
            ),
            html.Div(
                [
                    dcc.Link(
                        "\u2190 Back to Admin",
                        href="/admin",
                        className="btn btn-outline-secondary btn-sm",
                    ),
                ],
                className="page-actions",
            ),
        ],
        className="page-title-row",
    )

    projects_col = _tree_column(
        title="Projects",
        btn_label="+ New Project",
        btn_id="btn-open-proj-modal",
        btn_color="primary",
        table_div_id="projects-table",
        toast=toast_confirm_delete_proj(),
    )

    return dbc.Container(
        [
            # Page-local stores
            dcc.Store(id="proj-edit-id"),
            dcc.Store(id="proj-delete-id"),
            dcc.Store(id="exp-edit-id"),
            dcc.Store(id="exp-delete-id"),
            header,
            dbc.Row(
                [
                    dbc.Col(projects_col, xs=12, md=12)
                    
                ],
                className="g-3",
            ),
            # Modals (unchanged, in their own files)
            project_modal(),
        ],
        fluid=True,
        style={"padding": "20px 28px"},
    )
