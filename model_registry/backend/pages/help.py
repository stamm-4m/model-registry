import dash
from dash import html
import dash_bootstrap_components as dbc

def help_layout():

    sidebar = dbc.Card(
        [
            dbc.CardHeader(html.H5("Documentation")),
            dbc.CardBody(
                dbc.Nav(
                    [
                        dbc.NavLink("Overview", href="#overview", external_link=True),
                        dbc.NavLink("Architecture", href="#architecture", external_link=True),
                        dbc.NavLink("Upload Workflow", href="#upload", external_link=True),
                        dbc.NavLink("Prediction Workflow", href="#prediction", external_link=True),
                        dbc.NavLink("API Endpoints", href="#api", external_link=True),
                        dbc.NavLink("Configuration Files", href="#config", external_link=True),
                        dbc.NavLink("Error Handling", href="#errors", external_link=True),
                        dbc.NavLink("FAQ", href="#faq", external_link=True),
                    ],
                    vertical=True,
                    pills=True,
                )
            ),
        ],
        className="h-100",
    )

    content = html.Div(
        [
            html.H2("Help & Documentation", className="mb-4"),

            # Overview
            html.H4("Overview", id="overview"),
            html.P(
                """
                This backend application provides model registration,
                validation, and prediction services. It supports YAML
                configuration files, EDF processing, and REST-based
                communication between components.
                """
            ),

            html.Hr(),

            # Architecture
            html.H4("Architecture", id="architecture"),
            html.P("Main components of the system:"),
            html.Ul(
                [
                    html.Li("Models: Model validation and prediction logic."),
                    html.Li("Views: Dash UI components and callbacks."),
                    html.Li("Data: Uploaded datasets and processed files."),
                    html.Li("InfluxDb: Database integration layer."),
                    html.Li("R Integration: External R scripts execution."),
                ]
            ),
            html.P(
                "Workflow: Upload → Validate → Store → Predict → Save Results."
            ),

            html.Hr(),

            # Upload Workflow
            html.H4("Upload Workflow", id="upload"),
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P("1. Upload a valid file (.edf, .yaml, etc.)."),
                            html.P("2. Fill required metadata fields."),
                            html.P("3. Backend validates structure and variables."),
                            html.P("4. File is stored in the server directory."),
                        ],
                        title="How to Upload Files",
                    ),
                ],
                start_collapsed=True,
            ),

            html.Hr(),

            # Prediction Workflow
            html.H4("Prediction Workflow", id="prediction"),
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P("1. Select a registered model."),
                            html.P("2. Provide required input variables."),
                            html.P("3. Backend executes prediction logic."),
                            html.P("4. Results are displayed and stored."),
                        ],
                        title="How Prediction Works",
                    ),
                ],
                start_collapsed=True,
            ),

            html.Hr(),

            # API Endpoints
            html.H4("API Endpoints", id="api"),
            dbc.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Method"),
                                html.Th("Endpoint"),
                                html.Th("Description"),
                            ]
                        )
                    ),
                    html.Tbody(
                        [
                            html.Tr(
                                [
                                    html.Td("POST"),
                                    html.Td("/predict"),
                                    html.Td("Run model prediction"),
                                ]
                            ),
                            html.Tr(
                                [
                                    html.Td("GET"),
                                    html.Td("/models"),
                                    html.Td("List registered models"),
                                ]
                            ),
                        ]
                    ),
                ],
                bordered=True,
                striped=True,
                hover=True,
                responsive=True,
            ),

            html.Hr(),

            # Configuration Files
            html.H4("Configuration Files", id="config"),
            html.P("YAML configuration must include:"),
            html.Ul(
                [
                    html.Li("model_name"),
                    html.Li("model_version"),
                    html.Li("input_variables"),
                    html.Li("output_variables"),
                ]
            ),
            html.P("Ensure variable names match dataset columns."),

            html.Hr(),

            # Error Handling
            html.H4("Error Handling", id="errors"),
            html.Ul(
                [
                    html.Li("Validation Error: Missing required variables."),
                    html.Li("Format Error: Invalid file type."),
                    html.Li("Server Error (500): Internal processing failure."),
                ]
            ),

            html.Hr(),

            # FAQ
            html.H4("FAQ", id="faq"),
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        "Verify that all required variables exist in the dataset.",
                        title="Why does my model fail validation?",
                    ),
                    dbc.AccordionItem(
                        "Check backend logs for detailed error information.",
                        title="Where can I see server errors?",
                    ),
                ],
                start_collapsed=True,
            ),
        ],
        className="p-4",
    )
    return dbc.Container(html.H4("Page in construction"))
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(sidebar, width=3),
                    dbc.Col(content, width=9),
                ],
                className="mt-4",
            )
        ],
        fluid=True,
    )
