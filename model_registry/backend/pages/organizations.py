import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from model_registry.backend.pages.department_modal import department_modal
from model_registry.backend.pages.add_organization import organization_modal
from model_registry.backend.pages.user_modal import user_modal
from model_registry.backend.utils.utils_department import toast_confirm_delete_dept
from model_registry.backend.utils.utils_organization import toast_confirm_delete
from model_registry.backend.utils.utils_users import toast_confirm_delete_user


def organizations_layout():
    return dbc.Container([
        # Stores
        dcc.Store(id="org-edit-id"),
        dcc.Store(id="org-delete-id"),
        dcc.Store(id="org-refresh-trigger"),
        dcc.Store(id="dept-edit-id"),
        dcc.Store(id="dept-delete-id"),
        dcc.Store(id="dept-refresh-trigger"),
        dcc.Store(id="user-edit-id"),
        dcc.Store(id="user-delete-id"),
        dcc.Store(id="user-refresh-trigger"),

        # Title
        dbc.Row([
            dbc.Col([
                html.H1("Panel Organization", className="mb-4 mt-4")
            ])
        ]),

        # Tabs
        dbc.Tabs([
            # TAB 1: Organizations
            dbc.Tab(label="Organizations", tab_id="tab-org", children=[
                dbc.Card([
                    dbc.CardHeader("Organizations"),
                    dbc.CardBody([
                        dbc.Button("+ New Organization", id="btn-open-org-modal", color="primary", className="mb-3"),
                        toast_confirm_delete(),
                        html.Div(id="organizations-table")
                    ]),
                    organization_modal()
                ])
            ]),

            # TAB 2: Departments
            dbc.Tab(label="Departments", tab_id="tab-dept", children=[
                dbc.Card([
                    dbc.CardHeader("Departments"),
                    dbc.CardBody([
                        dbc.Button(
                            "+ New Department",
                            id="btn-open-dept-modal",
                            color="success",
                            className="mb-3"
                        ),
                        toast_confirm_delete_dept(),
                        html.Div(id="departments-table"),
                        department_modal()
                    ])
                ])
            ]),

            # TAB 3: Users
            dbc.Tab(label="Users by Department", tab_id="tab-user", children=[
                dbc.Card([
                    dbc.CardHeader("Users by Department"),
                    dbc.CardBody([
                        dbc.Button("+ New User", id="btn-open-user-modal", color="info", className="mb-3"),
                        toast_confirm_delete_user(),
                        html.Div(id="users-table"),
                        user_modal()
                    ])
                ])
            ])
        ], id="tabs-organization", active_tab="tab-org"),

        # Modal
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