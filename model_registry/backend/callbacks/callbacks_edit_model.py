import logging
import requests
import json
from dash import Input, Output, State, ctx, ALL, MATCH
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from model_registry.backend.config.settings import API_BASE_URL
from model_registry.backend.utils.utils_edit_model import feature_item, new_feature, package_row, output_item, new_output
logger = logging.getLogger(__name__)

def register_edit_model_callbacks(app):

    @app.callback(
        Output("packages-container", "children"),
        Input("add-package", "n_clicks"),
        Input({"type": "remove-package", "index": ALL}, "n_clicks"),
        State("packages-container", "children"),
        prevent_initial_call=True,
    )
    def update_packages(add_clicks, remove_clicks, children):
        triggered = ctx.triggered_id

        if triggered == "add-package":
            children.append(package_row(len(children)))
            return children

        if isinstance(triggered, dict) and triggered["type"] == "remove-package":
            index = triggered["index"]
            children = [c for c in children if c["props"]["id"] != index]
            return children

        return children

    @app.callback(
        Output("features-store", "data", allow_duplicate=True),
        Input("add-feature", "n_clicks"),
        State("features-store", "data"),
        prevent_initial_call=True,
    )
    def add_feature(_, features):
        features = features or []
        features.append(new_feature())
        return features

    @app.callback(
        Output("features-store", "data"),
        Input({"type": "remove-feature", "fid": ALL}, "n_clicks"),
        State("features-store", "data"),
        prevent_initial_call=True,
    )
    def remove_feature(_, features):
        triggered = ctx.triggered_id

        if not triggered or not isinstance(triggered, dict):
            raise PreventUpdate

        fid = triggered["fid"]
        return [f for f in features if f["id"] != fid]


    @app.callback(
        Output("features-accordion", "children"),
        Input("features-store", "data"),
    )
    def render_features(features):
        if not features:
            raise PreventUpdate
        return [feature_item(f) for f in features]

    @app.callback(
        Output("outputs-accordion", "children"),
        Input("outputs-store", "data"),
    )
    def render_outputs(outputs):
        if not outputs:
            return []

        return [output_item(o) for o in outputs]

    @app.callback(
        Output("outputs-store", "data", allow_duplicate=True),
        Input("add-output", "n_clicks"),
        State("outputs-store", "data"),
        prevent_initial_call=True,
    )
    def add_output(_, outputs):
        outputs = outputs or []
        outputs.append(new_output())
        return outputs

    @app.callback(
        Output("outputs-store", "data", allow_duplicate=True),
        Input({"type": "remove-output", "fid": ALL}, "n_clicks"),
        State("outputs-store", "data"),
        prevent_initial_call=True,
    )
    def remove_output(_, outputs):
        triggered = ctx.triggered_id
        if not triggered:
            raise PreventUpdate

        fid = triggered["fid"]
        return [o for o in outputs if o["id"] != fid]

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Input("back-to-list", "n_clicks"),
        State("edit-model-info", "data"),
        prevent_initial_call=True,
    )
    def go_back_to_list(n_clicks, info):
        if not n_clicks:
            raise PreventUpdate

        project_id = info["project_id"]

        # Change to destination accordind to project_id to load model list
        return f"/home"
    
# ---------------- SAVE ----------------#
    @app.callback(
        Output("save-feedback", "children"),
        Input("save-model", "n_clicks"),
        State("edit-model-info", "data"),

        State("edit_model_uuid", "value"),
        State("edit_model_doi", "value"),
        State("edit_name", "value"),
        State("edit_model_version", "value"),
        State("edit_creation_date", "value"),
        State("edit_author", "value"),
        State("edit_status", "value"),
        State("edit_status_description", "value"),
        State("edit_learner", "value"),
        State("edit_model_type", "value"),
        State("edit_model_name", "value"),
        State("edit_description", "value"),
        State("edit_language", "value"),
        State("edit_language_version", "value"),
        State("edit_config_model_file", "value"),
        State("edit_config_server", "value"),
        State("edit_config_port", "value"),
        State("edit_config_rest_api", "value"),
        State("edit_time_interval", "value"),
        State("edit_time_interval_units", "value"),
        State("edit_time_interval_description", "value"),
        State("edit_time_interval_aggregation", "value"),
        State("edit_time_interval_aggregation_description", "value"),

        # ---- PACKAGES ----
        State({"type": "package-name", "index": ALL}, "value"),
        State({"type": "package-version", "index": ALL}, "value"),

        # ---- FEATURES ----
        State({"type": "feature-name", "fid": ALL}, "value"),
        State({"type": "feature-type", "fid": ALL}, "value"),
        State({"type": "feature-units", "fid": ALL}, "value"),
        State({"type": "feature-lag", "fid": ALL}, "value"),
        State({"type": "feature-scaling", "fid": ALL}, "value"),
        State({"type": "feature-min", "fid": ALL}, "value"),
        State({"type": "feature-max", "fid": ALL}, "value"),
        State({"type": "feature-description", "fid": ALL}, "value"),

        prevent_initial_call=True,
    )
    def save_model(
        _,
        info,
        author,
        status,
        description,
        pkg_names,
        pkg_versions,
        f_names,
        f_types,
        f_units,
        f_lags,
        f_scalings,
        f_mins,
        f_maxs,
        f_descs,
    ):
        try:
            # =======================
            # PACKAGES
            # =======================
            packages = [
                {"package": n, "version": v}
                for n, v in zip(pkg_names, pkg_versions)
                if n and v
            ]

            # =======================
            # FEATURES
            # =======================
            features = []
            for i in range(len(f_names)):
                features.append(
                    {
                        "name": f_names[i],
                        "type": f_types[i],
                        "units": f_units[i],
                        "lag": f_lags[i],
                        "feature_scaling": f_scalings[i],
                        "expected_range": {
                            "min": f_mins[i],
                            "max": f_maxs[i],
                        },
                        "description": f_descs[i],
                    }
                )

            # =======================
            # PAYLOAD FINAL
            # =======================
            payload = {
                "metadata": {
                    "author": author,
                    "status": status,
                    "description": description,
                    "packages": packages,
                },
                "inputs": {
                    "features": features
                },
            }

            logger.debug("SAVE PAYLOAD:")
            logger.debug(json.dumps(payload, indent=2))

            # =======================
            # API CALL
            # =======================
            response = requests.put(
                f"{API_BASE_URL}{info['project_id']}/update_model/{info['model_name']}",
                json=payload,
                timeout=10,
            )

            if response.status_code != 200:
                return dbc.Alert(
                    f"❌ Error saving model: {response.text}",
                    color="danger",
                    dismissable=True,
                )

            return dbc.Alert(
                "✅ Model saved successfully",
                color="success",
                dismissable=True,
            )

        except Exception as e:
            logger.exception("Save model failed")
            return dbc.Alert(
                f"❌ Unexpected error: {str(e)}",
                color="danger",
                dismissable=True,
            )
