import logging

import dash_bootstrap_components as dbc
from dash import dcc, html

from model_registry.backend.utils.utils_template_ui import (
    algorithm_selector_dropdown,
    template_config_section,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fetch_model_row(slug: str, session_data) -> dict:
    """Return the flat DB row whose slug matches, or {}."""
    try:
        from model_registry.backend.services.model_service import ModelService
        rows, _ = ModelService().get_all_model_rows(session_data)
        return next((r for r in (rows or []) if r.get("slug") == slug), {})
    except Exception as exc:
        logger.warning("Could not fetch model row for slug=%s: %s", slug, exc)
        return {}


def _lang_name(language_jsonb) -> str:
    """Extract language name from [{name: ...}, {version: ...}] JSONB."""
    if isinstance(language_jsonb, list):
        return next((d.get("name", "") for d in language_jsonb if isinstance(d, dict) and "name" in d), "")
    return ""


def _lang_ver(language_jsonb) -> str:
    """Extract language version from [{name: ...}, {version: ...}] JSONB."""
    if isinstance(language_jsonb, list):
        return next((d.get("version", "") for d in language_jsonb if isinstance(d, dict) and "version" in d), "")
    return ""


def _pkg_rows(packages_jsonb, disabled=False):
    """Render pre-populated package rows for the packages container."""
    from model_registry.backend.utils.utils_edit_model import package_row
    rows = []
    for i, pkg in enumerate(packages_jsonb or []):
        rows.append(package_row(i, package=pkg.get("package", ""), version=pkg.get("version", "")))
    return rows


# ---------------------------------------------------------------------------
# Shared form layout  (add | edit | details)
# ---------------------------------------------------------------------------

def _io_items(value):
    """Coerce a model's inputs/outputs field into a flat list of dicts.

    Accepts BOTH shapes seen in the registry:
      * flat list (written by the form's save path):
            [{"name": ..., "type": ...}, ...]
      * the seed / YAML-registry object shape:
            inputs  = {"scaler": ..., "features": [...]}
            outputs = {"scaler": ..., "information": [...]}
    Without this, a model stored in the object shape rendered no features
    (the old code iterated the dict keys instead of the list). (fix 2026-06-12)
    """
    if isinstance(value, dict):
        for k in ("features", "information", "outputs", "inputs", "items"):
            inner = value.get(k)
            if isinstance(inner, list):
                return inner
            if isinstance(inner, dict):
                # A single feature dict, or a {name: spec} map. Some
                # models (e.g. reshaped LSTM inputs) store it this way.
                if "name" in inner:
                    return [inner]
                return [
                    {"name": kk, **(vv if isinstance(vv, dict) else {"value": vv})}
                    for kk, vv in inner.items()
                ]
        return []
    if isinstance(value, list):
        return value
    return []


def _normalize_io(items):
    """Ensure every input/output dict has an 'id' key, as feature_item requires.

    Tolerates the object shape ({"scaler":.., "features":[...]}) via _io_items.
    """
    import uuid as _uuid
    normalized = []
    for item in _io_items(items):
        if isinstance(item, str):
            item = {"name": item}
        if isinstance(item, dict):
            if "id" not in item:
                item = {**item, "id": str(_uuid.uuid4())}
            normalized.append(item)
    return normalized


def _extract_scalers_from_io(inputs, outputs):
    """Reconstruct scalers-store entries from scaler_* fields in inputs/outputs.

    When a model is loaded from the DB, scaler metadata is embedded in each
    input/output dict.  This rebuilds the library list so the dropdowns can
    show the correct selection in edit/details mode.
    """
    seen = {}
    for item in list(inputs or []) + list(outputs or []):
        if not isinstance(item, dict):
            continue
        sid = item.get("scaler_id")
        if sid and sid not in seen:
            seen[sid] = {
                "id":       sid,
                "label":    item.get("scaler_filename") or sid,
                "filename": item.get("scaler_filename") or "",
                "path":     item.get("scaler_path")     or "",
            }
    return list(seen.values())


def _build_io_and_scalers(raw_inputs, raw_outputs):
    """Return (scaler_library, feature_items, output_items) for the stores.

    Builds the Scaler Library from BOTH places a scaler can live:
      * per-item scaler_id/scaler_filename (flat list written by the form)
      * the object-level scaler filename used by the seed / YAML registry
        (inputs={"scaler": "X.pkl", "features":[...]}, outputs={"scaler": "y.pkl", ...}).
    The object-level X-scaler is assigned to every input feature and the
    Y-scaler to every output, so the dropdowns show the right selection.
    Previously the object-level scaler was ignored, so SVM/LSTM scalers
    never loaded. (fix 2026-06-12)
    """
    import uuid as _uuid
    feat_items = _normalize_io(raw_inputs)
    out_items  = _normalize_io(raw_outputs)
    library = {}

    # (1) per-item scalers already embedded -> preserve their ids
    for it in feat_items + out_items:
        sid = it.get("scaler_id")
        if sid and sid not in library:
            library[sid] = {
                "id": sid,
                "label": it.get("scaler_filename") or sid,
                "filename": it.get("scaler_filename") or "",
                "path": it.get("scaler_path") or "",
            }

    # (2) object-level scaler filename -> one X-scaler for inputs, one Y for outputs
    def _attach(items, filename, role):
        if not filename:
            return
        sid = next((sc["id"] for sc in library.values()
                    if sc["filename"] == filename), None)
        if sid is None:
            sid = f"scaler-{role}-{str(_uuid.uuid4())[:8]}"
            library[sid] = {"id": sid, "label": filename,
                            "filename": filename, "path": ""}
        for it in items:
            if not it.get("scaler_id"):
                it["scaler_id"] = sid
                it["scaler_filename"] = filename
                it["has_scaler"] = True

    _attach(feat_items, raw_inputs.get("scaler") if isinstance(raw_inputs, dict) else None, "x")
    _attach(out_items,  raw_outputs.get("scaler") if isinstance(raw_outputs, dict) else None, "y")

    return list(library.values()), feat_items, out_items



def model_form_layout(mode: str, project_id: str, model_id: str = None, session_data=None):
    """Single tabbed form for Add / Edit / Details.

    mode:
        "add"     – blank form, POST on save
        "edit"    – pre-populated from DB, PATCH on save
        "details" – pre-populated, all inputs disabled, no save button
    """
    row = {}
    db_uuid = None
    if mode in ("edit", "details") and model_id and session_data:
        row = _fetch_model_row(model_id, session_data)
        db_uuid = row.get("id")

    disabled = (mode == "details")

    def v(key, default=""):
        val = row.get(key)
        return val if val is not None else default

    # Language lives as JSONB list
    lang_name = _lang_name(v("language", []))
    lang_ver  = _lang_ver(v("language", []))

    # Training info from JSONB
    ti = v("training_information", {}) or {}

    # Packages
    pkg_children = _pkg_rows(v("packages", []), disabled=disabled)

    # Inputs/outputs + scaler library (tolerant of object & flat-list shapes)
    _io_scaler_library, _io_feature_items, _io_output_items = _build_io_and_scalers(
        v("inputs", []), v("outputs", []))

    titles = {
        "add":     ("Add Model",      "Register a new model into the project registry."),
        "edit":    ("Edit Model",     "Update model metadata and configuration."),
        "details": ("Model Details",  "Read-only view of model metadata and configuration."),
    }
    page_title, page_sub = titles[mode]

    save_label = "Update Model" if mode == "edit" else "Save Model"
    show_save  = mode in ("add", "edit")

    return html.Div([
        dcc.Store(id="add-model-info", data={
            "project_id": project_id,
            "model_id":   model_id,
            "db_uuid":    db_uuid,
            "mode":       mode,
        }),
        dcc.Store(id="add-features-store", data=_io_feature_items),
        dcc.Store(id="add-outputs-store",  data=_io_output_items),
        dcc.Store(id="template-config-store", data={}),
        dcc.Store(id="scalers-store", data=_io_scaler_library),

        dbc.Toast(
            id="save-model-toast",
            header="Notification",
            is_open=False,
            dismissable=True,
            duration=4000,
            icon="success",
            style={"position": "fixed", "top": 10, "right": 10, "width": 350, "zIndex": 9999},
        ),

        # ── Page header ────────────────────────────────────────────────
        html.Div([
            html.Div([
                html.H2(page_title, className="mb-0"),
                html.P(page_sub, className="page-sub"),
            ]),
        ], className="page-title-row mb-4"),

        # ── Tabs ───────────────────────────────────────────────────────
        dbc.Tabs([

            # ── Tab 1: Identity ────────────────────────────────────────
            dbc.Tab(label="① Identity", tab_id="tab-identity", children=[
                html.Div([
                    # File upload — only in add mode
                    dbc.Card(dbc.CardBody([
                        html.P("Model File", className="panel-title mb-2"),
                        dcc.Upload(
                            id="upload-data",
                            children=html.Div([
                                html.I(className="bi bi-cloud-upload fs-1 text-primary d-block mb-2"),
                                html.Span("Drag & drop your model file here, or "),
                                html.Span("browse", style={"textDecoration": "underline", "cursor": "pointer", "color": "#0d6efd"}),
                                html.Br(),
                                html.Small("Accepted: .pkl  .joblib  .keras  .h5  .rds  .yaml  .r", className="text-muted"),
                            ] if mode == "add" else [
                                html.I(className="bi bi-file-earmark-binary fs-1 text-muted d-block mb-2"),
                                html.Span(v("artifact_path", "No artifact on record") or "No artifact on record", className="text-muted"),
                            ], className="text-center py-4"),
                            accept=".pkl,.joblib,.keras,.h5,.rds,.yaml,.r",
                            multiple=False,
                            disabled=disabled,
                            style={
                                "border": "2px dashed #dee2e6",
                                "borderRadius": "8px",
                                "cursor": "pointer" if not disabled else "default",
                                "backgroundColor": "#f8f9fa",
                            },
                        ),
                        html.Div(id="output-data-upload", className="mt-2"),
                        html.Small([
                            html.I(className="bi bi-info-circle me-1"),
                            "Model ID, language and algorithm are auto-detected from the filename. Best results with STAMM convention: ",
                            html.Code("0001_[python]_name_ALGO.pkl"),
                            ". You can always edit them below."
                        ], className="text-muted d-block mt-2") if mode == "add" else None,
                    ]), className="mb-3 shadow-sm"),

                    # Identity fields
                    dbc.Card(dbc.CardBody([
                        html.P("Identification", className="panel-title mb-3"),
                        dbc.Row([
                            dbc.Col([
                                dbc.FormFloating([
                                    dbc.Input(id="add_model_id", type="text",
                                              placeholder="Auto-detected from filename — editable",
                                              value=v("slug"), disabled=disabled),
                                    dbc.Label("Model ID"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(id="add_name", type="text", placeholder="Model Name",
                                              value=v("name"), disabled=disabled),
                                    dbc.Label("Model Name"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(id="add_model_version", type="text", placeholder="e.g. 1.0.0",
                                              value=v("version"), disabled=disabled),
                                    dbc.Label("Version"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(id="add_model_uuid", type="text", placeholder="UUID",
                                              value=v("external_uuid"), disabled=disabled),
                                    dbc.Label("UUID"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(id="add_model_doi", type="text", placeholder="DOI",
                                              value=v("doi"), disabled=disabled),
                                    dbc.Label("DOI"),
                                ], className="mb-3"),
                            ], md=6),
                            dbc.Col([
                                dbc.FormFloating([
                                    dbc.Input(id="add_creation_date", type="date",
                                              value=v("creation_date"), disabled=disabled),
                                    dbc.Label("Creation Date"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Textarea(id="add_author", placeholder="Author(s)",
                                                 style={"height": "100px"},
                                                 value=v("authors"), disabled=disabled),
                                    dbc.Label("Author(s)"),
                                ], className="mb-3"),
                                html.Div([
                                    dbc.Label("Serving Status", className="fw-semibold text-muted small text-uppercase mb-1"),
                                    dbc.RadioItems(
                                        id="add_is_active",
                                        options=[
                                            {"label": "Online",  "value": True},
                                            {"label": "Offline", "value": False},
                                        ],
                                        value=v("is_active", True),
                                        inline=True,
                                        className="mb-3",
                                    ),
                                ]),
                                html.Div([
                                    dbc.Label("Validation Status", className="fw-semibold text-muted small text-uppercase mb-1"),
                                    dbc.RadioItems(
                                        id="add_governance_validation_status",
                                        options=[
                                            {"label": "Pending",  "value": "pending"},
                                            {"label": "Approved", "value": "approved"},
                                            {"label": "Rejected", "value": "rejected"},
                                        ],
                                        value=v("validation_status", "pending"),
                                        inline=True,
                                        className="mb-3",
                                    ),
                                ]),
                                dbc.FormFloating([
                                    dbc.Input(id="add_status", type="text", placeholder="e.g. trained, draft",
                                              value=v("status"), disabled=disabled),
                                    dbc.Label("Lifecycle Status"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(id="add_status_description", type="text",
                                              placeholder="Short description of current status",
                                              value=v("status_description"), disabled=disabled),
                                    dbc.Label("Status Description"),
                                ], className="mb-3"),
                            ], md=6),
                        ]),
                    ]), className="mb-3 shadow-sm"),
                ], className="pt-3"),
            ]),

            # ── Tab 2: Description ─────────────────────────────────────
            dbc.Tab(label="② Description", tab_id="tab-description", children=[
                html.Div([
                    dbc.Card(dbc.CardBody([
                        html.P("Algorithm & Language", className="panel-title mb-3"),
                        dbc.Row([
                            dbc.Col([
                                dbc.FormFloating([
                                    dbc.Input(id="add_learner", type="text",
                                              placeholder="e.g. RandomForest, LSTM",
                                              value=v("learner"), disabled=disabled),
                                    dbc.Label("Learner"),
                                ], className="mb-3"),
                                # Learner Family dropdown — drives hyperparameters in Training tab
                                algorithm_selector_dropdown(value=v("algorithm")),
                                html.Div([
                                    dbc.Label("ML Task", className="fw-semibold text-muted small text-uppercase mb-1"),
                                    dcc.Dropdown(
                                        id="add_ml_task",
                                        options=[
                                            {"label": "Regression",               "value": "regression"},
                                            {"label": "Classification",           "value": "classification"},
                                            {"label": "Clustering",               "value": "clustering"},
                                            {"label": "Dimensionality Reduction", "value": "dimensionality_reduction"},
                                            {"label": "Forecasting",              "value": "forecasting"},
                                            {"label": "Density Estimation",       "value": "density_estimation"},
                                            {"label": "Anomaly Detection",        "value": "anomaly_detection"},
                                        ],
                                        placeholder="Select ML task…",
                                        clearable=True,
                                        disabled=disabled,
                                    ),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(id="add_model_name", type="text",
                                              placeholder="Full model name",
                                              value=v("name"), disabled=disabled),
                                    dbc.Label("Full Model Name"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Textarea(id="add_description",
                                                 placeholder="Describe what this model does...",
                                                 style={"height": "120px"},
                                                 value=v("description"), disabled=disabled),
                                    dbc.Label("Description"),
                                ], className="mb-3"),
                            ], md=6),
                            dbc.Col([
                                html.Div([
                                    dbc.Label("Model Category", className="fw-semibold text-muted small text-uppercase mb-1"),
                                    dcc.Dropdown(
                                        id="add_model_category",
                                        options=[
                                            {"label": "Data-Driven", "value": "data_driven"},
                                            {"label": "Mechanistic", "value": "mechanistic"},
                                            {"label": "Hybrid",      "value": "hybrid"},
                                        ],
                                        placeholder="Select model category…",
                                        clearable=True,
                                        disabled=disabled,
                                    ),
                                ], className="mb-3"),
                                html.Div([
                                    dbc.Label("Model Type (explainability)", className="fw-semibold text-muted small text-uppercase mb-1"),
                                    dcc.Dropdown(
                                        id="add_model_type",
                                        options=[
                                            {"label": "Interpretable", "value": "interpretable"},
                                            {"label": "Black Box",     "value": "black_box"},
                                            {"label": "Hybrid",        "value": "hybrid"},
                                        ],
                                        value=v("model_type") or None,
                                        placeholder="Select model type…",
                                        clearable=True,
                                        disabled=disabled,
                                    ),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(id="add_language", type="text",
                                              placeholder="e.g. Python, R",
                                              value=lang_name, disabled=disabled),
                                    dbc.Label("Language"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(id="add_language_version", type="text",
                                              placeholder="e.g. 3.10",
                                              value=lang_ver, disabled=disabled),
                                    dbc.Label("Language Version"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(id="add_config_model_file", type="text",
                                              placeholder="Auto-populated from uploaded file",
                                              readonly=True, className="text-muted",
                                              value=v("artifact_path")),
                                    dbc.Label("Model File (auto)"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(id="add_config_server", type="text",
                                              placeholder="Server",
                                              value=(v("config_files") or {}).get("server", ""),
                                              disabled=disabled),
                                    dbc.Label("Server"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(id="add_config_port", type="text",
                                              placeholder="Port",
                                              value=(v("config_files") or {}).get("port", ""),
                                              disabled=disabled),
                                    dbc.Label("Port"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(id="add_config_rest_api", type="text",
                                              placeholder="REST API endpoint",
                                              value=(v("config_files") or {}).get("rest_api", ""),
                                              disabled=disabled),
                                    dbc.Label("REST API"),
                                ], className="mb-3"),
                            ], md=6),
                        ]),
                    ]), className="mb-3 shadow-sm"),

                    dbc.Card(dbc.CardBody([
                        html.P("Packages", className="panel-title mb-3"),
                        html.Div(id="add-packages-container", children=pkg_children),
                        dbc.Button("➕ Add package", id="add-add-package",
                                   color="secondary", outline=True, size="sm",
                                   className="mt-2", disabled=disabled),
                    ]), className="mb-3 shadow-sm"),

                    dbc.Card(dbc.CardBody([
                        html.P("Input Time Interval", className="panel-title mb-3"),
                        dbc.Row([
                            dbc.Col([
                                dbc.FormFloating([
                                    dbc.Input(id="add_time_interval", type="number",
                                              placeholder="Value",
                                              value=((v("input_time_interval") or {}).get("time_interval") or {}).get("value"),
                                              disabled=disabled),
                                    dbc.Label("Interval Value"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(id="add_time_interval_units", type="text",
                                              placeholder="e.g. minutes, seconds",
                                              value=((v("input_time_interval") or {}).get("time_interval") or {}).get("unit", ""),
                                              disabled=disabled),
                                    dbc.Label("Units"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(id="add_time_interval_description", type="text",
                                              placeholder="Description",
                                              value=(v("input_time_interval") or {}).get("description", ""),
                                              disabled=disabled),
                                    dbc.Label("Description"),
                                ], className="mb-3"),
                            ], md=6),
                            dbc.Col([
                                dbc.FormFloating([
                                    dbc.Input(id="add_time_interval_aggregation", type="text",
                                              placeholder="e.g. mean, last",
                                              value=((v("input_time_interval") or {}).get("aggregation") or {}).get("method", ""),
                                              disabled=disabled),
                                    dbc.Label("Aggregation Method"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(id="add_time_interval_aggregation_description", type="text",
                                              placeholder="Aggregation description",
                                              value=((v("input_time_interval") or {}).get("aggregation") or {}).get("description", ""),
                                              disabled=disabled),
                                    dbc.Label("Aggregation Description"),
                                ], className="mb-3"),
                            ], md=6),
                        ]),
                    ]), className="mb-3 shadow-sm"),
                ], className="pt-3"),
            ]),

            # ── Tab 3: Inputs & Outputs ────────────────────────────────
            dbc.Tab(label="③ Inputs & Outputs", tab_id="tab-io", children=[
                html.Div([
                    dbc.Card(dbc.CardBody([
                        html.P("Scaler Library", className="panel-title mb-3"),
                        html.Small([
                            html.I(className="bi bi-info-circle me-1"),
                            "Upload scalers once here, then assign them to any input or output below.",
                        ], className="text-muted d-block mb-3"),
                        # Uploaded scalers list
                        html.Div(id="scalers-list-container", children=[
                            html.Span("No scalers uploaded yet.", className="text-muted fst-italic small"),
                        ]),
                        html.Hr(className="my-3"),
                        dbc.Row([
                            dbc.Col([
                                dbc.FormFloating([
                                    dbc.Input(id="new-scaler-name", type="text",
                                              placeholder="e.g. X_scaler, y_scaler"),
                                    dbc.Label("Scaler name"),
                                ]),
                            ], md=5),
                            dbc.Col([
                                dcc.Upload(
                                    id="scaler-library-upload",
                                    children=html.Div([
                                        html.I(className="bi bi-cloud-upload me-2 text-primary"),
                                        "Drop scaler file or ",
                                        html.Span("browse",
                                                  style={"textDecoration": "underline",
                                                         "cursor": "pointer",
                                                         "color": "#0d6efd"}),
                                        html.Br(),
                                        html.Small(".pkl  .joblib  .rds", className="text-muted"),
                                    ], className="text-center py-2"),
                                    accept=".pkl,.joblib,.rds",
                                    multiple=False,
                                    style={
                                        "border": "2px dashed #dee2e6",
                                        "borderRadius": "8px",
                                        "cursor": "pointer",
                                        "backgroundColor": "#f8f9fa",
                                    },
                                ),
                            ], md=5),
                            dbc.Col([
                                dbc.Button("Add", id="scaler-library-add",
                                           color="primary", outline=True,
                                           size="sm", className="mt-1"),
                            ], md=2),
                        ], className="align-items-end"),
                        html.Div(id="scaler-library-feedback", className="mt-2"),
                    ]), className="mb-3 shadow-sm"),

                    dbc.Card(dbc.CardBody([
                        html.P("Inputs", className="panel-title mb-3"),
                        dbc.Accordion(id="add-features-accordion", always_open=True),
                        dbc.Button("➕ Add input feature", id="add-add-feature",
                                   color="secondary", outline=True, size="sm",
                                   className="mt-3", disabled=disabled),
                    ]), className="mb-3 shadow-sm"),

                    dbc.Card(dbc.CardBody([
                        html.P("Outputs", className="panel-title mb-3"),
                        dbc.Accordion(id="add-outputs-accordion", always_open=True),
                        dbc.Button("➕ Add output", id="add-add-output",
                                   color="secondary", outline=True, size="sm",
                                   className="mt-3", disabled=disabled),
                    ]), className="mb-3 shadow-sm"),
                ], className="pt-3"),
            ]),

            # ── Tab 4: Training ────────────────────────────────────────
            dbc.Tab(label="④ Training", tab_id="tab-training", children=[
                html.Div([
                    dbc.Card(dbc.CardBody([
                        html.P("Learner Hyperparameters", className="panel-title mb-3"),
                        html.Small([
                            html.I(className="bi bi-info-circle me-1"),
                            "Hyperparameters are loaded from the ",
                            html.Strong("Learner Family"),
                            " selected in the Description tab.",
                        ], className="text-muted d-block mb-3"),
                        template_config_section(),
                    ]), className="mb-3 shadow-sm"),

                    dbc.Card(dbc.CardBody([
                        html.P("Training Information", className="panel-title mb-3"),
                        dbc.Row([
                            dbc.Col([
                                dbc.FormFloating([
                                    dbc.Input(id="add_number_of_instances", type="text",
                                              placeholder="e.g. 5000",
                                              value=str(ti.get("n_instances", "") or ti.get("number_of_instances", "") or ""),
                                              disabled=disabled),
                                    dbc.Label("Number of Instances"),
                                ], className="mb-3"),
                                dbc.FormFloating([
                                    dbc.Input(id="add_validation", type="text",
                                              placeholder="e.g. 5-fold CV, hold-out 20%",
                                              value=str(ti.get("validation", "") or ""),
                                              disabled=disabled),
                                    dbc.Label("Validation Strategy"),
                                ], className="mb-3"),
                            ], md=6),
                            dbc.Col([
                                dbc.FormFloating([
                                    dbc.Textarea(id="add_experiments_id",
                                                 placeholder="Experiment IDs used for training",
                                                 style={"height": "120px"},
                                                 value=", ".join(str(x) for x in (ti.get("experiments_ID") or [])),
                                                 disabled=disabled),
                                    dbc.Label("Training Experiment IDs"),
                                ], className="mb-3"),
                            ], md=6),
                        ]),
                    ]), className="mb-3 shadow-sm"),
                ], className="pt-3"),
            ]),

        ], id="add-model-tabs", active_tab="tab-identity", className="mb-3"),

        # ── Action bar ─────────────────────────────────────────────────
        dbc.Card(dbc.CardBody(
            dbc.Row([
                dbc.Col(
                    dbc.Button("← Back to list", id="back-to-list-upload",
                               color="secondary", outline=True),
                    width="auto",
                ),
                dbc.Col(
                    dbc.Button(save_label, id="save-ml-model-config", color="primary",
                               style={"display": "none" if not show_save else "inline-block"}),
                    width="auto",
                ) if True else None,
                dbc.Col(html.Div(id="save-model-feedback", className="ms-3 fw-semibold")),
            ], className="align-items-center"),
        ), className="shadow-sm"),
    ])


# ---------------------------------------------------------------------------
# Public entry points (existing call-sites remain unchanged)
# ---------------------------------------------------------------------------

def model_upload_layout(project_id):
    """Thin wrapper kept for backward compat — Add mode."""
    return model_form_layout("add", project_id)
