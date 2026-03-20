import logging

import dash_bootstrap_components as dbc
import requests
from dash import dcc, html

from model_registry.backend.config.settings import API_BASE_URL
from model_registry.backend.utils.utils_edit_model import (
    get_value_from_list_of_dicts,
    normalize_date,
    normalize_features
)
from model_registry.backend.utils.utils_details_model import (
    package_row
)

logger = logging.getLogger(__name__)

def details_model_layout(project_id, model_id):
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

    value_validation=str(
    model.get("training_information", {}).get("validation", ""))

    return html.Div(
        [   
            dcc.Store(id="features-store-details", data=features),
            dcc.Store(
                id="outputs-store-details",
                data=outputs if outputs else []
            ),
            dcc.Download(id="download-model-file"),
            html.H3(
                f"Details Model: {model['model_identification'].get('ID', '')}",
                className="text-center my-4"
            ),
            dbc.Card(
                dbc.CardBody(
                    dbc.Container([
                        dbc.Row([
                            dbc.Col([
                                html.H4("Model Identification", className="mb-4"),
                                    html.Div([
                                        dbc.Label("Model ID", className="fw-semibold"),
                                        html.Div(model["model_identification"].get("ID", ""),className="fw-bold text-muted")
                                    ],className="mb-3"),
                                    html.Div([
                                        dbc.Label("Model UUID", className="fw-semibold"),
                                        html.Div(model["model_identification"].get("UUID", ""),className="fw-bold text-muted")
                                    ],className="mb-3"),
                                    html.Div([
                                        dbc.Label(
                                            "Model DOI",className="fw-semibold",),
                                        html.Div(children=model["model_identification"].get("doi", ""),className="fw-bold text-muted")
                                    ],className="mb-3"),
                                    html.Div([
                                        dbc.Label("Model Name",className="fw-semibold",),
                                        html.Div(children=model["model_identification"].get("name", ""),className="fw-bold text-muted")
                                    ],className="mb-3"),
                                    html.Div([
                                        dbc.Label("Model Version",className="fw-semibold",),
                                        html.Div(children=model["model_identification"].get("version", ""),className="fw-bold text-muted")
                                    ],className="mb-3"),
                            ],md=6,),

                            dbc.Col([
                                html.H4("Creation", className="mb-4"),
                                html.Div([
                                    dbc.Label(
                                        "Creation Date",
                                        className="fw-semibold"
                                    ),
                                    html.Div(children=normalize_date(model["model_identification"].get("creation_date", "")),className="fw-bold text-muted")
                                ],className="mb-3"),
                                html.Div([
                                    dbc.Label(
                                        "Author",
                                        className="fw-semibold"
                                    ),
                                    html.Div(children=model["model_identification"].get("author", ""),className="fw-bold text-muted",style={"height": "50px"}),
                                ], className="mb-3"),
                                html.Div([
                                        dbc.Label("Status", className="fw-semibold"),
                                        html.Div(model["model_identification"].get("status", "offline"),className="fw-bold text-muted")
                                    ],className="mb-3"),

                                html.Div([
                                        dbc.Label("Status Description",className="fw-semibold"),
                                        html.Div(model["model_identification"].get("status_description", ""),className="fw-bold text-muted",
                                            style={"height": "100px"},
                                        ),
                                    ],className="mb-3"), 
                            ],md=6,),
                        ],className="mb-4",),
                    
                        dbc.Row([
                            html.H4("Model Description", className="mb-4"),
                            dbc.Col([
                                html.Div([
                                    dbc.Label("Learner",className="fw-semibold"),
                                    html.Div(children=model["model_description"].get("learner", ""),className="fw-bold text-muted")
                                ],className="mb-3"),
                                html.Div([
                                    dbc.Label(
                                        "Model Type",
                                        className="fw-semibold"
                                    ),
                                    html.Div(children=model["model_description"].get("model_type", ""),className="fw-bold text-muted")
                                ],className="mb-3"),
                                html.Div([
                                    dbc.Label("Model Name",className="fw-semibold"),
                                    html.Div(children=model["model_description"].get("model_name", ""),className="fw-bold text-muted")
                                ],className="mb-3"),
                                
                                
                                html.Div([
                                    dbc.Label(
                                        "Model Description",
                                        className="fw-semibold"
                                    ),
                                    html.Div(children=model["model_description"].get("description", ""),className="fw-bold text-muted",
                                        style={"height": "150px"},
                                    ),
                                ], className="mb-3"),
                                html.Div([
                                    dbc.Label(
                                        "Language",
                                        className="fw-semibold"
                                    ),
                                    html.Div(children=language_name,className="fw-bold text-muted")
                                ], className="mb-3"),
                                html.Div([
                                    dbc.Label(
                                        "Language Version",
                                        className="fw-semibold"
                                    ),
                                    html.Div(children=language_version,className="fw-bold text-muted")
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
                                                p.get("version", "-"),
                                            )
                                            for i, p in enumerate(packages)
                                        ]
                                        or [package_row(0)],
                                    )
                                    
                                ]), 

                            ],md=6,),

                            dbc.Col([
                                html.Div([
                                    dbc.Label(
                                        "Model File",
                                        className="fw-semibold"
                                    ),
                                    html.Div(
                                        children=model["model_description"]["config_files"].get("model_file", ""),
                                        className="fw-bold text-muted"
                                    )
                                ],className="mb-3",),
                                html.Div([
                                    dbc.Label(
                                        "Configuration server",
                                        className="fw-semibold"
                                    ),
                                    html.Div(
                                        children=model["model_description"]["config_files"].get("server", ""),
                                        className="fw-bold text-muted"
                                    )
                                ], className="mb-3"),
                                html.Div([
                                    dbc.Label(
                                        "Configuration Port",
                                        className="fw-semibold"
                                    ),
                                    html.Div(
                                        children=model["model_description"]["config_files"].get("port", ""),
                                        className="fw-bold text-muted"
                                    )
                                ], className="mb-3"),
                                html.Div([
                                    dbc.Label(
                                        "Configuration REST API",
                                        className="fw-semibold"
                                    ),
                                    html.Div(
                                        children=model["model_description"]["config_files"].get("rest_api", ""),
                                        className="fw-bold text-muted"
                                    )
                                ], className="mb-3"),
                                html.Div([
                                    html.H5("Input time interval", className="mt-4"),
                                    html.Div([
                                        dbc.Label(
                                            "Input time interval value",
                                            className="fw-semibold"
                                        ),
                                        html.Div(
                                            children=model["model_description"].get("input_time_interval", {}).get("time_interval", {}).get("value", ""),
                                            className="fw-bold text-muted"
                                        ),
                                    ], className="mb-3"),
                                    html.Div([
                                        dbc.Label(
                                            "Input time interval units",
                                            className="fw-semibold"
                                        ),
                                        html.Div(children=model["model_description"].get("input_time_interval", {}).get("time_interval", {}).get("unit", ""),
                                                 className="fw-bold text-muted"),
                                    ], className="mb-3"),
                                    html.Div([
                                        dbc.Label(
                                            "Input time interval description",
                                            className="fw-semibold"
                                        ),
                                        html.Div(
                                            children=model["model_description"].get("input_time_interval", {}).get("description", ""),
                                            className="fw-bold text-muted"),
                                    ], className="mb-3"),
                                    html.H5("Aggregation", className="mt-4"),
                                    html.Div([
                                        dbc.Label(
                                            "Input time interval aggregation",
                                            className="fw-semibold"
                                        ),
                                        html.Div(
                                            children=model["model_description"].get("input_time_interval", {}).get("aggregation", {}).get("method", ""),
                                            className="fw-bold text-muted"
                                        )
                                    ], className="mb-3"),
                                    html.Div([
                                        dbc.Label(
                                            "Input time interval aggregation description",
                                            className="fw-semibold"
                                        ),
                                        html.Div(
                                            children=model["model_description"].get("input_time_interval", {}).get("aggregation", {}).get("description", ""),
                                            className="fw-bold text-muted"
                                        )
                                    ], className="mb-3"),

                                ])

                            ],md=6,),
                        ],className="mb-4",),    

                        dbc.Row([
                            html.H4("Training information", className="mb-4"),
                            dbc.Col([
                                html.Div([
                                    html.H5("Hyperparameters", className="mt-4"),
                                    html.Div([
                                        dbc.Label(
                                            "Number of trees",
                                            className="fw-semibold"
                                        ),
                                        html.Div(
                                            children=model.get("training_information", {}).get("hyperparameters", {}).get("number_of_trees", ""),
                                            className="fw-bold text-muted"
                                        )
                                    ], className="mb-3"),
                                    html.Div([
                                        dbc.Label(
                                            "Maximum depth",
                                            className="fw-semibold"
                                        ),
                                        html.Div(
                                            children=model.get("training_information", {}).get("hyperparameters", {}).get("max_tree_depth", ""),
                                            className="fw-bold text-muted"
                                        )
                                    ], className="mb-3"),
                                    html.Div([
                                        dbc.Label(
                                            "Minimum number of instances per leaf",
                                            className="fw-semibold"
                                        ),
                                        html.Div(
                                            children=model.get("training_information", {}).get("hyperparameters", {}).get("min_number_instances_per_leaf", ""),
                                        )
                                    ], className="mb-3"),
                                    html.Div([
                                        dbc.Label(
                                            "Input committees",
                                            className="fw-semibold"
                                        ),
                                        html.Div(
                                            children=model.get("training_information", {}).get("hyperparameters", {}).get("committees", ""),
                                        )
                                    ], className="mb-3"),
                                    html.Div([
                                        dbc.Label(
                                            "Input instance based correction",
                                            className="fw-semibold"
                                        ),
                                        html.Div(
                                            children=model.get("training_information", {}).get("hyperparameters", {}).get("instance_based_corrections", ""),
                                            className="fw-bold text-muted"
                                        )
                                    ], className="mb-3"),
                                ])
                            ],md=6,),

                            dbc.Col([
                                html.Div([
                                    dbc.Label(
                                        "Number of Instances",
                                        className="fw-semibold"
                                    ),
                                    html.Div(
                                        children=model.get("training_information", {}).get("number_of_instances", ""),
                                        className="fw-bold text-muted"
                                    )
                                ], className="mb-3"),
                                html.Div([
                                    dbc.Label(
                                        "Validation",
                                        className="fw-semibold"
                                    ),
                                    html.Div(
                                        children=value_validation,
                                        className="fw-bold text-muted"
                                    )
                                ], className="mb-3"),
                                html.Div([
                                    dbc.Label(
                                        "Training experiments ID",
                                        className="fw-semibold"
                                    ),
                                    html.Div(
                                        children=model.get("training_information", {}).get("experiments_ID", ""),
                                        className="fw-bold text-muted"
                                    )
                                ], className="mb-3"),
                            ],md=6,),
                                    
                        ],className="mb-4",),

                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H4("Inputs", className="mb-4"),
                                    dbc.Accordion(
                                        id="features-accordion-details",
                                        always_open=True
                                    ),                                    
                                ])

                            ],md=12),
                            
                        ],className="mb-4",),

                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H4("Outputs", className="mb-4"),
                                    dbc.Accordion(
                                        id="outputs-accordion-details",
                                        always_open=True
                                    )
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
                                    [
                                        html.I(className="bi bi-download me-2"),
                                        "Download model"
                                    ],
                                    id="download-model",
                                    color="primary",
                                ),
                                width="auto",
                            ),


                            dbc.Col(
                                html.Div(
                                    id="download-feedback",
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

