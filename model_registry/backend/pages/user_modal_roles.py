from dash import html, dcc
import dash_bootstrap_components as dbc


def roles_modal():
    return dbc.Modal([

        # HEADER
        dbc.ModalHeader(
            dbc.ModalTitle("Manage Roles & Permissions")
        ),

        dbc.ModalBody([
            # store user id for callbacks
            dcc.Store(id="roles-user-id"),
            # User Info
            dbc.Card([
                dbc.CardBody([
                    html.H5("User Information", className="mb-3"),

                    dbc.Row([
                        dbc.Col([
                            html.Small("Full Name", className="text-muted"),
                            html.Div(id="roles-user-name", className="fw-bold")
                        ], width=6),

                        dbc.Col([
                            html.Small("Email (Username)", className="text-muted"),
                            html.Div(id="roles-user-email", className="fw-bold")
                        ], width=6),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Small("Laboratory", className="text-muted"),
                            html.Div(id="roles-user-laboratory", className="fw-bold")
                        ], width=12),    
                    ])

                ])
            ], className="mb-4"),


            # Roles Checklist
            dbc.Card([
                dbc.CardBody([

                    html.H5("Assigned Roles", className="mb-3"),

                    dcc.Checklist(
                        id="user-roles-checklist",
                        options=[],
                        value=[],
                        labelStyle={
                            "display": "flex",
                            "alignItems": "center",
                            "marginBottom": "8px",
                            "padding": "6px 10px",
                            "borderRadius": "6px",
                            "border": "1px solid #e9ecef",
                            "cursor": "pointer"
                        },
                        inputStyle={
                            "marginRight": "10px",
                            "transform": "scale(1.2)"
                        }
                    )

                ])
            ], className="mb-4"),


            # Permissions View
            dbc.Card([
                dbc.CardBody([

                    html.H5("Role Permissions", className="mb-3"),

                    html.Div(
                        id="role-permissions-view",
                        className="ps-2"
                    )

                ])
            ])

        ]),

        # FOOTER
        dbc.ModalFooter([
            dbc.Button("Close", id="btn-close-roles-modal"),
            dbc.Button("Save", id="btn-save-roles", color="primary")
        ]),

    ], id="roles-modal", is_open=False, size="lg")