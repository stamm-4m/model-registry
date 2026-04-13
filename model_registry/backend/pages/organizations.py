import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

def organizations_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Management Organizations", className="mb-4 mt-4")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Organizations"),
                    dbc.CardBody([
                        dbc.Button("+ New Organization", color="primary", className="mb-3"),
                        html.Div(id="organizations-table")
                    ])
                ])
            ], md=12)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Departments"),
                    dbc.CardBody([
                        dbc.Button("+ New Department", color="success", className="mb-3"),
                        html.Div(id="departments-table")
                    ])
                ])
            ], md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Users by Department"),
                    dbc.CardBody([
                        dbc.Button("+ New User", color="info", className="mb-3"),
                        html.Div(id="users-table")
                    ])
                ])
            ], md=6)
        ]),
        
        dbc.Modal([
            dbc.ModalHeader("New Organization"),
            dbc.ModalBody([
                dbc.Input(id="org-name", placeholder="Organization Name", className="mb-3"),
                dbc.Input(id="org-description", placeholder="Description", type="textarea", className="mb-3")
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", color="secondary", id="close-org-modal"),
                dbc.Button("Save", color="primary", id="save-org-btn")
            ])
        ], id="org-modal")
    ], fluid=True)