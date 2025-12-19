import dash_bootstrap_components as dbc
from dash import dcc, html


def top_toolbar():
    """
    Top toolbar with configuration options for a Dash page.
    """
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    dbc.Row(
                        [
                            dbc.Col(
                                html.H5("Configuration", className="mb-0"),
                                width="auto",
                            ),

                            dbc.Col(
                                dcc.Dropdown(
                                    id="combo-dataset",
                                    options=[
                                        {
                                            "label": "Project_IndPenSim",
                                            "value": "indpensim",
                                        },
                                        {
                                            "label": "Bioindustry_E.Coli",
                                            "value": "ecoli",
                                        },
                                    ],
                                    placeholder="Select project",
                                    clearable=False,
                                ),
                                width=3,
                            ),

                            dbc.Col(
                                dcc.Dropdown(
                                    id="combo-model",
                                    options=[
                                        {
                                            "label": "0001_[python]_penicillin_RF",
                                            "value": "model_1",
                                        },
                                        {
                                            "label": "0002_[R]_penicillin_RF",
                                            "value": "model_2",
                                        },
                                    ],
                                    placeholder="Select model",
                                    clearable=False,
                                ),
                                width=3,
                            ),

                            dbc.Col(
                            [
                                dbc.Button(
                                    html.I(className="bi bi-gear",style={"fontSize": "1.2rem"},),
                                    id="btn-settings",
                                    color="secondary",
                                    outline=True,
                                ),
                                dbc.Tooltip(
                                    "Settings",
                                    target="btn-settings",
                                ),
                            ],
                                width="auto",
                            ),
                        ],
                        align="center",
                        className="g-2",
                    )
                ),
                className="mb-3 shadow-sm",
            ),

            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Advanced Settings")),
                    dbc.ModalBody(
                        dcc.Checklist(
                            id="check-options",
                            options=[
                                {
                                    "label": "Normalize data",
                                    "value": "norm",
                                },
                                {
                                    "label": "Show grid",
                                    "value": "grid",
                                },
                            ],
                        )
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close",
                            id="close-settings",
                            color="secondary",
                        )
                    ),
                ],
                id="settings-modal",
                is_open=False,
            ),
        ]
    )
