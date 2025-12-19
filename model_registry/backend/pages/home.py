from dash import html,dcc,dash_table
import dash_bootstrap_components as dbc

def home_layout():
    return dbc.Container(
        fluid=True,
        className="vh-100 p-4",
        children=[

            # Title
            html.H2(
                "Model Registry",
                className="text-primary text-center mb-4"
            ),

            # =========================
            # Filter bar
            # =========================
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(
                            dcc.Dropdown(
                                id="filter-project",
                                options=[
                                    {"label": "Project A", "value": "project_a"},
                                    {"label": "Project B", "value": "project_b"},
                                ],
                                placeholder="Project name",
                                clearable=True
                            ),
                            md=4
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="filter-model",
                                options=[
                                    {"label": "Model X", "value": "model_x"},
                                    {"label": "Model Y", "value": "model_y"},
                                ],
                                placeholder="Model name",
                                clearable=True
                            ),
                            md=4
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="filter-author",
                                options=[
                                    {"label": "Alice", "value": "alice"},
                                    {"label": "Bob", "value": "bob"},
                                ],
                                placeholder="Author",
                                clearable=True
                            ),
                            md=4
                        ),
                    ])
                ]),
                className="mb-4 shadow-sm"
            ),

            # =========================
            # Models table
            # =========================
            dbc.Card(
                dbc.CardBody([
                    dash_table.DataTable(
                        id="models-table",
                        columns=[
                            {"name": "Model name", "id": "model_name"},
                            {"name": "Authors", "id": "authors"},
                            {
                                "name": "Actions",
                                "id": "actions",
                                "presentation": "markdown"
                            },
                        ],
                        data=[
                            {
                                "model_name": "EEGNet v1",
                                "authors": "Carlos Suarez",
                                "actions": (
                                    '<span title="Monitoring">📊</span>&nbsp;&nbsp;'
                                    '<span title="Reports">📄</span>&nbsp;&nbsp;'
                                    '<span title="Edit model">✏️</span>&nbsp;&nbsp;'
                                    '<span title="Delete model">🗑️</span>'
                                )
                            },
                            {
                                "model_name": "CNN Classifier",
                                "authors": "Alice, Bob",
                                "actions": (
                                    '<span title="Monitoring">📊</span>&nbsp;&nbsp;'
                                    '<span title="Reports">📄</span>&nbsp;&nbsp;'
                                    '<span title="Edit model">✏️</span>&nbsp;&nbsp;'
                                    '<span title="Delete model">🗑️</span>'
                                )
                            }
                        ],
                        markdown_options={"html": True},
                        style_table={
                            "overflowX": "auto"
                        },
                        style_cell={
                            "textAlign": "center",
                            "padding": "10px",
                        },
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold",
                        },
                        style_as_list_view=True,
                    )
                ]),
                className="shadow-lg"
            )
        ]
    )

