import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc

def users_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Manage Users", className="mb-4")
            ], width=12)
        ], className="mt-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Button("Add User", id="btn-add-user", color="primary", className="mb-3")
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.Div(id="users-table-container")
            ], width=12)
        ], className="mt-3"),
        
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Add User")),
            dbc.ModalBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Username"),
                            dbc.Input(id="input-username", type="text", placeholder="Enter username")
                        ], width=12, className="mb-3")
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Email"),
                            dbc.Input(id="input-email", type="email", placeholder="Enter email")
                        ], width=12, className="mb-3")
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Role"),
                            dcc.Dropdown(id="input-role", options=[
                                {"label": "Admin", "value": "admin"},
                                {"label": "User", "value": "user"}
                            ])
                        ], width=12)
                    ])
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="btn-cancel", className="me-2"),
                dbc.Button("Save", id="btn-save-user", color="primary")
            ])
        ], id="modal-add-user", is_open=False)
    ], fluid=True)