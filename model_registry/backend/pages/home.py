from dash import html,dcc,dash_table
import dash_ag_grid as dag
import dash_bootstrap_components as dbc

def home_layout():
    models_grid = dag.AgGrid(
        id="models-grid",
        columnDefs=[
            {"headerName": "Model", "field": "model_name"},
            {"headerName": "Author", "field": "authors", "width": 600},

            {
                "headerName": "Status",
                "field": "status",
                "cellRenderer": "StatusRenderer",
                "width": 100
            },
            {
                "headerName": "Edit",
                "field": "edit",
                "cellRenderer": "EditIconRenderer",
                "width": 80
            }
        ],
        rowData=[],
        defaultColDef={
            "sortable": True,
            "filter": True,
            "resizable": True
        },
        dashGridOptions={
            "rowHeight": 45
        }
    )

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
                    models_grid
                ]),
                className="shadow-lg"
            )
        ]
    )

