import base64
import logging
import os

import dash_bootstrap_components as dbc
import requests
from dash import ALL, Input, Output, State, ctx
from dash.exceptions import PreventUpdate

from model_registry.backend.config.settings import settings
from model_registry.backend.utils.utils_edit_model import (
    feature_item,
    new_feature,
    new_output,
    output_item,
    package_row,
)
from model_registry.backend.utils.utils_model_upload import get_path_models_folder

logger = logging.getLogger(__name__)
allowed_extensions = ["pkl", "yaml", "rds", "h5", "joblib", "r", "keras"]

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
        return "/home"
    
# ---------------- SAVE ----------------#
    @app.callback(
        Output("save-feedback", "children"),
        Input("save-model", "n_clicks"),

        # ===== CONTEXT =====
        State("edit-model-info", "data"),

        # ===== MODEL IDENTIFICATION =====
        State("edit_model_uuid", "value"),
        State("edit_model_doi", "value"),
        State("edit_name", "value"),
        State("edit_model_version", "value"),
        State("edit_creation_date", "value"),
        State("edit_author", "value"),
        State("edit_status", "value"),
        State("edit_status_description", "value"),

        # ===== MODEL DESCRIPTION =====
        State("edit_learner", "value"),
        State("edit_model_type", "value"),
        State("edit_model_name", "value"),
        State("edit_description", "value"),
        State("edit_language", "value"),
        State("edit_language_version", "value"),

        State({"type": "package-name", "index": ALL}, "value"),
        State({"type": "package-version", "index": ALL}, "value"),

        State("edit_config_model_file", "value"),
        State("edit_config_server", "value"),
        State("edit_config_port", "value"),
        State("edit_config_rest_api", "value"),

        # ===== TIME INTERVAL =====
        State("edit_time_interval", "value"),
        State("edit_time_interval_units", "value"),
        State("edit_time_interval_description", "value"),

        # ===== TIME AGGREGATION =====
        State("edit_time_interval_aggregation", "value"),
        State("edit_time_interval_aggregation_description", "value"),

        # ===== HYPERPARAMETERS =====
        State("edit_number_of_trees", "value"),
        State("edit_max_tree_depth", "value"),
        State("edit_min_number_instances_per_leaf", "value"),
        State("edit_committees", "value"),
        State("edit_instance_based_correction", "value"),
        State("edit_number_of_instances", "value"),
        State("edit_validation", "value"),
        State("edit_experiments_id", "value"),

        # ===== INPUTS =====
        State({"type": "feature-name", "fid": ALL}, "value"),
        State({"type": "feature-type", "fid": ALL}, "value"),
        State({"type": "feature-units", "fid": ALL}, "value"),
        State({"type": "feature-lag", "fid": ALL}, "value"),
        State({"type": "feature-scaling", "fid": ALL}, "value"),
        State({"type": "feature-min", "fid": ALL}, "value"),
        State({"type": "feature-max", "fid": ALL}, "value"),
        State({"type": "feature-description", "fid": ALL}, "value"),

        # ===== OUTPUTS =====
        State({"type": "output-name", "fid": ALL}, "value"),
        State({"type": "output-units", "fid": ALL}, "value"),
        State({"type": "output-horizon", "fid": ALL}, "value"),
        State({"type": "output-scaling", "fid": ALL}, "value"),
        State({"type": "output-min", "fid": ALL}, "value"),
        State({"type": "output-max", "fid": ALL}, "value"),
        State({"type": "output-description", "fid": ALL}, "value"),

        prevent_initial_call=True,
    )
    def save_model(
        _,
        info,
        uuid, doi, name, version, creation_date, author, status, status_desc,
        learner, model_type, model_name, description, language, language_version,
        pkg_names, pkg_versions,
        cfg_model_file, cfg_server, cfg_port, cfg_rest,
        ti_value, ti_units, ti_desc,
        agg_value, agg_desc,
        n_trees, max_depth, min_leaf, committees, instance_corr,
        n_instances, validation, experiments_id,
        f_names, f_types, f_units, f_lags, f_scalings, f_mins, f_maxs, f_descs,
        o_names, o_units, o_horizons, o_scalings, o_mins, o_maxs, o_descs,
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
            # Inputs
            # =======================
            inputs = [
                {
                    "name": f_names[i],
                    "type": f_types[i],
                    "units": f_units[i],
                    "lag": f_lags[i],
                    "feature_scaling": f_scalings[i],
                    "expected_range": {"min": f_mins[i], "max": f_maxs[i]},
                    "description": f_descs[i],
                }
                for i in range(len(f_names))
            ]

            # =======================
            # Outputs
            # =======================
            outputs = [
                {
                    "name": o_names[i],
                    "units": o_units[i],
                    "forecast_horizon": o_horizons[i],
                    "feature_scaling": o_scalings[i],
                    "expected_range": {"min": o_mins[i], "max": o_maxs[i]},
                    "description": o_descs[i],
                }
                for i in range(len(o_names))
            ]

            # =======================
            # PAYLOAD FINAL
            # =======================
            payload = {
                "ml_model_configuration": {
                    "model_identification": {
                        "name": name,
                        "version": version,
                        "ID": info["model_id"],
                        "UUID": uuid,
                        "author": author,
                        "doi": doi,
                        "creation_date": creation_date,
                        "project": "../project_info.yaml",
                        "status": status,
                        "status_description": status_desc,
                    },
                    "model_description": {
                        "learner": learner,
                        "model_type": model_type,
                        "model_name": model_name,
                        "description": description,
                        "language": [
                            {"name": language},
                            {"version": language_version},
                        ],
                        "config_files": {
                            "model_file": cfg_model_file,
                            "server": cfg_server,
                            "port": cfg_port,
                            "rest_api": cfg_rest,
                        },
                        "packages": packages,
                        "input_time_interval": {
                            "time_interval": {
                                "value": ti_value,
                                "unit": ti_units,
                            },
                            "aggregation": {
                                "method": agg_value,
                                "description": agg_desc,
                            },
                            "description": ti_desc,
                        },
                    },
                    "training_information": {
                        "number_of_instances": n_instances,
                        "hyperparameters": {
                            "number_of_trees": n_trees,
                            "max_tree_depth": max_depth,
                            "min_number_instances_per_leaf": min_leaf,
                            "committees": committees,
                            "instance_based_correction": instance_corr,
                        },
                        "validation": validation,
                        "experiments_ID": experiments_id,
                    },
                    "inputs": {"features": inputs},
                    "outputs": {"information": outputs},
                }
            }


            # =======================
            # API CALL
            # =======================
            response = requests.put(
                f"{settings.API_BASE_URL}{info['project_id']}/update/{info['model_id']}",
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

    @app.callback(
        Output("edit_config_model_file_status", "children"),
        Input("edit_config_model_file_upload", "filename"),
        Input("edit_config_model_file_upload", "contents"),
        State("edit_config_model_file", "value"),
        State("edit-model-info", "data"),
        prevent_initial_call=True
    )
    def update_model_file(filename, contents, current_value, model_info):

        if not filename:
            raise PreventUpdate
        
        if contents is None or filename is None:
            return dbc.Alert("No file has been uploaded.", color="danger", dismissable=True)

        # Validate allowed extensions
        extension = filename.split('.')[-1].lower()
        if extension not in allowed_extensions:
            return dbc.Alert(
                f"File type not allowed. Only allowed types are: {', '.join(allowed_extensions)}",
                color="danger",
                dismissable=True
            )
        
        original_extension = current_value.split('.')[-1].lower()

        if extension != original_extension:
            return dbc.Alert(
                f"File must be a .{original_extension} file",
                color="danger",
                dismissable=True
            )


        # Decode the uploaded file
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            # Create the storage folder if it does not exist
            upload_folder = get_path_models_folder(model_info["project_id"])
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            # Save the file in the "Models" folder
            filepath = os.path.join(upload_folder, current_value)
            with open(filepath, "wb") as f:
                f.write(decoded)     

            return  dbc.Alert(
                f"File updated successfully",
                color="success",
                dismissable=True
            )
        except Exception as e:
            logger.exception("Error updating model file")
            return dbc.Alert(
                f"Error updating model file: {str(e)}",
                color="danger",
                dismissable=True
            )
