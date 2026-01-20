import requests
from dash import html, dcc
import dash_bootstrap_components as dbc
import logging
from model_registry.backend.config.settings import API_BASE_URL
from model_registry.backend.utils.utils_edit_model import (get_value_from_list_of_dicts, normalize_date, normalize_features, package_row)
logger = logging.getLogger(__name__)

def edit_model_layout(project_id, model_id):
    response = requests.get(
        f"{API_BASE_URL}{project_id}/metadata/{model_id}"
    )
    model = response.json()
    language_data = model.get("model_description", {}).get("language", [])
    language_name = get_value_from_list_of_dicts(language_data, "name")
    language_version = get_value_from_list_of_dicts(language_data, "version")
    packages = model.get("model_description", {}).get("packages", [])
    features = model.get("inputs", {}).get("features", [])
    features= normalize_features(features)
    outputs = model.get("outputs",{}).get("information",[])
    outputs = normalize_features(outputs)



    return html.Div(
        [   
            dcc.Store(id="features-store", data=features),
            dcc.Store(
                id="outputs-store",
                data=outputs if outputs else []
            ),
            html.H3(
                f"Edit Model: {model['model_identification'].get('ID', '')}",
                className="text-center my-4"
            ),
            dbc.Card(
                dbc.CardBody(
                    dbc.Container([
                        dbc.Row([
                            dbc.Col([
                                html.H4("Model Identification", className="mb-4"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            value=model["model_identification"].get("ID", ""),
                                            readonly=True,
                                            plaintext=True,
                                            className="fw-bold text-muted"
                                        ),
                                        dbc.Label("Model ID"),
                                    ],className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="edit_model_uuid",
                                            type="text",
                                            placeholder="Model UUID",
                                            value=model["model_identification"].get("UUID", ""),
                                        ),
                                        dbc.Label("Model UUID"),
                                    ],className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="edit_model_doi",
                                            type="text",
                                            placeholder="Model DOI",
                                            value=model["model_identification"].get("doi", ""),
                                        ),
                                        dbc.Label("Model DOI"),
                                    ],className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="edit_name",
                                            type="text",
                                            placeholder="Model Name",
                                            value=model["model_identification"].get("name", ""),
                                        ),
                                        dbc.Label("Model Name"),
                                    ],className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="edit_model_version",
                                            type="text",
                                            placeholder="Model Version",
                                            value=model["model_identification"].get("version", ""),
                                        ),
                                        dbc.Label("Model Version"),
                                    ],className="mb-3"),

                            ],md=6,),

                            dbc.Col([
                                html.H4("Creation", className="mb-4"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="edit_creation_date",
                                        type="date",
                                        placeholder="Creation Date",
                                        value=normalize_date(model["model_identification"].get("creation_date", "")),
                                    ),
                                    dbc.Label("Creation Date"),
                                ],className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Textarea(
                                        id="edit_author",
                                        placeholder="Author",
                                        value=model["model_identification"].get("author", ""),
                                        style={"height": "100px"},
                                    ),
                                    dbc.Label("Author"),
                                ], className="mb-3"),
                                html.Div([
                                        dbc.Label("Status", className="fw-semibold"),
                                        dbc.RadioItems(
                                            id="edit_status",
                                            options=[
                                                {"label": "Online", "value": "online"},
                                                {"label": "Offline", "value": "offline"},
                                            ],
                                            value=model["model_identification"].get("status", "offline"),
                                            inline=True,
                                        ),
                                    ],className="mb-3"),

                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="edit_status_description",
                                            type="text",
                                            placeholder="Status Description",
                                            value=model["model_identification"].get("status_description", ""),
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
                                        id="edit_learner",
                                        type="text",
                                        placeholder="Learner",
                                        value=model["model_description"].get("learner", ""),
                                    ),
                                    dbc.Label("Learner"),
                                ],className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="edit_model_type",
                                        type="text",
                                        placeholder="Model Type",
                                        value=model["model_description"].get("model_type", ""),
                                    ),
                                    dbc.Label("Model Type"),
                                ],className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="edit_model_name",
                                        type="text",
                                        placeholder="Model Name",
                                        value=model["model_description"].get("model_name", ""),
                                    ),
                                    dbc.Label("Model Name"),
                                ],className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Textarea(
                                        id="edit_description",
                                        placeholder="Model Description",
                                        value=model["model_description"].get("description", ""),
                                        style={"height": "150px"},
                                    ),
                                    dbc.Label("Model Description"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="edit_language",
                                        type="text",
                                        placeholder="Language",
                                        value=language_name,
                                    ),
                                    dbc.Label("Language"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="edit_language_version",
                                        type="text",
                                        placeholder="Language Version",
                                        value=language_version,
                                    ),
                                    dbc.Label("Language Version"),
                                ], className="mb-3"),
                                
                                html.Div(
                                [
                                    html.H5("Packages", className="mt-4"),
                                    html.Div(
                                        id="packages-container",
                                        children=[
                                            package_row(
                                                i,
                                                p.get("package", ""),
                                                p.get("version", ""),
                                            )
                                            for i, p in enumerate(packages)
                                        ]
                                        or [package_row(0)],
                                    ),
                                    dbc.Button(
                                        "➕ Add package",
                                        id="add-package",
                                        color="secondary",
                                        outline=True,
                                        className="mt-2",
                                    ),
                                ]), 

                            ],md=6,),

                            dbc.Col([
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="edit_config_model_file",
                                        type="text",
                                        placeholder="Configuration Model File",
                                        value=model["model_description"]["config_files"].get("model_file", ""),
                                    ),
                                    dbc.Label("Model File"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="edit_config_server",
                                        type="text",
                                        placeholder="Configuration Server",
                                        value=model["model_description"]["config_files"].get("server", ""),
                                    ),
                                    dbc.Label("Configuration Server"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="edit_config_port",
                                        type="text",
                                        placeholder="Configuration Port",
                                        value=model["model_description"]["config_files"].get("port", ""),
                                    ),
                                    dbc.Label("Configuration Port"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="edit_config_rest_api",
                                        type="text",
                                        placeholder="Configuration REST API",
                                        value=model["model_description"]["config_files"].get("rest_api", ""),
                                    ),
                                    dbc.Label("Configuration REST API"),
                                ], className="mb-3"),
                                html.Div([
                                    html.H5("Input time interval", className="mt-4"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="edit_time_interval",
                                            type="number",
                                            placeholder="Input time interval",
                                            value=model["model_description"].get("input_time_interval", {}).get("time_interval", {}).get("value", ""),
                                        ),
                                        dbc.Label("Input time interval"),
                                    ], className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="edit_time_interval_units",
                                            type="text",
                                            placeholder="Input time interval units",
                                            value=model["model_description"].get("input_time_interval", {}).get("time_interval", {}).get("unit", ""),
                                        ),
                                        dbc.Label("Input time interval units"),
                                    ], className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="edit_time_interval_description",
                                            type="text",
                                            placeholder="Input time interval description",
                                            value=model["model_description"].get("input_time_interval", {}).get("description", ""),
                                        ),
                                        dbc.Label("Input time interval description"),
                                    ], className="mb-3"),
                                    html.H5("Aggregation", className="mt-4"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="edit_time_interval_aggregation",
                                            type="text",
                                            placeholder="Input time interval aggregation",
                                            value=model["model_description"].get("input_time_interval", {}).get("aggregation", {}).get("method", ""),
                                        ),
                                        dbc.Label("Input time interval aggregation"),
                                    ], className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="edit_time_interval_aggregation_description",
                                            type="text",
                                            placeholder="Input time interval aggregation description",
                                            value=model["model_description"].get("input_time_interval", {}).get("aggregation", {}).get("description", ""),
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
                                            id="edit_number_of_trees",
                                            type="number",
                                            placeholder="Input number of trees",
                                            value=model.get("training_information", {}).get("hyperparameters", {}).get("number_of_trees", ""),
                                        ),
                                        dbc.Label("Number of trees"),
                                    ], className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="edit_max_tree_depth",
                                            type="number",
                                            placeholder="Maximum depth",
                                            value=model.get("training_information", {}).get("hyperparameters", {}).get("max_tree_depth", ""),
                                        ),
                                        dbc.Label("Maximum depth"),
                                    ], className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="edit_min_number_instances_per_leaf",
                                            type="number",
                                            placeholder="Input min number instances per leaf",
                                            value=model.get("training_information", {}).get("hyperparameters", {}).get("min_number_instances_per_leaf", ""),
                                        ),
                                        dbc.Label("Input min number instances per leaf"),
                                    ], className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="edit_committees",
                                            type="number",
                                            placeholder="Input committees",
                                            value=model.get("training_information", {}).get("hyperparameters", {}).get("committees", ""),
                                        ),
                                        dbc.Label("Input committees"),
                                    ], className="mb-3"),
                                    dbc.FormFloating([
                                        dbc.Input(
                                            id="edit_instance_based_correction",
                                            type="number",
                                            placeholder="Input instance based correction",
                                            value=model.get("training_information", {}).get("hyperparameters", {}).get("instance_based_corrections", ""),
                                        ),
                                        dbc.Label("Input instance based correction"),
                                    ], className="mb-3"),
                                ])
                            ],md=6,),

                            dbc.Col([
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="edit_number_of_instances",
                                        type="text",
                                        placeholder="Number of Instances",
                                        value=model.get("training_information", {}).get("number_of_instances", ""),
                                    ),
                                    dbc.Label("Number of Instances"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(
                                        id="edit_validation",
                                        type="text",
                                        placeholder="Validation",
                                        value=model.get("training_information", {}).get("validation", ""),
                                    ),
                                    dbc.Label("Validation"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Textarea(
                                        id="edit_experiments_id",
                                        placeholder="Experiments ID",
                                        value=model.get("training_information", {}).get("experiments_ID", ""),
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
                                        id="features-accordion",
                                        always_open=True
                                    ),
                                    dbc.Button(
                                        "➕ Add input feature",
                                        id="add-feature",
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
                                        id="outputs-accordion",
                                        always_open=True
                                    ),
                                    dbc.Button(
                                        "➕ Add output ",
                                        id="add-output",
                                        color="secondary",
                                        outline=True,
                                        className="mt-3",
                                    ),
                                ]),

                            ],md=12),
                        ],className="mb-4",),


                    ])
                )
            ),
            dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    "← Back to list",
                                    id="back-to-list",
                                    color="secondary",
                                    outline=True,
                                    className="me-2",
                                ),
                                width="auto",
                            ),

                            dbc.Col(
                                dbc.Button(
                                    "💾 Save changes",
                                    id="save-model",
                                    color="primary",
                                ),
                                width="auto",
                            ),

                            dbc.Col(
                                html.Div(
                                    id="save-feedback",
                                    className="ms-3 fw-semibold",
                                ),
                            ),
                        ],
                        className="align-items-center mt-4",
                    ),
            dcc.Store(id="edit-model-info", data={
                "project_id": project_id,
                "model_id": model_id
            })

    ])

