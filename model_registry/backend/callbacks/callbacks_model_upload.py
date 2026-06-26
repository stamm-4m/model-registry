import base64
import hashlib
import logging
import os
import re

import dash_bootstrap_components as dbc
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

# ---------------------------------------------------------------------------
# Magic-byte validation
# ---------------------------------------------------------------------------

# Known non-model file signatures → always reject regardless of extension.
_FORBIDDEN_SIGNATURES = [
    (b"%PDF", "PDF document"),
    (b"PK\x03\x04", "ZIP / Office Open XML (xlsx, docx, …)"),
    (b"\xd0\xcf\x11\xe0", "OLE2 compound file (xls, doc, …)"),
    (b"\xff\xd8\xff", "JPEG image"),
    (b"\x89PNG", "PNG image"),
    (b"GIF8", "GIF image"),
    (b"BM", "BMP image"),
    (b"<html", "HTML file"),
    (b"<!DOC", "HTML/XML file"),
]

# Expected leading bytes per extension (at least one must match).
# None means "no positive check — extension alone is sufficient."
_EXPECTED_SIGNATURES: dict = {
    "pkl": [b"\x80\x02", b"\x80\x03", b"\x80\x04", b"\x80\x05"],
    "joblib": [b"\x80\x02", b"\x80\x03", b"\x80\x04", b"\x80\x05"],
    "h5": [b"\x89HDF"],
    "keras": [b"\x89HDF", b"PK\x03\x04"],  # keras v2 = HDF5; keras v3 = zip
    "rds": [b"X\n", b"\x1f\x8b"],  # binary RDS or gzip-compressed
    "r": None,  # plain text R script — skip
    "yaml": None,  # plain text — skip
}


def _validate_model_bytes(decoded: bytes, extension: str) -> str | None:
    """Return an error message if the bytes look wrong, else None."""
    header = decoded[:8]

    # 1. Reject known non-model formats unconditionally.
    for sig, label in _FORBIDDEN_SIGNATURES:
        if header.startswith(sig):
            return f"File looks like a {label}, not a model artifact."

    # 2. Positive check: does the header match what we expect for this ext?
    expected = _EXPECTED_SIGNATURES.get(extension)
    if expected is not None:
        if not any(header.startswith(s) for s in expected):
            return (
                f"File header does not match the expected format for .{extension}. "
                "Make sure you are uploading the correct model file."
            )

    return None


MODEL_TYPE_MAP = {
    "pkl": "pickle",
    "joblib": "sklearn",
    "h5": "keras",
    "keras": "keras",
    "rds": "r_model",
    "r": "r_script",
}

# ---------------------------------------------------------------------------
# Scaler Library helpers
# ---------------------------------------------------------------------------


def _scaler_options(scalers):
    """Convert scalers-store list to Dash dropdown option dicts."""
    return [{"label": s["label"], "value": s["id"]} for s in (scalers or [])]


def _render_scaler_list(scalers):
    """Render the scalers-list-container contents."""
    if not scalers:
        return html.P("No scalers uploaded yet.", className="text-muted small")
    rows = []
    for s in scalers:
        rows.append(
            dbc.ListGroupItem(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Span(s["label"], className="fw-semibold"), width=8
                        ),
                        dbc.Col(
                            html.Small(s["filename"], className="text-muted"), width=3
                        ),
                        dbc.Col(
                            dbc.Button(
                                "×",
                                id={"type": "remove-scaler", "id": s["id"]},
                                color="link",
                                size="sm",
                                className="text-danger p-0",
                            ),
                            width=1,
                            className="text-end",
                        ),
                    ],
                    align="center",
                ),
                className="px-2 py-1",
            )
        )
    return dbc.ListGroup(rows, flush=True)


def register_model_upload_callbacks(app):
    # Callback to upload the file
    @app.callback(
        Output("output-data-upload", "children", allow_duplicate=True),
        Output("add-model-info", "data"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("add-model-info", "data"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def update_output(contents, filename, model_info, session_data):
        # Preserve any existing context (most importantly project_id) so a
        # transient failure does not wipe it out and break the next attempt.
        model_info = dict(model_info or {})

        if contents is None or filename is None:
            return html.Div(["No file has been uploaded."]), model_info

        # Validate allowed extensions
        extension = filename.split(".")[-1].lower()
        if extension not in allowed_extensions:
            return html.Div(
                [
                    "File type not allowed. Only allowed types are: "
                    + ", ".join(allowed_extensions)
                ]
            ), model_info
        logger.info(f"model info: {model_info}")
        project_id = model_info.get("project_id")
        if not project_id:
            logger.error(
                "Model upload aborted: project_id missing from add-model-info store"
            )
            return html.Div(
                [
                    html.P("Error processing the file."),
                    html.P(
                        "No project selected. Please open the upload page from a project."
                    ),
                ]
            ), model_info

        # Decode the uploaded file
        try:
            _content_type, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)
        except (ValueError, base64.binascii.Error) as e:
            logger.exception("Failed to decode uploaded file %s", filename)
            return html.Div(
                [
                    html.P("Error processing the file."),
                    html.P(str(e)),
                ]
            ), model_info

        # Magic-byte validation — reject disguised files before touching disk.
        validation_error = _validate_model_bytes(decoded, extension)
        if validation_error:
            return html.Div(
                [
                    dbc.Alert(
                        [
                            html.I(className="bi bi-shield-exclamation me-2"),
                            html.Strong("Invalid file: "),
                            html.Span(validation_error),
                        ],
                        color="danger",
                        className="py-2 px-3 mt-2",
                    ),
                ]
            ), model_info

        try:
            # Create the storage folder if it does not exist
            upload_folder = get_path_models_folder(project_id, session_data)
            if not upload_folder:
                raise ValueError(
                    f"Could not resolve models folder for project '{project_id}'"
                )
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            # Save the file in the "Models" folder
            filepath = os.path.join(upload_folder, filename)
            with open(filepath, "wb") as f:
                f.write(decoded)

            extractor = ModelMetadataExtractor(filepath)
            metadata = extractor.extract() or {}
            metadata["project_id"] = project_id
            metadata["artifact_path"] = filepath
            metadata["artifact_format"] = extension
            metadata["artifact_size_bytes"] = len(decoded)

            logger.info(f"Extracted metadata: {metadata}")

            size_kb = round(len(decoded) / 1024, 1)
            return html.Div(
                [
                    dbc.Alert(
                        [
                            html.I(
                                className="bi bi-check-circle-fill me-2 text-success"
                            ),
                            html.Strong(filename),
                            html.Span(
                                f"  ·  {size_kb} KB  ·  .{extension}",
                                className="text-muted ms-1",
                            ),
                        ],
                        color="success",
                        className="py-2 px-3 mt-2",
                    ),
                ]
            ), metadata
        except Exception as e:
            logger.exception("Error processing uploaded model file %s", filename)
            return html.Div(
                [
                    dbc.Alert(
                        [
                            html.I(className="bi bi-x-circle-fill me-2"),
                            html.Strong("Upload failed: "),
                            html.Span(str(e)),
                        ],
                        color="danger",
                        className="py-2 px-3 mt-2",
                    ),
                ]
            ), model_info

    # ----- Callback to populate the form -----
    @app.callback(
        Output("add_model_id", "value"),
        Output("add_model_name", "value"),
        Output("add_config_model_file", "value"),
        Output("add_creation_date", "value"),
        Output("add_model_version", "value"),
        Output("add_status", "value"),
        Output("add_is_active", "value"),
        Output("add_language", "value"),
        Input("add-model-info", "data"),
        prevent_initial_call=True,
    )
    def populate_add_model_form(metadata):
        if not metadata:
            return "", "", "", None, "", "", True, None
        # In edit/details mode the layout pre-populates values directly;
        # this callback must not overwrite them.
        if metadata.get("mode") in ("edit", "details"):
            raise PreventUpdate

        return (
            metadata.get("model_id"),
            metadata.get("model_id"),
            metadata.get("model_file"),
            normalize_date(metadata.get("created_at")),
            metadata.get("version"),
            metadata.get("status"),
            bool(metadata.get("is_active", True)),
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
            children = [
                c
                for c in children
                if c.get("props", {}).get("id", {}).get("index") != index
            ]
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
        State("scalers-store", "data"),
    )
    def render_features(features, scalers):
        if not features:
            return []
        opts = _scaler_options(scalers)
        return [feature_item(f, opts) for f in features]

    @app.callback(
        Output("add-outputs-accordion", "children"),
        Input("add-outputs-store", "data"),
        State("scalers-store", "data"),
    )
    def render_outputs(outputs, scalers):
        if not outputs:
            return []
        opts = _scaler_options(scalers)
        return [output_item(o, opts) for o in outputs]

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
        Output("user-session", "data", allow_duplicate=True),
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
        State("add_is_active", "value"),
        State("add_status_description", "value"),
        # ===== MODEL DESCRIPTION =====
        State("add_learner", "value"),
        State("template-algorithm-selector", "value"),  # Learner Family → algorithm
        State("add_ml_task", "value"),
        State("add_model_category", "value"),
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
        # ===== TRAINING INFO =====
        State("add_number_of_instances", "value"),
        State("add_validation", "value"),
        State("add_experiments_id", "value"),
        # ===== GOVERNANCE =====
        State("add_governance_validation_status", "value"),
        # ===== INPUTS =====
        State({"type": "feature-name", "fid": ALL}, "value"),
        State({"type": "feature-type", "fid": ALL}, "value"),
        State({"type": "feature-units", "fid": ALL}, "value"),
        State({"type": "feature-lag", "fid": ALL}, "value"),
        State({"type": "feature-scaling", "fid": ALL}, "value"),
        State({"type": "feature-min", "fid": ALL}, "value"),
        State({"type": "feature-max", "fid": ALL}, "value"),
        State({"type": "feature-description", "fid": ALL}, "value"),
        State({"type": "feature-name", "fid": ALL}, "id"),
        # ===== OUTPUTS =====
        State({"type": "output-name", "fid": ALL}, "value"),
        State({"type": "output-units", "fid": ALL}, "value"),
        State({"type": "output-horizon", "fid": ALL}, "value"),
        State({"type": "output-scaling", "fid": ALL}, "value"),
        State({"type": "output-min", "fid": ALL}, "value"),
        State({"type": "output-max", "fid": ALL}, "value"),
        State({"type": "output-description", "fid": ALL}, "value"),
        State({"type": "output-name", "fid": ALL}, "id"),
        # ===== TEMPLATE CONFIG =====
        State("template-config-store", "data"),
        # ===== STORES (carry scaler assignments) =====
        State("add-features-store", "data"),
        State("add-outputs-store", "data"),
        State("scalers-store", "data"),
        State("user-session", "data"),
        prevent_initial_call=True,
    )
    def save_metadata(
        n_clicks,
        model_info,
        model_id,
        uuid,
        doi,
        name,
        version,
        creation_date,
        author,
        status,
        is_active,
        status_desc,
        learner,
        algorithm_family,
        ml_task,
        model_category,
        model_type,
        model_name,
        description,
        language,
        language_version,
        pkg_names,
        pkg_versions,
        cfg_model_file,
        cfg_server,
        cfg_port,
        cfg_rest,
        ti_value,
        ti_units,
        ti_desc,
        agg_value,
        agg_desc,
        n_instances,
        validation,
        experiments_id,
        governance_validation_status,
        f_names,
        f_types,
        f_units,
        f_lags,
        f_scalings,
        f_mins,
        f_maxs,
        f_descs,
        f_ids,
        o_names,
        o_units,
        o_horizons,
        o_scalings,
        o_mins,
        o_maxs,
        o_descs,
        o_ids,
        template_config,
        features_store,
        outputs_store,
        scalers_store,
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
        # Build a lookup: fid → store entry (carries scaler_id, scaler_path, etc.)
        _fstore = {f["id"]: f for f in (features_store or []) if isinstance(f, dict)}
        _scalers_map = {s["id"]: s for s in (scalers_store or [])}

        # Build straight from the DOM field values — the source of truth for
        # what the user actually typed. The matching `feature-name` id array
        # gives each row's fid in the SAME order as the value arrays, so we
        # can still look up scaler info from the store by fid. We do NOT
        # filter on the store's `name`: newly added rows have an empty name
        # in the store (it only lives in the DOM until save), so that filter
        # silently dropped every new feature. (bug fix 2026-06-12)
        inputs = []
        for i, _fid_obj in enumerate(f_ids or []):
            if i >= len(f_names) or not (f_names[i] or "").strip():
                continue
            fid = _fid_obj.get("fid") if isinstance(_fid_obj, dict) else None
            _fs = _fstore.get(fid, {})
            scaler_id = _fs.get("scaler_id") or None
            scaler_info = _scalers_map.get(scaler_id, {}) if scaler_id else {}
            inputs.append(
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
                    "scaler_id": scaler_id,
                    "scaler_filename": scaler_info.get("filename")
                    or _fs.get("scaler_filename")
                    or "",
                    "scaler_path": scaler_info.get("path")
                    or _fs.get("scaler_path")
                    or "",
                    "has_scaler": scaler_id is not None,
                }
            )

        # =======================
        # OUTPUTS
        # =======================
        _ostore = {o["id"]: o for o in (outputs_store or []) if isinstance(o, dict)}
        outputs = []
        for i, _oid_obj in enumerate(o_ids or []):
            if i >= len(o_names) or not (o_names[i] or "").strip():
                continue
            oid = _oid_obj.get("fid") if isinstance(_oid_obj, dict) else None
            _os = _ostore.get(oid, {})
            scaler_id = _os.get("scaler_id") or None
            scaler_info = _scalers_map.get(scaler_id, {}) if scaler_id else {}
            outputs.append(
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
                    "scaler_id": scaler_id,
                    "scaler_filename": scaler_info.get("filename")
                    or _os.get("scaler_filename")
                    or "",
                    "scaler_path": scaler_info.get("path")
                    or _os.get("scaler_path")
                    or "",
                    "has_scaler": scaler_id is not None,
                }
            )

        # =======================
        # NORMALISE & DERIVE
        # =======================
        _info = model_info or {}

        # Algorithm: prefer Learner Family dropdown, fall back to extractor result
        _algorithm = algorithm_family or _info.get("algorithm") or "custom"
        if (
            template_config
            and isinstance(template_config, dict)
            and template_config.get("algorithm")
        ):
            _algorithm = template_config["algorithm"]
        if _algorithm not in ModelMetadataExtractor.ALLOWED_ALGORITHMS:
            _algorithm = "custom"

        _status = status or _info.get("status") or "draft"
        if _status not in ModelMetadataExtractor.ALLOWED_STATUS:
            _status = "draft"

        # Slug: must match ^[a-z0-9][a-z0-9_-]*$ — sanitise the raw model_id
        raw_slug = model_id or name or model_name or "model"
        _slug = re.sub(r"[^a-z0-9_-]", "_", raw_slug.lower()).strip("_") or "model"

        # Artifact block — path/format/size come from the upload step;
        # sha256 is computed on-disk from the saved file.
        _artifact_path = _info.get("artifact_path")
        _artifact_format = _info.get("artifact_format", "custom")
        _artifact_size = _info.get("artifact_size_bytes")
        _sha256 = ""
        if _artifact_path and os.path.exists(_artifact_path):
            try:
                h = hashlib.sha256()
                with open(_artifact_path, "rb") as fh:
                    for chunk in iter(lambda: fh.read(65536), b""):
                        h.update(chunk)
                _sha256 = h.hexdigest()

            except Exception:
                pass  # sha256 stays ""

        # =======================
        # PAYLOAD
        # =======================
        _experiments = [
            e.strip() for e in (experiments_id or "").split(",") if e.strip()
        ]

        payload = {
            "slug": _slug,
            "name": name or model_name or _slug,
            "description": description or "",
            "algorithm": _algorithm,
            "status": _status,
            "version": version or "1.0.0",
            "authors": author or "",
            "doi": doi or "",
            "learner": learner or "",
            "model_type": model_type or "",
            "external_uuid": uuid or "",
            "creation_date": creation_date or "",
            "status_description": status_desc or "",
            "is_active": is_active if is_active is not None else True,
            "language": [{"name": language or ""}, {"version": language_version or ""}],
            "packages": packages,
            "inputs": inputs,
            "outputs": outputs,
            "config": template_config or {},
            "metrics": {},
            "config_files": {
                "model_file": cfg_model_file or "",
                "server": cfg_server or "",
                "port": cfg_port or "",
                "rest_api": cfg_rest or "",
            },
            "input_time_interval": {
                "time_interval": {"value": ti_value, "unit": ti_units or ""},
                "aggregation": {
                    "method": agg_value or "",
                    "description": agg_desc or "",
                },
                "description": ti_desc or "",
            },
            "artifact": {
                "path": _artifact_path or "",
                "format": _artifact_format,
                "size_bytes": _artifact_size,
                "sha256": _sha256,
            },
            "metrics": {},
            "training": {
                "dataset_hash": "",
                "training_experiment_ids": _experiments,
                "n_instances": n_instances,
                "validation": validation or "",
            },
            "governance": {
                "validation_status": governance_validation_status or "pending",
            },
            "ml_task": ml_task or "regression",
            "model_category": model_category or "data_driven",
        }

        # =======================
        # API CALL
        # =======================
        project_id = _info.get("project_id")
        mode = _info.get("mode", "add")
        db_uuid = _info.get("db_uuid")

        try:
            if mode == "edit" and db_uuid:
                # PATCH — update existing row
                result, session_data = ModelService().update_model_row(
                    session_data, db_uuid, payload
                )
                verb = "updated"
            else:
                # POST — create new row and link to project
                result, session_data = ModelService().create_model_for_project(
                    session_data, project_id, payload
                )
                verb = "saved"

            if result is None:
                return (
                    True,
                    dbc.Alert(
                        "❌ Error: could not save model to the database.",
                        color="danger",
                    ),
                    "danger",
                    "Error",
                    dbc.Alert(
                        "❌ Error: could not save model to the database.",
                        color="danger",
                    ),
                )

            return (
                True,
                dbc.Alert(f"✅ Model {verb} successfully.", color="success"),
                "success",
                "Success",
                dbc.Alert(f"✅ Model {verb} successfully.", color="success"),
                session_data,
            )

        except Exception as exc:
            logger.exception("save_metadata failed")
            return (
                True,
                dbc.Alert(f"❌ Unexpected error: {exc}", color="danger"),
                "danger",
                "Error",
                dbc.Alert(f"❌ Unexpected error: {exc}", color="danger"),
                session_data,
            )

    # ── Scaler Library ─────────────────────────────────────────────────

    # Single source of truth for the scaler list display (fires on load + any change)
    @app.callback(
        Output("scalers-list-container", "children"),
        Input("scalers-store", "data"),
    )
    def sync_scaler_list(scalers):
        return _render_scaler_list(scalers)

    @app.callback(
        Output("scalers-store", "data", allow_duplicate=True),
        Output("scaler-library-feedback", "children"),
        Input("scaler-library-add", "n_clicks"),
        State("scaler-library-upload", "contents"),
        State("scaler-library-upload", "filename"),
        State("new-scaler-name", "value"),
        State("scalers-store", "data"),
        State("add-model-info", "data"),
        prevent_initial_call=True,
    )
    def add_scaler_to_library(
        n_clicks, contents, filename, scaler_name, scalers, model_info
    ):
        import base64
        import os
        import uuid as _uuid

        if not n_clicks or not contents:
            raise PreventUpdate

        filename = filename or "scaler.pkl"
        label = (scaler_name or "").strip() or filename
        _, b64 = contents.split(",", 1)
        decoded = base64.b64decode(b64)

        _info = model_info or {}
        project_id = _info.get("project_id", "")
        slug = _info.get("model_id", "model")
        save_dir = get_path_models_folder(project_id) or "/tmp"
        os.makedirs(save_dir, exist_ok=True)

        scaler_id = str(_uuid.uuid4())[:8]
        save_path = os.path.join(save_dir, f"{slug}_scaler_{scaler_id}_{filename}")
        with open(save_path, "wb") as fh:
            fh.write(decoded)

        scalers = list(scalers or [])
        scalers.append(
            {
                "id": scaler_id,
                "label": label,
                "filename": filename,
                "path": save_path,
            }
        )

        feedback = dbc.Alert(
            f"✅ Scaler '{label}' added.",
            color="success",
            dismissable=True,
            duration=3000,
        )
        return scalers, feedback

    @app.callback(
        Output("scalers-store", "data", allow_duplicate=True),
        Input({"type": "remove-scaler", "id": ALL}, "n_clicks"),
        State("scalers-store", "data"),
        prevent_initial_call=True,
    )
    def remove_scaler(remove_clicks, scalers):
        triggered = ctx.triggered_id
        if not triggered or not any(c for c in (remove_clicks or []) if c):
            raise PreventUpdate
        scaler_id = triggered["id"]
        return [s for s in (scalers or []) if s["id"] != scaler_id]

    # Populate scaler dropdowns on every feature/output when scalers-store changes
    @app.callback(
        Output({"type": "feature-scaler-select", "fid": ALL}, "options"),
        Input("scalers-store", "data"),
        State({"type": "feature-scaler-select", "fid": ALL}, "id"),
    )
    def update_feature_scaler_options(scalers, feature_ids):
        opts = _scaler_options(scalers)
        return [opts] * len(feature_ids)

    @app.callback(
        Output({"type": "output-scaler-select", "fid": ALL}, "options"),
        Input("scalers-store", "data"),
        State({"type": "output-scaler-select", "fid": ALL}, "id"),
    )
    def update_output_scaler_options(scalers, output_ids):
        opts = _scaler_options(scalers)
        return [opts] * len(output_ids)

    # Persist scaler selection back into features/outputs store
    @app.callback(
        Output("add-features-store", "data", allow_duplicate=True),
        Input({"type": "feature-scaler-select", "fid": ALL}, "value"),
        State({"type": "feature-scaler-select", "fid": ALL}, "id"),
        State("add-features-store", "data"),
        State("scalers-store", "data"),
        prevent_initial_call=True,
    )
    def update_feature_scaler_selection(values, ids, features, scalers):
        if not features:
            raise PreventUpdate
        scaler_map = {s["id"]: s for s in (scalers or [])}
        updated = list(features)
        for sel_id_dict, val in zip(ids, values):
            fid = sel_id_dict["fid"]
            for i, f in enumerate(updated):
                if isinstance(f, dict) and f.get("id") == fid:
                    scaler_info = scaler_map.get(val, {})
                    updated[i] = {
                        **f,
                        "scaler_id": val,
                        "scaler_path": scaler_info.get("path", ""),
                        "scaler_filename": scaler_info.get("filename", ""),
                        "has_scaler": val is not None,
                    }
        return updated

    @app.callback(
        Output("add-outputs-store", "data", allow_duplicate=True),
        Input({"type": "output-scaler-select", "fid": ALL}, "value"),
        State({"type": "output-scaler-select", "fid": ALL}, "id"),
        State("add-outputs-store", "data"),
        State("scalers-store", "data"),
        prevent_initial_call=True,
    )
    def update_output_scaler_selection(values, ids, outputs, scalers):
        if not outputs:
            raise PreventUpdate
        scaler_map = {s["id"]: s for s in (scalers or [])}
        updated = list(outputs)
        for sel_id_dict, val in zip(ids, values):
            fid = sel_id_dict["fid"]
            for i, o in enumerate(updated):
                if isinstance(o, dict) and o.get("id") == fid:
                    scaler_info = scaler_map.get(val, {})
                    updated[i] = {
                        **o,
                        "scaler_id": val,
                        "scaler_path": scaler_info.get("path", ""),
                        "scaler_filename": scaler_info.get("filename", ""),
                        "has_scaler": val is not None,
                    }
        return updated

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Input("back-to-list-upload", "n_clicks"),
        State("add-model-info", "data"),
        prevent_initial_call=True,
    )
    def back_to_list(n_clicks, model_info):
        if not n_clicks:
            raise PreventUpdate
        return "/home"
