import dash_bootstrap_components as dbc
from dash import dcc, html


def model_upload_layout(project_id):
        """Property that generates the layout for the upload component and additional form."""
        return html.Div([
            dcc.Store(id="add-model-info", data={
                "project_id": project_id
            }),
            dcc.Store(id="add-features-store", data=[]),
            dcc.Store(
                id="add-outputs-store",
                data=[]
            ),
            html.H3("Add Model", className="text-center my-4"),
            # Section: Upload File
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H3("Upload file model"),
                        dcc.Upload(
                            id="upload-data",
                            children=html.Button('Upload'),
                            multiple=False
                        )
                    ]
                ),
                className="my-3 shadow-sm",
            ),
            html.Div(id="output-data-upload"),
            dbc.Card(
                dbc.CardBody(
                    dbc.Container([
                        dbc.Row([
                            dbc.Col([
                                html.H4("Model Identification", className="mb-4"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="add_model_id",
                                            placeholder="Model file name",
                                            plaintext=True,
                                            readonly=True,
                                            className="fw-bold text-muted"
                                        ),
                                        dbc.Label("Model ID"),
                                    ],className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="add_model_uuid",
                                            type="text",
                                            placeholder="Model UUID",
                                    ),
                                        dbc.Label("Model UUID"),
                                    ],className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="add_model_doi",
                                            type="text",
                                            placeholder="Model DOI",
                                        ),
                                        dbc.Label("Model DOI"),
                                    ],className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="add_name",
                                            type="text",
                                            placeholder="Model Name",
                                        ),
                                        dbc.Label("Model Name"),
                                    ],className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="add_model_version",
                                            type="text",
                                            placeholder="Model Version",
                                        ),
                                        dbc.Label("Model Version"),
                                    ],className="mb-3"),

                            ],md=6,),

                            dbc.Col([
                                html.H4("Creation", className="mb-4"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="add_creation_date",
                                        type="date",
                                        placeholder="Creation Date",
                                    ),
                                    dbc.Label("Creation Date"),
                                ],className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Textarea(
                                        id="add_author",
                                        placeholder="Author",
                                        style={"height": "100px"},
                                    ),
                                    dbc.Label("Author"),
                                ], className="mb-3"),
                                html.Div([
                                        dbc.Label("Status", className="fw-semibold"),
                                        dbc.RadioItems(
                                            id="add_status",
                                            options=[
                                                {"label": "Online", "value": "online"},
                                                {"label": "Offline", "value": "offline"},
                                            ],
                                            inline=True,
                                        ),
                                    ],className="mb-3"),

                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="add_status_description",
                                            type="text",
                                            placeholder="Status Description",
                                        ),
                                        dbc.Label("Status Description"),
                                    ],className="mb-3"), 
                            ],md=6,),
                        ],className="mb-4",),
                    
                        dbc.Row([
                            html.H4("Model Description", className="mb-4"),
                            dbc.Col([
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="add_learner",
                                        type="text",
                                        placeholder="Learner",
                                    ),
                                    dbc.Label("Learner"),
                                ],className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="add_model_type",
                                        type="text",
                                        placeholder="Model Type",
                                    ),
                                    dbc.Label("Model Type"),
                                ],className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="add_model_name",
                                        type="text",
                                        placeholder="Model Name",
                                    ),
                                    dbc.Label("Model Name"),
                                ],className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Textarea(
                                        id="add_description",
                                        placeholder="Model Description",
                                        style={"height": "150px"},
                                    ),
                                    dbc.Label("Model Description"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="add_language",
                                        type="text",
                                        placeholder="Language",
                                    ),
                                    dbc.Label("Language"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="add_language_version",
                                        type="text",
                                        placeholder="Language Version",
                                    ),
                                    dbc.Label("Language Version"),
                                ], className="mb-3"),
                                
                                html.Div(
                                [
                                    html.H5("Packages", className="mt-4"),
                                    html.Div(
                                        id="add-packages-container",
                                        children=[],
                                    ),
                                    dbc.Button(
                                        "➕ Add package",
                                        id="add-add-package",
                                        color="secondary",
                                        outline=True,
                                        className="mt-2",
                                    ),
                                ]), 

                            ],md=6,),

                            dbc.Col([
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="add_config_model_file",
                                        type="text",
                                        placeholder="Configuration Model File",
                                    ),
                                    dbc.Label("Model File"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="add_config_server",
                                        type="text",
                                        placeholder="Configuration Server",
                                    ),
                                    dbc.Label("Configuration Server"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="add_config_port",
                                        type="text",
                                        placeholder="Configuration Port",
                                    ),
                                    dbc.Label("Configuration Port"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="add_config_rest_api",
                                        type="text",
                                        placeholder="Configuration REST API",
                                    ),
                                    dbc.Label("Configuration REST API"),
                                ], className="mb-3"),
                                html.Div([
                                    html.H5("Input time interval", className="mt-4"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="add_time_interval",
                                            type="number",
                                            placeholder="Input time interval",
                                        ),
                                        dbc.Label("Input time interval"),
                                    ], className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="add_time_interval_units",
                                            type="text",
                                            placeholder="Input time interval units",
                                        ),
                                        dbc.Label("Input time interval units"),
                                    ], className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="add_time_interval_description",
                                            type="text",
                                            placeholder="Input time interval description",
                                        ),
                                        dbc.Label("Input time interval description"),
                                    ], className="mb-3"),
                                    html.H5("Aggregation", className="mt-4"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="add_time_interval_aggregation",
                                            type="text",
                                            placeholder="Input time interval aggregation",
                                        ),
                                        dbc.Label("Input time interval aggregation"),
                                    ], className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="add_time_interval_aggregation_description",
                                            type="text",
                                            placeholder="Input time interval aggregation description",
                                        ),
                                        dbc.Label("Input time interval aggregation description"),
                                    ], className="mb-3"),

                                ])

                            ],md=6,),
                        ],className="mb-4",),    

                        dbc.Row([
                            html.H4("Training information", className="mb-4"),
                            dbc.Col([
                                html.Div([
                                    html.H5("Hyperparameters", className="mt-4"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="add_number_of_trees",
                                            type="number",
                                            placeholder="Input number of trees",
                                        ),
                                        dbc.Label("Number of trees"),
                                    ], className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="add_max_tree_depth",
                                            type="number",
                                            placeholder="Maximum depth",
                                        ),
                                        dbc.Label("Maximum depth"),
                                    ], className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="add_min_number_instances_per_leaf",
                                            type="number",
                                            placeholder="Input min number instances per leaf",
                                        ),
                                        dbc.Label("Input min number instances per leaf"),
                                    ], className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="add_committees",
                                            type="number",
                                            placeholder="Input committees",
                                        ),
                                        dbc.Label("Input committees"),
                                    ], className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="add_instance_based_correction",
                                            type="number",
                                            placeholder="Input instance based correction",
                                        ),
                                        dbc.Label("Input instance based correction"),
                                    ], className="mb-3"),
                                ])
                            ],md=6,),

                            dbc.Col([
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="add_number_of_instances",
                                        type="text",
                                        placeholder="Number of Instances",
                                    ),
                                    dbc.Label("Number of Instances"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="add_validation",
                                        type="text",
                                        placeholder="Validation",
                                    ),
                                    dbc.Label("Validation"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Textarea(
                                        id="add_experiments_id",
                                        placeholder="Experiments ID",
                                        style={"height": "120px"},
                                    ),
                                    dbc.Label("Training experiments ID"),
                                ], className="mb-3"),
                            ],md=6,),
                                    
                        ],className="mb-4",),

                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H4("Inputs", className="mb-4"),
                                    dbc.Accordion(
                                        id="add-features-accordion",
                                        always_open=True
                                    ),
                                    dbc.Button(
                                        "➕ Add input feature",
                                        id="add-add-feature",
                                        color="secondary",
                                        outline=True,
                                        className="mt-3",
                                    ),
                                ])

                            ],md=12),
                            
                        ],className="mb-4",),

                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H4("Outputs", className="mb-4"),
                                    dbc.Accordion(
                                        id="add-outputs-accordion",
                                        always_open=True
                                    ),
                                    dbc.Button(
                                        "➕ Add output ",
                                        id="add-add-output",
                                        color="secondary",
                                        outline=True,
                                        className="mt-3",
                                    ),
                                ]),

                            ],md=12),
                        ],className="mb-4",),

                            # Save button
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("Save Configuration", id="save-ml-model-config", color="primary", className="mt-4"),
                                ], className="text-center"),
                                dbc.Col(
                                    html.Div(
                                        id="save-model-feedback",
                                        className="ms-3 fw-semibold",
                                    ),
                                ),
                            ])

                        ], fluid=True),
                    
                ),
                className="my-3 shadow-sm",
            ),
        ])
    
    
        

