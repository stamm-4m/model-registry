import base64
import logging
import os

from dash import ALL, Input, Output, State, ctx, html
from dash.exceptions import PreventUpdate

from model_registry.backend.services.model_service import ModelService
from model_registry.backend.utils.model_metadata_extractor import ModelMetadataExtractor
from model_registry.backend.utils.utils_edit_model import (
    feature_item,
    new_feature,
    new_output,
    normalize_date,
    output_item,
    package_row,
)
from model_registry.backend.utils.utils_model_upload import (
    get_path_models_folder,
)

logger = logging.getLogger(__name__)

allowed_extensions = ["pkl", "yaml", "rds", "h5", "joblib", "r", "keras"]

MODEL_TYPE_MAP = {
    "pkl": "pickle",
    "joblib": "sklearn",
    "h5": "keras",
    "keras": "keras",
    "rds": "r_model",
    "r": "r_script"
}

def register_model_upload_callbacks(app):
        
    # Callback to upload the file
    @app.callback(
        Output("output-data-upload", 'children', allow_duplicate=True),
        Output("add-model-info", 'data'),
        Input("upload-data", 'contents'),
        State("upload-data", 'filename'),
        State("add-model-info", "data"),
        prevent_initial_call=True
    )
    def update_output(contents, filename, model_info):
        metadata = {}
        if contents is None or filename is None:
            return html.Div(["No file has been uploaded."]), metadata

        # Validate allowed extensions
        extension = filename.split('.')[-1].lower()
        if extension not in allowed_extensions:
            return html.Div(["File type not allowed. Only allowed types are: " + ", ".join(allowed_extensions)]), metadata

        # Decode the uploaded file
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            # Create the storage folder if it does not exist
            upload_folder = get_path_models_folder(model_info["project_id"])
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            # Save the file in the "Models" folder
            filepath = os.path.join(upload_folder, filename)
            with open(filepath, "wb") as f:
                f.write(decoded)

            extractor = ModelMetadataExtractor(filepath)
            metadata = extractor.extract()
            metadata["project_id"] = model_info["project_id"]
            metadata["artifact_path"] = filepath
            metadata["artifact_format"] = extension
            metadata["artifact_size_bytes"] = len(decoded)

            logger.info(f"Extracted metadata: {metadata}")

            return html.Div([
                html.P(f"File {filename} uploaded successfully."),
            ]), metadata
        except Exception as e:
            return html.Div([
                html.P("Error processing the file."),
                html.P(str(e))
            ]), metadata
        
    # ----- Callback to populate the form -----    
    @app.callback(
        Output("add_model_id", "value"),    
        Output("add_model_name", "value"),
        Output("add_config_model_file", "value"),
        Output("add_creation_date", "value"),
        Output("add_model_version", "value"),
        Output("add_status", "value"),
        Output("add_language", "value"),
        Input("add-model-info", "data"),
        prevent_initial_call=True
    )
    def populate_add_model_form(metadata):
        if not metadata:
            return "", "", "", None, "", "", None

        return (
            metadata.get("model_id"),
            metadata.get("model_id"),
            metadata.get("model_file"),
            normalize_date(metadata.get("created_at")),
            metadata.get("version"),
            metadata.get("status"),
            metadata.get("language_name"),
        )
    # ----- Callback to packages -----
    @app.callback(
            Output("add-packages-container", "children"),
            Input("add-add-package", "n_clicks"),
            Input({"type": "remove-package", "index": ALL}, "n_clicks"),
            State("add-packages-container", "children"),
            prevent_initial_call=True,
        )
    def update_packages(add_clicks, remove_clicks, children):
            triggered = ctx.triggered_id

            if triggered == "add-add-package":
                children.append(package_row(len(children)))
                return children

            if isinstance(triggered, dict) and triggered["type"] == "remove-package":
                index = triggered["index"]
                children = [c for c in children if c.get("props", {}).get("id", {}).get("index") != index]
                return children

            return children
# ----- Callback to features -----
    @app.callback(
        Output("add-features-store", "data", allow_duplicate=True),
        Input("add-add-feature", "n_clicks"),
        State("add-features-store", "data"),
        prevent_initial_call=True,
    )
    def add_feature(_, features):
        features = features or []
        return features + [new_feature()]

    @app.callback(
        Output("add-features-store", "data"),
        Input({"type": "remove-feature", "fid": ALL}, "n_clicks"),
        State("add-features-store", "data"),
        prevent_initial_call=True,
    )
    def remove_feature(n_clicks, features):
        if not n_clicks or all(v is None for v in n_clicks):
            raise PreventUpdate

        triggered = ctx.triggered_id
        if not isinstance(triggered, dict):
            raise PreventUpdate

        fid = triggered["fid"]

        logger.debug(f"Removing feature with fid={fid}")
        return [f for f in features if f["id"] != fid]


    @app.callback(
        Output("add-features-accordion", "children"),
        Input("add-features-store", "data"),
    )
    def render_features(features):
        if not features:
            return []
        return [feature_item(f) for f in features]

    @app.callback(
        Output("add-outputs-accordion", "children"),
        Input("add-outputs-store", "data"),
    )
    def render_outputs(outputs):
        if not outputs:
            return []
        return [output_item(o) for o in outputs]

    @app.callback(
        Output("add-outputs-store", "data", allow_duplicate=True),
        Input("add-add-output", "n_clicks"),
        State("add-outputs-store", "data"),
        prevent_initial_call=True,
    )
    def add_output(_, outputs):
        outputs = outputs or []
        return outputs + [new_output()]

    @app.callback(
        Output("add-outputs-store", "data", allow_duplicate=True),
        Input({"type": "remove-output", "fid": ALL}, "n_clicks"),
        State("add-outputs-store", "data"),
        prevent_initial_call=True,
    )
    def remove_output(n_clicks, outputs):
        if not n_clicks or all(v is None for v in n_clicks):
            raise PreventUpdate

        triggered = ctx.triggered_id
        if not isinstance(triggered, dict):
            raise PreventUpdate

        fid = triggered["fid"]
        
        return [o for o in outputs if o["id"] != fid]

    @app.callback(
        Output("save-model-toast", "is_open"),
        Output("save-model-toast", "children"),
        Output("save-model-toast", "icon"),
        Output("save-model-toast", "header"),
        Output("save-model-feedback", "children"),
        Input("save-ml-model-config", "n_clicks"),

        State("add-model-info", "data"),

        # ===== MODEL IDENTIFICATION =====
        State("add_model_id", "value"), 
        State("add_model_uuid", "value"),
        State("add_model_doi", "value"),
        State("add_name", "value"),
        State("add_model_version", "value"),
        State("add_creation_date", "value"),
        State("add_author", "value"),
        State("add_status", "value"),
        State("add_status_description", "value"),

        # ===== MODEL DESCRIPTION =====
        State("add_learner", "value"),
        State("add_model_type", "value"),
        State("add_model_name", "value"),
        State("add_description", "value"),
        State("add_language", "value"),
        State("add_language_version", "value"),

        State({"type": "package-name", "index": ALL}, "value"),
        State({"type": "package-version", "index": ALL}, "value"),

        State("add_config_model_file", "value"),
        State("add_config_server", "value"),
        State("add_config_port", "value"),
        State("add_config_rest_api", "value"),

        # ===== TIME INTERVAL =====
        State("add_time_interval", "value"),
        State("add_time_interval_units", "value"),
        State("add_time_interval_description", "value"),

        # ===== TIME AGGREGATION =====
        State("add_time_interval_aggregation", "value"),
        State("add_time_interval_aggregation_description", "value"),

        # ===== HYPERPARAMETERS =====
        State("add_number_of_trees", "value"),
        State("add_max_tree_depth", "value"),
        State("add_min_number_instances_per_leaf", "value"),
        State("add_committees", "value"),
        State("add_instance_based_correction", "value"),
        State("add_number_of_instances", "value"),
        State("add_validation", "value"),
        State("add_experiments_id", "value"),

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
        State("user-session", "data"),
        prevent_initial_call=True
    )
    def save_metadata(
        n_clicks, model_info, model_id,
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
        session_data,
    ):
        if not n_clicks or not model_info:
            raise PreventUpdate

        # =======================
        # PACKAGES
        # =======================
        packages = [
            {"package": n, "version": v}
            for n, v in zip(pkg_names, pkg_versions)
            if n and v
        ]

        # =======================
        # INPUT FEATURES
        # =======================
        inputs = [
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
            for i in range(len(f_names))
            if f_names[i]
        ]

        # =======================
        # OUTPUTS
        # =======================
        outputs = [
            {
                "name": o_names[i],
                "units": o_units[i],
                "forecast_horizon": o_horizons[i],
                "feature_scaling": o_scalings[i],
                "expected_range": {
                    "min": o_mins[i],
                    "max": o_maxs[i],
                },
                "description": o_descs[i],
            }
            for i in range(len(o_names))
            if o_names[i]
        ]

        # Normalize values that must satisfy DB CHECK constraints.
        _info = model_info or {}
        _algorithm = (
            learner or model_type or _info.get("algorithm") or "custom"
        )
        if _algorithm not in ModelMetadataExtractor.ALLOWED_ALGORITHMS:
            _algorithm = "custom"
        _status = status or _info.get("status") or "draft"
        if _status not in ModelMetadataExtractor.ALLOWED_STATUS:
            _status = "draft"

        payload = {
            # ----- core identification -----
            "slug": model_id,
            "name": name or model_name or model_id,
            "description": description,
            "algorithm": _algorithm,
            "status": _status,
            "version": version or "1.0.0",

            # ----- IO contract -----
            "inputs": inputs,
            "outputs": outputs,

            # ----- artifact location (from upload step) -----
            "artifact_path": (model_info or {}).get("artifact_path"),
            "artifact_format": (model_info or {}).get("artifact_format"),
            "artifact_size_bytes": (model_info or {}).get("artifact_size_bytes"),

            # ----- identification mirror columns -----
            "doi": doi,
            "authors": author,
            "learner": learner,
            "model_type": model_type,
            "external_uuid": uuid,
            "creation_date": creation_date,
            "status_description": status_desc,

            # ----- rich descriptive blocks -----
            "language": {
                "name": language,
                "version": language_version,
            },
            "packages": packages,
            "config_files": {
                "model_file": cfg_model_file,
                "server": cfg_server,
                "port": cfg_port,
                "rest_api": cfg_rest,
            },
            "input_time_interval": {
                "time_interval": {"value": ti_value, "unit": ti_units},
                "aggregation": {"method": agg_value, "description": agg_desc},
                "description": ti_desc,
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
        }

        # =======================
        # PERSIST IN POSTGRES
        # =======================
        logger.info(f"model_info : {model_info}")
        result, _ = ModelService().create_model_for_project(
            session_data, model_info["project_id"], payload
        )

        if result is None:
            return (
                True,
                "Error: could not save model to the database.",
                "danger",
                "Error",
                "",
            )

        return (
            True,
            f"Model saved successfully. ID: {result.get('id')}",
            "success",
            "Notification",
            "",
        )

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Input("back-to-list-upload", "n_clicks"),
        prevent_initial_call=True,
    )
    def go_back_to_list_upload(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return "/home"
