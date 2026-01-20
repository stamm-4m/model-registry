import dash_bootstrap_components as dbc
from dash import html,dcc

def add_project_layout():


    return html.Div([ 
        dbc.Container(
        [
            dbc.Alert(
                id="project-form-alert",
                is_open=False,
                color="danger",
            ),

            dbc.Form(
                [
                    dbc.FormFloating(
                        [
                            dbc.Input(id="project-id", type="text", placeholder="P0001"),
                            dbc.Label("Project ID"),
                        ],
                        className="mb-3",
                    ),

                    dbc.FormFloating(
                        [
                            dbc.Input(id="project-name", type="text", placeholder="Project Name"),
                            dbc.Label("Project Name"),
                        ],
                        className="mb-3",
                    ),

                    dbc.FormFloating(
                        [
                            dbc.Textarea(
                                id="project-description",
                                placeholder="Project description",
                                style={"height": "120px"},
                            ),
                            dbc.Label("Description"),
                        ],
                        className="mb-3",
                    ),

                    dbc.FormFloating(
                        [
                            dbc.Input(id="project-coordinator", type="text", placeholder="Coordinator"),
                            dbc.Label("Coordinator"),
                        ],
                        className="mb-3",
                    ),

                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.FormFloating(
                                    [
                                        dbc.Input(id="project-start-date", type="date"),
                                        dbc.Label("Start Date"),
                                    ]
                                ),
                                md=6,
                            ),
                            dbc.Col(
                                dbc.FormFloating(
                                    [
                                        dbc.Input(id="project-end-date", type="date"),
                                        dbc.Label("End Date"),
                                    ]
                                ),
                                md=6,
                            ),
                        ],
                        className="mb-3",
                    ),

                    dbc.FormFloating(
                        [
                            dcc.Dropdown(
                                id="assigned-users",
                                multi=True,
                                placeholder="Assign users",
                            )
                        ],
                        className="mb-4",
                    ),

                    dbc.Button(
                        "Create Project",
                        id="open-confirm-modal",
                        color="primary",
                        className="w-100",
                    ),
                ]
            ),

            # Confirmation modal
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(id="project-modal-title")),
                    dbc.ModalBody(id="project-modal-body"),
                    dbc.ModalFooter(
                        dbc.Button(
                            "OK",
                            id="project-modal-ok",
                            color="primary",
                        )
                    ),
                ],
                id="confirm-project-modal",
                is_open=False,
            ),
        ],
        className="mt-4",)
        
    ])