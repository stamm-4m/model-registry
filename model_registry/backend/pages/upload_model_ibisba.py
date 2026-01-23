from dash import html
import dash_bootstrap_components as dbc

from model_registry.backend.utils.utils_upload_model_ibisba import get_available_projects


def add_upload_model_ibisba_layout():
    options_projects = get_available_projects()
    return dbc.Container(
        [
            html.H2("Upload model to IBISBA (FAIRDOM-SEEK)"),
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
                                dbc.Input(
                                    id="model-project-id-ibisba",
                                    type="number",
                                    placeholder="model.py",
                                ),
                                dbc.Label("Projetc id IBISBA"),
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
                                dbc.Input(
                                    id="model-creators",
                                    type="text",
                                ),
                                dbc.Label(
                                    "Creators (FAIRDOM person IDs, comma separated)"
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
        ],
        fluid=True,
    )
