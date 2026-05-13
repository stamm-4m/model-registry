import dash_bootstrap_components as dbc
from dash import dcc, html

from model_registry.backend.components.models_grid import get_models_grid
from model_registry.backend.pages.modal_project import project_modal


def home_layout(projects_options=None, permissions=None):
    models_grid = get_models_grid(permissions=permissions)

    projects_list = projects_options or []
    options_projects_dropdown = [
        {"label": p["name"], "value": p["project_ID"]}
        for p in projects_list
    ]
    default_project_id = (
        options_projects_dropdown[0]["value"] if options_projects_dropdown else None
    )

    # ---- Page header ----
    page_header = html.Div(
        [
            html.Div(
                [
                    html.H2(
                        [
                            html.I(className="bi bi-cpu me-2 text-primary"),
                            "ML Soft Sensors",
                        ],
                        className="page-title mb-1",
                    ),
                    html.P(
                        "Browse the projects you have access to and manage their registered models.",
                        className="text-muted mb-0",
                    ),
                ],
                className="page-header-text",
            ),
            html.Div(
                [
                    dbc.Badge(
                        [
                            html.I(className="bi bi-folder2-open me-1"),
                            f"{len(projects_list)} project"
                            + ("s" if len(projects_list) != 1 else ""),
                        ],
                        color="light",
                        text_color="primary",
                        className="me-2 px-3 py-2 border",
                    ),
                ],
                className="page-header-actions",
            ),
        ],
        className="page-header d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2",
    )

    # ---- Project selector card ----
    project_card = dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.I(className="bi bi-funnel-fill me-2 text-primary"),
                        html.Span("Project Selection", className="card-section-title"),
                    ],
                    className="mb-3 d-flex align-items-center",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    "Project",
                                    html_for="filter-project",
                                    className="form-label small text-muted",
                                ),
                                dcc.Dropdown(
                                    id="filter-project",
                                    options=options_projects_dropdown,
                                    placeholder="Select a project...",
                                    clearable=True,
                                    value=default_project_id,
                                    className="project-dropdown",
                                ),
                            ],
                            md=8,
                        ),
                        dbc.Col(
                            dbc.Button(
                                [
                                    html.I(className="bi bi-plus-lg me-1"),
                                    "Add Project",
                                ],
                                id="btn-open-proj-modal",
                                color="primary",
                                className="w-100",
                            ),
                            md=4,
                            className="d-flex align-items-end",
                        ),
                    ],
                    className="g-3",
                ),
            ]
        ),
        className="mb-4 shadow-sm border-0 home-card",
    )
    # MODAL
    project_modal(),
    # ---- Models card ----
    models_card = dbc.Card(
        [
            dbc.CardHeader(
                html.Div(
                    [
                        html.Div(
                            [
                                html.I(className="bi bi-collection me-2 text-primary"),
                                html.Span(
                                    "Registered Models",
                                    className="card-section-title",
                                ),
                                html.Small(
                                    "Manage the models for the selected project.",
                                    className="text-muted ms-3 d-none d-md-inline",
                                ),
                            ],
                            className="d-flex align-items-center",
                        ),
                        dbc.Button(
                            [
                                html.I(className="bi bi-plus-lg me-1"),
                                "Add Model",
                            ],
                            id="add-model",
                            color="primary",
                            size="sm",
                        ),
                    ],
                    className="d-flex justify-content-between align-items-center flex-wrap gap-2",
                ),
                className="bg-white border-0 pt-3 pb-2",
            ),
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.Small(
                                [
                                    html.I(className="bi bi-info-circle me-1"),
                                    "Available actions: ",
                                    html.Strong("Register to IBISBA"),
                                    ", ",
                                    html.Strong("Explainability (XAI)"),
                                    ", ",
                                    html.Strong("Details"),
                                    ", ",
                                    html.Strong("Edit"),
                                    ", ",
                                    html.Strong("Delete"),
                                    ".",
                                ],
                                className="text-muted",
                            )
                        ],
                        className="mb-3",
                    ),
                    models_grid,
                ]
            ),
        ],
        className="shadow-sm border-0 home-card",
    )

    # ---- Modals & dialogs ----
    confirm_delete = dcc.ConfirmDialog(
        id="confirm-delete-model",
        message="Are you sure you want to delete this model? This action cannot be undone.",
    )

    project_required_modal = dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Project Required")),
            dbc.ModalBody(
                "Please select a project name before adding a new model."
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "OK",
                    id="close-project-modal",
                    className="ms-auto",
                    n_clicks=0,
                )
            ),
        ],
        id="project-required-modal",
        is_open=False,
    )

    return dbc.Container(
        fluid=True,
        className="home-page p-4",
        children=[
            page_header,
            project_card,
            # Modal para agregar proyecto
            project_modal(),
            models_card,
            confirm_delete,
            dcc.Store(id="model-to-delete"),
            project_required_modal,
        ],
    )
