from dash import Output, Input, html
import dash_bootstrap_components as dbc


from model_registry.backend.services.project_service import ProjectService
from model_registry.backend.utils.utils_projects import build_table_projects
from model_registry.backend.utils.utils_experiments import build_table_experiments
from model_registry.backend.services.experiment_service import ExperimentService
import logging
logger = logging.getLogger(__name__)


def register_project_table_callbacks(app):

    # Callback load projects 
    @app.callback(
        Output("projects-table", "children"),
        Input("proj-refresh-trigger", "data")
    )
    def load_projects(refresh_data):
        service = ProjectService()
        projects = service.get_all_projects()

        if not projects:
            return html.Div("No projects found.")

        return build_table_projects(projects)
    # Callback load experiments
    @app.callback(
        Output("experiments-table", "children"),
        Input("exp-refresh-trigger", "data")
    )
    def load_experiments(refresh_data):

        service = ExperimentService()
        experiments = service.get_all_experiments()

        if not experiments:
            return html.Div("No experiments found.")

        return build_table_experiments(experiments)
    