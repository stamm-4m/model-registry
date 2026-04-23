import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from model_registry.backend.pages.department_modal import department_modal
from model_registry.backend.pages.add_organization import organization_modal
from model_registry.backend.pages.laboratory_modal import laboratory_modal
from model_registry.backend.pages.user_modal import user_modal
from model_registry.backend.pages.user_modal_roles import roles_modal
from model_registry.backend.utils.utils_department import toast_confirm_delete_dept
from model_registry.backend.utils.utils_laboratory import toast_confirm_delete_lab
from model_registry.backend.utils.utils_organization import toast_confirm_delete
from model_registry.backend.utils.utils_users import toast_confirm_delete_user


def organizations_layout():
    return dbc.Container([

        # STORES
        dcc.Store(id="org-edit-id"),
        dcc.Store(id="org-delete-id"),
        dcc.Store(id="org-refresh-trigger"),
        dcc.Store(id="dept-edit-id"),
        dcc.Store(id="dept-delete-id"),
        dcc.Store(id="dept-refresh-trigger"),
        dcc.Store(id="lab-edit-id"),
        dcc.Store(id="lab-delete-id"),
        dcc.Store(id="lab-refresh-trigger"),
        dcc.Store(id="user-edit-id"),
        dcc.Store(id="user-delete-id"),
        dcc.Store(id="user-refresh-trigger"),

        # 🔷 HEADER
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2("Organization Panel", className="fw-bold mb-0"),
                    html.P("Manage organizations, departments, laboratories and users",
                           className="text-muted mb-0")
                ])
            ])
        ], className="mb-4 mt-3"),

        # 🔷 TABS
        dbc.Tabs(
            id="tabs-organization",
            active_tab="tab-org",
            className="nav-pills nav-fill",
            children=[

                # =========================
                # ORGANIZATIONS
                # =========================
                dbc.Tab(label="Organizations", tab_id="tab-org", children=[
                    dbc.Card([
                        dbc.CardBody([

                            # HEADER ACTIONS
                            dbc.Row([
                                dbc.Col(html.H5("Organizations", className="fw-semibold"), width=6),
                                dbc.Col(
                                    dbc.Button(
                                        "+ New Organization",
                                        id="btn-open-org-modal",
                                        color="primary",
                                        className="float-end"
                                    ),
                                    width=6
                                )
                            ], className="mb-3"),

                            toast_confirm_delete(),

                            html.Div(id="organizations-table")

                        ])
                    ], className="shadow-sm border-0"),

                    organization_modal()
                ]),

                # =========================
                # DEPARTMENTS
                # =========================
                dbc.Tab(label="Departments", tab_id="tab-dept", children=[
                    dbc.Card([
                        dbc.CardBody([

                            dbc.Row([
                                dbc.Col(html.H5("Departments", className="fw-semibold"), width=6),
                                dbc.Col(
                                    dbc.Button(
                                        "+ New Department",
                                        id="btn-open-dept-modal",
                                        color="success",
                                        className="float-end"
                                    ),
                                    width=6
                                )
                            ], className="mb-3"),

                            toast_confirm_delete_dept(),

                            html.Div(id="departments-table"),

                        ])
                    ], className="shadow-sm border-0"),

                    department_modal()
                ]),

                # =========================
                # LABORATORIES
                # =========================
                dbc.Tab(label="Laboratories", tab_id="tab-lab", children=[
                    dbc.Card([
                        dbc.CardBody([

                            dbc.Row([
                                dbc.Col(html.H5("Laboratories", className="fw-semibold"), width=6),
                                dbc.Col(
                                    dbc.Button(
                                        "+ New Laboratory",
                                        id="btn-open-lab-modal",
                                        color="success",
                                        className="float-end"
                                    ),
                                    width=6
                                )
                            ], className="mb-3"),

                            toast_confirm_delete_lab(),

                            html.Div(id="laboratories-table"),

                        ])
                    ], className="shadow-sm border-0"),

                    laboratory_modal()
                ]),

                # =========================
                # USERS
                # =========================
                dbc.Tab(label="Users", tab_id="tab-user", children=[
                    dbc.Card([
                        dbc.CardBody([

                            dbc.Row([
                                dbc.Col(html.H5("Users", className="fw-semibold"), width=6),
                                dbc.Col(
                                    dbc.Button(
                                        "+ New User",
                                        id="btn-open-user-modal",
                                        color="success",
                                        className="float-end"
                                    ),
                                    width=6
                                )
                            ], className="mb-3"),

                            toast_confirm_delete_user(),

                            html.Div(id="users-table"),

                        ])
                    ], className="shadow-sm border-0"),

                    user_modal(),
                    roles_modal()
                ]),
            ]
        ),

    ], fluid=True)