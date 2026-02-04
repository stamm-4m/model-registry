import dash_bootstrap_components as dbc
from dash import html, dcc

from model_registry.backend.utils.utils_upload_model_ibisba import (
    get_available_projects,get_available_creators, get_available_projects_ibisba
)


def add_upload_model_ibisba_layout():
    options_projects = get_available_projects()
    options_creators = get_available_creators()
    options_projects_ibisba = get_available_projects_ibisba()
    return dbc.Container(
        [
            html.H2(
                style={"color":"#3f8814"},
                children=[
                    html.Img(
                        src="/assets/icon-ibisba.jpeg",
                        style={
                            "height": "56px",
                            "marginRight": "10px",
                            "verticalAlign": "middle",
                        },
                    ),
                    "Push models to IBISBA hub" 
                ]
            ),
            html.Hr(),

            # =========================
            # 1️⃣ Project selection
            # =========================
            dbc.FormFloating(
                [
                    dbc.Select(
                        id="projects-dropdown",
                        options=options_projects,
                        placeholder="Select a project",
                    ),
                    dbc.Label("Project"),
                ],
                className="mb-4",
            ),
            # =========================
            # 2️⃣ Models selection
            # =========================
            dbc.Collapse(
                dbc.FormFloating(
                    [
                        dbc.Select(
                            id="available-models-dropdown",
                            options=[],
                            placeholder="Select a model",
                        ),
                        dbc.Label("Available models"),
                    ],
                    className="mb-4",
                ),
                id="models-dropdown-collapse",
                is_open=False,
            ),

            # =========================
            # 3️⃣ Upload form
            # =========================
            dbc.Collapse(
                dbc.Form(
                    [
                        dbc.FormFloating(
                            [
                                dbc.Input(
                                    id="metadata-yaml-path",
                                    type="text",
                                    placeholder="metadata.yaml",
                                ),
                                dbc.Label("Model metadata YAML file path"),
                            ],
                            className="mb-3",
                        ),
                        
                        dbc.FormFloating(
                            [
                                dbc.Input(
                                    id="model-file-name",
                                    type="text",
                                    placeholder="model name",
                                ),
                                dbc.Label("Name model's file"),
                            ],
                            className="mb-3",
                        ),

                        dbc.FormFloating(
                            [
                                dbc.Input(
                                    id="model-file-path",
                                    type="text",
                                    placeholder="model.py",
                                ),
                                dbc.Label("Model file path"),
                            ],
                            className="mb-3",
                        ),

                        dbc.FormFloating(
                            [
                                dbc.Select(
                                    id="model-project-id-ibisba",
                                    options=options_projects_ibisba,
                                    placeholder="Select a project in IBISBA hub",
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
                                ),
                                dbc.Label("Model title in FAIRDOM"),
                            ],
                            className="mb-3",
                        ),

                        dbc.FormFloating(
                            [
                                 dcc.Dropdown(
                                    id="model-creators",
                                    options=options_creators,
                                    placeholder="Model creators in IBISBA hub",
                                    value=[],
                                    multi=True,
                                    className="form-control"
                                ),
                                
                                
                            ],
                            className="mb-3",
                        ),

                        dbc.Button(
                            "Upload model to IBISBA",
                            id="upload-model-btn",
                            color="primary",
                            className="mt-3",
                        ),

                        html.Br(),
                        html.Div(id="upload-status"),
                    ]
                ),
                id="upload-form-collapse",
                is_open=False,
            ),
            # =========================
            # Modal comfirmation information
            # =========================
            dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Confirm information for upload to the IBISBA Hub")),
                dbc.ModalBody(id="confirm-upload-body"),
                dbc.ModalFooter(
                    [
                        dbc.Button("Cancel", id="cancel-upload-btn", color="secondary"),
                        dbc.Button("Confirm upload", id="confirm-upload-btn", color="primary"),
                    ]
                ),
            ],
            id="confirm-upload-modal",
            is_open=False,
        )
        ],
        fluid=True,
    )
