import json
import logging
from datetime import UTC, datetime

import dash
from dash import ALL, Input, Output, State
from dash.exceptions import PreventUpdate

from model_registry.backend.services.airflow_client import (
    trigger_deployment_soft_sensors,
)
from model_registry.backend.services.api_clients import RunsApiClient, EquipmentsApiClient
from model_registry.backend.services.experiment_service import ExperimentService
from model_registry.backend.services.project_service import ProjectService
from model_registry.backend.services.model_service import ModelService
from model_registry.backend.services.api_clients import ModelsApiClient

logger = logging.getLogger(__name__)


def _resolve_model_slugs(session_data, model_ids: list | None):
    """models.slug for every model attached to the experiment — the
    identifiers Airflow needs to call /predict/{model_id} for each one.
    """
    if not model_ids:
        return [], session_data
    models_client = ModelsApiClient()
    slugs = []
    for mid in model_ids:
        model, session_data = models_client.get_model_row(mid, session_data)
        if model and model.get("slug"):
            slugs.append(model["slug"])
    return slugs, session_data


def _start_prediction_loop(
    session_data, experiment_id: str, project_id: str, model_ids: list | None = None, vessel_id: str | None = None
):
    """Create the experiment's first run and trigger the Airflow prediction
    loop for it. Best-effort: logs and returns on any failure so a hiccup
    here never blocks experiment creation from succeeding in the UI.
    """
    run_payload = {
        "experiment_id": experiment_id,
        "start_time": datetime.now(UTC).isoformat(),
    }
    run, session_data = RunsApiClient().create(run_payload, session_data)
    if run is None:
        logger.error(f"Could not create initial run for experiment {experiment_id} — Airflow not triggered.")
        return session_data

    project, session_data = ProjectService().get_project(session_data, project_id)
    project_name = project.name if project else ""

    model_slugs, session_data = _resolve_model_slugs(session_data, model_ids)
    if not model_slugs:
        logger.warning(f"No model attached to experiment {experiment_id} — Airflow will fall back to its own env-var pin.")

    triggered = trigger_deployment_soft_sensors(
        run_id=run["id"],
        experiment_id=experiment_id,
        project_id=project_id,
        project_name=project_name,
        model_ids=model_slugs,
        vessel_id=vessel_id,
    )
    if not triggered:
        logger.warning(f"Airflow trigger failed for experiment {experiment_id}, run {run['id']}.")
    return session_data


def register_experiment_modal_callbacks(app):
    @app.callback(
        Output("experiment-modal", "is_open"),
        Input("btn-open-exp-modal", "n_clicks"),
        Input("btn-close-exp-modal", "n_clicks"),
        Input("btn-save-exp", "n_clicks"),
        State("experiment-modal", "is_open"),
        prevent_initial_call=True,
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
        prevent_initial_call=True,
    )
    def load_projects_dropdown(n, n_list, session_data):
        service = ProjectService()
        projects, session_data = service.get_all_projects(session_data)
        logger.debug(f"Loaded projects for dropdown: {projects}")
        return [
            {"label": proj.name, "value": str(proj.id)} for proj in projects
        ], session_data

    @app.callback(
        Output("exp-vessel-dropdown", "options"),
        Output("user-session", "data", allow_duplicate=True),
        Input("btn-open-exp-modal", "n_clicks"),
        Input({"type": "btn-edit-exp", "index": ALL}, "n_clicks"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def load_vessels_dropdown(n, n_list, session_data):
        equipments, session_data = EquipmentsApiClient().list(session_data)
        return [
            {"label": eq.get("name"), "value": str(eq.get("id"))} for eq in (equipments or [])
        ], session_data

    @app.callback(
        Output("exp-models-dropdown", "options"),
        Output("user-session", "data", allow_duplicate=True),
        Input("exp-project-dropdown", "value"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def load_models_for_project(project_uuid, session_data):
        if not project_uuid:
            raise PreventUpdate
        # Resolve external project code
        psvc = ProjectService()
        proj, session_data = psvc.get_project(session_data, project_uuid)
        if not proj or not proj.project_id:
            return [], session_data
        msvc = ModelService()
        models, session_data = msvc.list_db_models_for_project(session_data, proj.project_id)
        options = []
        if models:
            for m in models:
                db_uuid = m.get("metadata", {}).get("db_uuid")
                label = m.get("model_name") or db_uuid
                # get description and name if available
                target_name = m.get("metadata", {}).get("target_name")
                target_description = m.get("metadata", {}).get("target_description")

                if target_name:
                    label += f" - {target_name}"
                if target_description:
                    label += f" - {target_description}"
                options.append({"label": label, "value": str(db_uuid)})
        return options, session_data

    @app.callback(
        Output("exp-name-input", "value"),
        Output("exp-project-dropdown", "value"),
        Output("exp-models-dropdown", "value"),
        Output("exp-vessel-dropdown", "value"),
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
        State("exp-models-dropdown", "value"),
        State("exp-vessel-dropdown", "value"),
        State("exp-description-input", "value"),
        State("exp-initial-conditions-input", "value"),
        State("exp-set-points-input", "value"),
        State("exp-start-time-input", "value"),
        State("exp-end-time-input", "value"),
        State("exp-edit-id", "data"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def save_experiment(
        n,
        name,
        project_id,
        model_ids,
        vessel_id,
        description,
        initial_conditions,
        set_points,
        start_time,
        end_time,
        exp_id,
        session_data,
    ):
        if not n:
            raise PreventUpdate
        if not name or not project_id:
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                True,
                "Name and project required",
                "danger",
                session_data,
            )
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
                    model_ids=model_ids,
                    name=name,
                    project_id=project_id,
                    vessel_id=vessel_id,
                    description=description,
                    initial_conditions=ic,
                    set_points=sp,
                    start_time=st,
                    end_time=et,
                )
                msg = "Experiment updated successfully"
                icon = "success"
            else:
                logger.debug("Creating new experiment")
                new_exp, session_data = service.add_experiment(
                    session_data,
                    name=name,
                    project_id=project_id,
                    model_ids=model_ids,
                    vessel_id=vessel_id,
                    description=description,
                    initial_conditions=ic,
                    set_points=sp,
                    start_time=st,
                    end_time=et,
                )
                msg = "Experiment created successfully"
                icon = "success"
                if new_exp is not None:
                    session_data = _start_prediction_loop(
                        session_data, new_exp.id, project_id, model_ids, vessel_id
                    )
            logger.debug(f"Saved experiment: {name}, project_id: {project_id}")
            return "", None, [], None, "", "", "", "", "", None, n, True, msg, icon, session_data
        except Exception as e:
            logger.error(f"Error saving experiment: {e}")
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                True,
                f"Error: {e}",
                "danger",
                session_data,
            )

    @app.callback(
        Output("experiment-modal", "is_open", allow_duplicate=True),
        Output("exp-name-input", "value", allow_duplicate=True),
        Output("exp-project-dropdown", "value", allow_duplicate=True),
        Output("exp-models-dropdown", "value", allow_duplicate=True),
        Output("exp-vessel-dropdown", "value", allow_duplicate=True),
        Output("exp-description-input", "value", allow_duplicate=True),
        Output("exp-initial-conditions-input", "value", allow_duplicate=True),
        Output("exp-set-points-input", "value", allow_duplicate=True),
        Output("exp-start-time-input", "value", allow_duplicate=True),
        Output("exp-end-time-input", "value", allow_duplicate=True),
        Output("exp-edit-id", "data"),
        Output("user-session", "data", allow_duplicate=True),
        Input({"type": "btn-edit-exp", "index": ALL}, "n_clicks"),
        State("user-session", "data"),
        prevent_initial_call=True,
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
        logger.debug(
            f"Editing experiment with ID: {exp_id}, name: {exp.name}, project_id: {exp.project_id}"
        )
        # load linked model ids
        models_client = ModelsApiClient()
        links, session_data = models_client.list_experiment_models(session_data)
        logger.debug(f"Loaded experiment_models links: {links}")
        linked = []
        if links:
            linked = [str(l.get("model_id")) for l in links if str(l.get("experiment_id")) == str(exp_id) and l.get("model_id")]
        return (
            True,
            exp.name,
            str(exp.project_id) if exp.project_id else None,
            linked,
            str(exp.vessel_id) if exp.vessel_id else None,
            exp.description or "",
            ic,
            sp,
            st,
            et,
            str(exp_id),
            session_data,
        )
