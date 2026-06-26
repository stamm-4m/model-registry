import dash_bootstrap_components as dbc
from dash import dcc, html


def roles_modal():
    return dbc.Modal(
        [
            # HEADER
            dbc.ModalHeader(dbc.ModalTitle("Manage Roles & Permissions")),
            dbc.ModalBody(
                [
                    # Store user id for callbacks
                    dcc.Store(id="roles-user-id"),
                    # User Information Card
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H5("User Information", className="mb-3"),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Small(
                                                        "Full Name",
                                                        className="text-muted",
                                                    ),
                                                    html.Div(
                                                        id="roles-user-name",
                                                        className="fw-bold",
                                                    ),
                                                ],
                                                width=6,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Small(
                                                        "Email (Username)",
                                                        className="text-muted",
                                                    ),
                                                    html.Div(
                                                        id="roles-user-email",
                                                        className="fw-bold",
                                                    ),
                                                ],
                                                width=6,
                                            ),
                                        ]
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Small(
                                                        "Laboratory",
                                                        className="text-muted",
                                                    ),
                                                    html.Div(
                                                        id="roles-user-laboratory",
                                                        className="fw-bold",
                                                    ),
                                                ],
                                                width=12,
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ],
                        className="mb-4",
                    ),
                    # Assigned Roles Checklist
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H5("Assigned Roles to User", className="mb-3"),
                                    # Checklist for all roles assigned to the user
                                    dcc.Checklist(
                                        id="user-roles-checklist",
                                        options=[],  # To be filled dynamically with all available roles
                                        value=[],
                                        labelStyle={
                                            "display": "flex",
                                            "alignItems": "center",
                                            "marginBottom": "8px",
                                            "padding": "6px 10px",
                                            "borderRadius": "6px",
                                            "border": "1px solid #e9ecef",
                                            "cursor": "pointer",
                                        },
                                        inputStyle={
                                            "marginRight": "10px",
                                            "transform": "scale(1.2)",
                                        },
                                    ),
                                    # Role Permissions Accordion (expandable)
                                    dbc.Accordion(
                                        [
                                            dbc.AccordionItem(
                                                [
                                                    html.H5(
                                                        "Role Permissions",
                                                        className="mb-3",
                                                    ),
                                                    # This div will be filled dynamically with the permissions for the selected role(s)
                                                    html.Div(
                                                        id="role-permissions-view",
                                                        className="ps-2",
                                                    ),
                                                ],
                                                title="Show Role Permissions",
                                            )
                                        ],
                                        start_collapsed=True,
                                        className="mb-4",
                                    ),
                                ]
                            )
                        ],
                        className="mb-4",
                    ),
                    # Project and Model Access Card
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "Project and Model Access", className="mb-3"
                                    ),
                                    # Project selection dropdown
                                    html.Label("Project", className="mb-1 fw-bold"),
                                    dcc.Dropdown(
                                        id="user-projects-dropdown",
                                        options=[],  # To be filled dynamically with available projects
                                        value=None,
                                        placeholder="Select a project",
                                        clearable=True,
                                        className="mb-3",
                                    ),
                                    # Model selection dropdown (filtered by project)
                                    html.Label("Model", className="mb-1 fw-bold"),
                                    dcc.Dropdown(
                                        id="user-models-dropdown",
                                        options=[],  # To be filled dynamically with models for the selected project
                                        value=None,
                                        placeholder="Select a model",
                                        clearable=True,
                                        className="mb-3",
                                    ),
                                    # Checklist for assigning model-specific permissions (only permissions over the selected model resource)
                                    html.Label(
                                        "Assign Permissions to Model",
                                        className="mb-1 fw-bold",
                                    ),
                                    dcc.Checklist(
                                        id="user-models-permissions-checklist",
                                        options=[],  # To be filled dynamically with available permissions for the selected model
                                        value=[],
                                        labelStyle={
                                            "display": "flex",
                                            "alignItems": "center",
                                            "marginBottom": "8px",
                                            "padding": "6px 10px",
                                            "borderRadius": "6px",
                                            "border": "1px solid #e9ecef",
                                            "cursor": "pointer",
                                        },
                                        inputStyle={
                                            "marginRight": "10px",
                                            "transform": "scale(1.2)",
                                        },
                                    ),
                                    # You can add a description or tooltip for each role if needed
                                ]
                            )
                        ],
                        className="mb-4",
                    ),
                ]
            ),
            # FOOTER
            dbc.ModalFooter(
                [
                    dbc.Button("Close", id="btn-close-roles-modal"),
                    dbc.Button("Save", id="btn-save-roles", color="primary"),
                ]
            ),
        ],
        id="roles-modal",
        is_open=False,
        size="lg",
    )
