from dash import Output, Input, State, ALL
import dash
from dash.exceptions import PreventUpdate
import json

from model_registry.backend.services.project_service import ProjectService
from model_registry.backend.services.experiment_service import ExperimentService
import logging
logger = logging.getLogger(__name__)



def register_experiment_modal_callbacks(app):

    @app.callback(
        Output("experiment-modal", "is_open"),
        Input("btn-open-exp-modal", "n_clicks"),
        Input("btn-close-exp-modal", "n_clicks"),
        Input("btn-save-exp", "n_clicks"),
        State("experiment-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_experiment_modal(open_click, close_click, save_click, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        trigger = ctx.triggered_id
        if trigger == "btn-open-exp-modal":
            return True
        elif trigger in ["btn-close-exp-modal", "btn-save-exp"]:
            return False
        return is_open

    @app.callback(
        Output("exp-project-dropdown", "options"),
        Output("user-session", "data", allow_duplicate=True),
        Input("btn-open-exp-modal", "n_clicks"),
        Input({"type": "btn-edit-exp", "index": ALL}, "n_clicks"),
        State("user-session", "data"),
        prevent_initial_call=True
    )
    def load_projects_dropdown(n, n_list, session_data):
        service = ProjectService()
        projects, session_data = service.get_all_projects(session_data)
        logger.debug(f"Loaded projects for dropdown: {projects}")
        return [
            {"label": proj.name, "value": str(proj.id)}
            for proj in projects
        ], session_data

    @app.callback(
        Output("exp-name-input", "value"),
        Output("exp-project-dropdown", "value"),
        Output("exp-description-input", "value"),
        Output("exp-initial-conditions-input", "value"),
        Output("exp-set-points-input", "value"),
        Output("exp-start-time-input", "value"),
        Output("exp-end-time-input", "value"),
        Output("exp-edit-id", "data", allow_duplicate=True),
        Output("exp-refresh-trigger", "data", allow_duplicate=True),
        Output("exp-toast", "is_open", allow_duplicate=True),
        Output("exp-toast", "children", allow_duplicate=True),
        Output("exp-toast", "icon", allow_duplicate=True),
        Output("user-session", "data", allow_duplicate=True),
        Input("btn-save-exp", "n_clicks"),
        State("exp-name-input", "value"),
        State("exp-project-dropdown", "value"),
        State("exp-description-input", "value"),
        State("exp-initial-conditions-input", "value"),
        State("exp-set-points-input", "value"),
        State("exp-start-time-input", "value"),
        State("exp-end-time-input", "value"),
        State("exp-edit-id", "data"),
        State("user-session", "data"),
        prevent_initial_call=True
    )
    def save_experiment(n, name, project_id, description, initial_conditions, set_points, start_time, end_time, exp_id, session_data):
        if not n:
            raise PreventUpdate
        if not name or not project_id:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, True, "Name and project required", "danger", session_data
        service = ExperimentService()
        ic = None
        sp = None
        try:
            ic = json.loads(initial_conditions) if initial_conditions else None
        except Exception:
            ic = None
        try:
            sp = json.loads(set_points) if set_points else None
        except Exception:
            sp = None
        st = start_time if start_time else None
        et = end_time if end_time else None
        try:
            if exp_id:
                logger.debug(f"Editing experiment with ID: {exp_id}")
                _, session_data = service.update_experiment(
                    session_data,
                    exp_id,
                    name=name,
                    project_id=project_id,
                    description=description,
                    initial_conditions=ic,
                    set_points=sp,
                    start_time=st,
                    end_time=et
                )
                msg = "Experiment updated successfully"
                icon = "success"
            else:
                logger.debug("Creating new experiment")
                _, session_data = service.add_experiment(
                    session_data,
                    name=name,
                    project_id=project_id,
                    description=description,
                    initial_conditions=ic,
                    set_points=sp,
                    start_time=st,
                    end_time=et
                )
                msg = "Experiment created successfully"
                icon = "success"
            logger.debug(f"Saved experiment: {name}, project_id: {project_id}")
            return "", None, "", "", "", "", "", None, n, True, msg, icon, session_data
        except Exception as e:
            logger.error(f"Error saving experiment: {e}")
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, True, f"Error: {e}", "danger", session_data

    @app.callback(
        Output("experiment-modal", "is_open", allow_duplicate=True),
        Output("exp-name-input", "value", allow_duplicate=True),
        Output("exp-project-dropdown", "value", allow_duplicate=True),
        Output("exp-description-input", "value", allow_duplicate=True),
        Output("exp-initial-conditions-input", "value", allow_duplicate=True),
        Output("exp-set-points-input", "value", allow_duplicate=True),
        Output("exp-start-time-input", "value", allow_duplicate=True),
        Output("exp-end-time-input", "value", allow_duplicate=True),
        Output("exp-edit-id", "data"),
        Output("user-session", "data", allow_duplicate=True),
        Input({"type": "btn-edit-exp", "index": ALL}, "n_clicks"),
        State("user-session", "data"),
        prevent_initial_call=True
    )
    def open_edit_experiment(n_clicks_list, session_data):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        if not any(n and n > 0 for n in n_clicks_list):
            raise PreventUpdate
        exp_id = ctx.triggered_id["index"]
        service = ExperimentService()
        exp, session_data = service.get_experiment_by_id(session_data, exp_id)
        if exp is None:
            raise PreventUpdate
        import json
        ic = json.dumps(exp.initial_conditions) if exp.initial_conditions else ""
        sp = json.dumps(exp.set_points) if exp.set_points else ""
        st = str(exp.start_time) if exp.start_time else ""
        et = str(exp.end_time) if exp.end_time else ""
        logger.debug(f"Editing experiment with ID: {exp_id}, name: {exp.name}, project_id: {exp.project_id}")
        return True, exp.name, str(exp.project_id) if exp.project_id else None, exp.description or "", ic, sp, st, et, str(exp_id), session_data