import dash_bootstrap_components as dbc
from dash import html, dcc

from model_registry.backend.utils.utils_upload_model_ibisba import (
    get_available_projects,
    get_available_creators,
    get_available_projects_ibisba,
    get_information_model,
)


def add_upload_model_ibisba_layout(project_id, model_id):
    model_information = get_information_model(project_id, model_id)

    return dbc.Container(
        [
            dbc.Row(
                [
                    dcc.Store(id="metadata-yaml-path"),
                    dcc.Store(id="model-file-name"),
                    dcc.Store(id="model-file-path"),

                    # =========================
                    # LEFT COLUMN – Information
                    # =========================
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H5(
                                        [
                                            html.Img(
                                                src="/assets/logo.png",
                                                style={
                                                    "height": "36px",
                                                    "marginRight": "10px",
                                                    "verticalAlign": "middle",
                                                },
                                            ),
                                            "Model Registry information",
                                        ],
                                        className="mb-0",
                                    )
                                ),
                                dbc.CardBody(
                                    [
                                        html.H4("Model Identification", className="mb-4"),
                                        dbc.FormFloating(
                                            [
                                                dbc.Input(
                                                    id="projects-dropdown",
                                                    type="text",
                                                    value=project_id,
                                                    readonly=True,
                                                    plaintext=True,
                                                ),
                                                dbc.Label("Project ID"),
                                            ],
                                            className="mb-4",
                                        ),

                                        dbc.FormFloating(
                                            [
                                                dbc.Input(
                                                    id="available-models-dropdown",
                                                    value=model_information.get("ID", ""),
                                                    readonly=True,
                                                    plaintext=True,
                                                ),
                                                dbc.Label("Model ID"),
                                            ],
                                            className="mb-3",
                                        ),
                                        

                                        dbc.FormFloating(
                                            [
                                                dbc.Input(
                                                    id="edit_model_uuid",
                                                    type="text",
                                                    plaintext=True,
                                                    value=model_information.get("UUID", ""),
                                                    readonly=True,
                                                ),
                                                dbc.Label("Model UUID"),
                                            ],
                                            className="mb-3",
                                        ),

                                        dbc.FormFloating(
                                            [
                                                dbc.Input(
                                                    id="edit_model_doi",
                                                    type="text",
                                                    plaintext=True,
                                                    value=model_information.get("doi", ""),
                                                    readonly=True,
                                                ),
                                                dbc.Label("Model DOI"),
                                            ],
                                            className="mb-3",
                                        ),

                                        dbc.FormFloating(
                                            [
                                                dbc.Input(
                                                    id="edit_name",
                                                    type="text",
                                                    plaintext=True,
                                                    value=model_information.get("name", ""),
                                                    readonly=True,
                                                ),
                                                dbc.Label("Model Name"),
                                            ],
                                            className="mb-3",
                                        ),

                                        dbc.FormFloating(
                                            [
                                                dbc.Input(
                                                    id="edit_model_version",
                                                    type="text",
                                                    plaintext=True,
                                                    value=model_information.get("version", ""),
                                                    readonly=True,
                                                ),
                                                dbc.Label("Model Version"),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Button(
                                            "Confirm selection",
                                            id="confirm-selection-btn",
                                            color="success",
                                            className="mt-3",
                                        ),
                                        dbc.Alert(
                                            "Project and model confirmed",
                                            id="selection-confirmed-alert",
                                            color="success",
                                            is_open=False,
                                            className="mt-3"
                                        ),
                                    ]
                                ),
                            ],
                            className="h-100",
                        ),
                        md=6,
                    ),

                    # =========================
                    # RIGHT COLUMN – Push models
                    # =========================
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H5(
                                        [
                                            html.Img(
                                                src="/assets/icon-ibisba.jpeg",
                                                style={
                                                    "height": "36px",
                                                    "marginRight": "10px",
                                                    "verticalAlign": "middle",
                                                },
                                            ),
                                            "IBISBA hub information",
                                        ],
                                        style={"color": "#3f8814"},
                                        className="mb-0",
                                    )
                                ),
                                dbc.CardBody(
                                    [
                                        dbc.Collapse(
                                            dbc.Form(
                                                [
                                                    dbc.FormFloating(
                                                        [
                                                            dbc.Select(
                                                                id="model-project-id-ibisba",
                                                                options=[],
                                                                placeholder="Select a project in IBISBA hub",
                                                                required=True,
                                                            ),
                                                            dbc.Label("Project id IBISBA"),
                                                        ],
                                                        className="mb-3",
                                                    ),

                                                    dbc.FormFloating(
                                                        [
                                                            dbc.Input(
                                                                id="model-title",
                                                                type="text",
                                                                placeholder="Model title",
                                                                required=True,
                                                            ),
                                                            dbc.Label("Model title in FAIRDOM"),
                                                        ],
                                                        className="mb-3",
                                                    ),

                                                    dbc.FormFloating(
                                                        [
                                                            dcc.Dropdown(
                                                                id="model-creators",
                                                                options=[],
                                                                placeholder="Model creators in IBISBA hub",
                                                                multi=True,
                                                                className="form-control",
                                                            ),
                                                        ],
                                                        className="mb-3",
                                                    ),

                                                    dbc.FormFloating(
                                                        [
                                                            dcc.Dropdown(
                                                                id="model-organisms",
                                                                options=[],
                                                                placeholder="Model organisms in IBISBA hub",
                                                                value=[],
                                                                multi=True,
                                                                className="form-control",
                                                            ),
                                                        ],
                                                        className="mb-3",
                                                    ),

                                                    dbc.Button(
                                                        "Confirm selection",
                                                        id="confirm-selection-ibisba-btn",
                                                        color="success",
                                                        className="mt-3",
                                                    ),
                                                    dbc.Alert(
                                                        "Project and model confirmed",
                                                        id="selection-confirmed-ibisba-alert",
                                                        color="success",
                                                        is_open=False,
                                                        className="mt-3"
                                                    ),
                                                ]
                                            ),
                                            id="upload-form-collapse",
                                            is_open=False,
                                        )
                                    ]
                                ),
                            ],
                            className="h-100",
                        ),
                        md=6,
                    ),
                ],
                className="g-4",
            ),
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.Collapse(
                                dbc.Form(
                                    [
                                        html.Div(
                                            dbc.Button(
                                                "Push model to IBISBA",
                                                id="upload-model-btn",
                                                color="primary",
                                                className="mt-3",
                                            ),
                                            className="text-center"
                                        ),
                                        html.Div(className="mt-4"),
                                        html.Div(
                                            id="upload-status",
                                            className="text-start"
                                        ),
                                    ]
                                ),
                                id="boton-form-collapse",
                                is_open=False,
                            )
                        ),
                        md=12,
                    )
                ]
            ),

            # =========================
            # Modal confirmation
            # =========================
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(
                            "Confirm information for upload to the IBISBA Hub"
                        )
                    ),
                    dbc.ModalBody(id="confirm-upload-body"),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "Cancel",
                                id="cancel-upload-btn",
                                color="secondary",
                            ),
                            dbc.Button(
                                "Confirm upload",
                                id="confirm-upload-btn",
                                color="primary",
                            ),
                        ]
                    ),
                ],
                id="confirm-upload-modal",
                is_open=False,
            ),
        ],
        fluid=True,
    )
