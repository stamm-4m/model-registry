from dash import dcc, html
import dash_bootstrap_components as dbc

from model_registry.backend.pages.add_experiments import experiment_modal
from model_registry.backend.pages.modal_project import project_modal
from model_registry.backend.utils.utils_experiments import toast_confirm_delete_exp
from model_registry.backend.utils.utils_projects import toast_confirm_delete_proj


def projects_layout():
    return dbc.Container([

        # 🔹 STORES
        dcc.Store(id="proj-edit-id"),
        dcc.Store(id="proj-delete-id"),
        dcc.Store(id="proj-refresh-trigger"),
        dcc.Store(id="exp-edit-id"),
        dcc.Store(id="exp-delete-id"),
        dcc.Store(id="exp-refresh-trigger"),

        # 🔝 HEADER
        dbc.Row([
            dbc.Col([
                html.H2("Projects & Experiments", className="fw-bold mb-1"),
                html.P(
                    "Manage projects and experiments across your organization",
                    className="text-muted"
                )
            ])
        ], className="mb-4 mt-3"),

        # 🔹 TABS
        dbc.Tabs(

            [
                # =========================
                # 📁 PROJECTS TAB
                # =========================
                dbc.Tab(
                    label="Projects",
                    tab_id="tab-proj",
                    children=[

                        dbc.Card([
                            dbc.CardBody([

                                # 🔹 ACTION BAR
                                dbc.Row([
                                    dbc.Col([
                                        html.H5("Projects", className="mb-0")
                                    ], width=6),

                                    dbc.Col([
                                        dbc.Button(
                                            "+ New Project",
                                            id="btn-open-proj-modal",
                                            color="primary"
                                        )
                                    ], width=6, className="text-end")
                                ], className="mb-3"),

                                toast_confirm_delete_proj(),

                                # 🔹 TABLE
                                html.Div(id="projects-table")

                            ])
                        ], className="shadow-sm border-0"),

                        # MODAL
                        project_modal()

                    ]
                ),

                # =========================
                # 🧪 EXPERIMENTS TAB
                # =========================
                dbc.Tab(
                    label="Experiments",
                    tab_id="tab-exp",
                    children=[

                        dbc.Card([
                            dbc.CardBody([

                                # 🔹 ACTION BAR
                                dbc.Row([
                                    dbc.Col([
                                        html.H5("Experiments", className="mb-0")
                                    ], width=6),

                                    dbc.Col([
                                        dbc.Button(
                                            "+ New Experiment",
                                            id="btn-open-exp-modal",
                                            color="success"
                                        )
                                    ], width=6, className="text-end")
                                ], className="mb-3"),

                                toast_confirm_delete_exp(),

                                # 🔹 TABLE
                                html.Div(id="experiments-table")

                            ])
                        ], className="shadow-sm border-0"),

                        # MODAL
                        experiment_modal()

                    ]
                ),

            ],

            id="tabs-projects",
            active_tab="tab-proj",
            className="nav-pills nav-fill",
        )

    ], fluid=True)