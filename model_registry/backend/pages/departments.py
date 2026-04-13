from dash import dcc, html
import dash_bootstrap_components as dbc

def departments_layout():
    """Layout for departments page using Bootstrap components."""
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.H1("Departments", className="mb-4"),
                        width=12
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Departments List"),
                                dbc.CardBody(
                                    [
                                        html.P("Department content will be displayed here"),
                                        dcc.Loading(
                                            id="loading-departments",
                                            type="default",
                                            children=html.Div(id="departments-data")
                                        )
                                    ]
                                )
                            ]
                        ),
                        width=12
                    )
                ],
                className="mb-4"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Add Department",
                            color="primary",
                            id="btn-add-department"
                        ),
                        width=12
                    )
                ]
            )
        ],
        fluid=True,
        className="p-4"
    )