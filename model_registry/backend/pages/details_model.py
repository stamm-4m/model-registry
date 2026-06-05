import logging

import dash_bootstrap_components as dbc
from dash import dcc, html

from model_registry.backend.services.model_service import get_model_metadata
from model_registry.backend.utils.utils_edit_model import (
    get_value_from_list_of_dicts,
    normalize_date,
    normalize_features,
)
from model_registry.backend.utils.utils_details_model import package_row

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Small UI helpers (presentational only)
# ---------------------------------------------------------------------------
def _info_item(label, value, *, multiline=False, mono=False):
    """Compact label + value block used across the page."""
    val_classes = "details-value"
    if multiline:
        val_classes += " details-value-multiline"
    if mono:
        val_classes += " details-value-mono"
    display_value = value if value not in (None, "") else html.Span("—", className="text-muted fst-italic")
    return html.Div(
        [
            html.Div(label, className="details-label"),
            html.Div(display_value, className=val_classes),
        ],
        className="details-item",
    )


def _section_card(title, icon, body, subtitle=None):
    """A consistent card wrapper for each metadata section."""
    return dbc.Card(
        [
            dbc.CardHeader(
                html.Div(
                    [
                        html.I(className=f"bi {icon} me-2 text-primary"),
                        html.Span(title, className="details-section-title"),
                        html.Small(subtitle, className="text-muted ms-3") if subtitle else None,
                    ],
                    className="d-flex align-items-center",
                ),
                className="bg-white border-0 pt-3 pb-2",
            ),
            dbc.CardBody(body),
        ],
        className="shadow-sm border-0 mb-4 details-card",
    )


def _status_badge(status):
    if status is True:
        status = "online"
    else:
        status = "offline"
    status = (status or "offline").lower()
    color_map = {
        "online": "success",
        "offline": "secondary",
        "deprecated": "warning",
        "error": "danger",
    }
    color = color_map.get(status, "secondary")
    icon = {
        "online": "bi-check-circle-fill",
        "offline": "bi-pause-circle",
        "deprecated": "bi-exclamation-triangle-fill",
        "error": "bi-x-circle-fill",
    }.get(status, "bi-circle")
    return dbc.Badge(
        [html.I(className=f"bi {icon} me-1"), status.capitalize()],
        color=color,
        className="px-3 py-2 details-status-badge",
    )


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
def details_model_layout(project_id, model_id, session_data=None):
    model, _ = get_model_metadata(project_id, model_id, session_data)
    if model is None:
        logger.error("Could not fetch metadata for %s/%s", project_id, model_id)
        return html.Div(
            dbc.Alert(
                "Could not load model details. Please make sure you are logged in "
                "and have permission to view this model.",
                color="danger",
            ),
            className="p-4",
        )
    # -------- Extract data ---------------------------------------------------
    identification = model.get("model_identification", {}) or {}
    description = model.get("model_description", {}) or {}
    config_files = description.get("config_files", {}) or {}
    input_time_interval = description.get("input_time_interval", {}) or {}
    time_interval = input_time_interval.get("time_interval", {}) or {}
    aggregation = input_time_interval.get("aggregation", {}) or {}

    language_data = description.get("language", []) or []
    language_name = get_value_from_list_of_dicts(language_data, "name") or ""
    language_version = get_value_from_list_of_dicts(language_data, "version") or ""

    packages = description.get("packages", []) or []

    features = normalize_features(model.get("inputs", {}).get("features", []) or [])
    outputs = normalize_features(model.get("outputs", {}).get("information", []) or [])

    input_scaler = model.get("inputs", {}).get("scaler") or ""
    output_scaler = model.get("outputs", {}).get("scaler") or ""

    training = model.get("training_information", {}) or {}
    hyperparameters = training.get("hyperparameters", {}) or {}
    value_validation = str(training.get("validation", "") or "")

    model_name = identification.get("ID") or model_id
    model_version = identification.get("version", "")
    # ``status`` is the textual lifecycle (e.g. draft / deployed) and
    # ``is_active`` is the boolean online/offline flag. Older payloads only
    # exposed ``status`` and used it as a boolean -- accept both shapes.
    status_text = identification.get("status", "")
    if isinstance(status_text, bool):
        status_text = ""
    if "is_active" in identification:
        is_active = identification.get("is_active")
    else:
        is_active = identification.get("status", False)

    # -------- Hero / page header --------------------------------------------
    hero = dbc.Card(
        dbc.CardBody(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.I(className="bi bi-cpu-fill text-primary me-2"),
                                    html.Span("Model Details", className="text-muted small text-uppercase fw-semibold letter-spaced"),
                                ],
                                className="mb-2",
                            ),
                            html.H2(model_name, className="details-hero-title mb-1"),
                            html.Div(
                                [
                                    html.Span(
                                        [html.I(className="bi bi-folder2-open me-1"), f"Project: {project_id}"],
                                        className="me-3 text-muted small",
                                    ),
                                    html.Span(
                                        [html.I(className="bi bi-hash me-1"), f"ID: {identification.get('ID', model_id)}"],
                                        className="me-3 text-muted small",
                                    ),
                                    html.Span(
                                        [html.I(className="bi bi-tag me-1"), f"v{model_version}" if model_version else "—"],
                                        className="me-3 text-muted small",
                                    ),
                                ],
                                className="mb-2 d-flex flex-wrap",
                            ),
                            html.Div(
                                [
                                    _status_badge(is_active),
                                    dbc.Badge(
                                        [html.I(className="bi bi-code-slash me-1"), f"{language_name} {language_version}".strip() or "—"],
                                        color="light",
                                        text_color="dark",
                                        className="ms-2 px-3 py-2 border",
                                    ),
                                    dbc.Badge(
                                        [html.I(className="bi bi-diagram-3 me-1"), description.get("learner") or description.get("model_type") or "—"],
                                        color="light",
                                        text_color="dark",
                                        className="ms-2 px-3 py-2 border",
                                    ),
                                ],
                                className="d-flex flex-wrap align-items-center",
                            ),
                        ],
                        md=8,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.Div("Created", className="text-muted small text-uppercase fw-semibold"),
                                html.Div(
                                    normalize_date(identification.get("creation_date", "")) or "—",
                                    className="fw-semibold mb-2",
                                ),
                                html.Div("Author", className="text-muted small text-uppercase fw-semibold"),
                                html.Div(identification.get("author", "") or "—", className="fw-semibold"),
                            ],
                            className="text-md-end",
                        ),
                        md=4,
                        className="d-flex align-items-center justify-content-md-end",
                    ),
                ],
                className="g-3",
            )
        ),
        className="shadow-sm border-0 mb-4 details-hero",
    )

    # -------- Identification card -------------------------------------------
    identification_body = dbc.Row(
        [
            dbc.Col(
                [
                    _info_item("Model ID", identification.get("ID", "")),
                    _info_item("Model UUID", identification.get("UUID", ""), mono=True),
                    _info_item("DOI", identification.get("doi", "")),
                ],
                md=6,
            ),
            dbc.Col(
                [
                    _info_item("Name", identification.get("name", "")),
                    _info_item("Version", identification.get("version", "")),
                    _info_item("Status", status_text),
                    _info_item(
                        "Status description",
                        identification.get("status_description", ""),
                        multiline=True,
                    ),
                ],
                md=6,
            ),
        ],
        className="g-3",
    )

    # -------- Description card ----------------------------------------------
    description_body = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            _info_item("Learner", description.get("learner", "")),
                            _info_item("Model type", description.get("model_type", "")),
                            _info_item("Model name", description.get("model_name", "")),
                            _info_item("Language", language_name),
                            _info_item("Language version", language_version),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            _info_item(
                                "Description",
                                description.get("description", ""),
                                multiline=True,
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="g-3",
            ),
            html.Hr(className="my-4"),
            html.Div(
                [
                    html.H6(
                        [html.I(className="bi bi-box-seam me-2 text-primary"), "Packages"],
                        className="details-subsection-title mb-3",
                    ),
                    html.Div(
                        id="packages-container",
                        children=[
                            package_row(i, p.get("package", ""), p.get("version", "-"))
                            for i, p in enumerate(packages)
                        ]
                        or [package_row(0)],
                    ),
                ]
            ),
        ]
    )

    # -------- Configuration & deployment ------------------------------------
    config_body = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            _info_item("Model file", config_files.get("model_file", ""), mono=True),
                            _info_item("Server", config_files.get("server", "")),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            _info_item("Port", config_files.get("port", "")),
                            _info_item("REST API", config_files.get("rest_api", ""), mono=True),
                        ],
                        md=6,
                    ),
                ],
                className="g-3",
            ),
            html.Hr(className="my-4"),
            html.H6(
                [html.I(className="bi bi-clock-history me-2 text-primary"), "Input time interval"],
                className="details-subsection-title mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            _info_item("Value", time_interval.get("value", "")),
                            _info_item("Units", time_interval.get("unit", "")),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            _info_item(
                                "Description",
                                input_time_interval.get("description", ""),
                                multiline=True,
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="g-3",
            ),
            html.Hr(className="my-4"),
            html.H6(
                [html.I(className="bi bi-bar-chart-steps me-2 text-primary"), "Aggregation"],
                className="details-subsection-title mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(_info_item("Method", aggregation.get("method", "")), md=6),
                    dbc.Col(
                        _info_item(
                            "Description",
                            aggregation.get("description", ""),
                            multiline=True,
                        ),
                        md=6,
                    ),
                ],
                className="g-3",
            ),
        ]
    )

    # -------- Training information ------------------------------------------
    training_body = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H6(
                                [html.I(className="bi bi-sliders me-2 text-primary"), "Hyperparameters"],
                                className="details-subsection-title mb-3",
                            ),
                            _info_item("Number of trees", hyperparameters.get("number_of_trees", "")),
                            _info_item("Max tree depth", hyperparameters.get("max_tree_depth", "")),
                            _info_item(
                                "Min instances per leaf",
                                hyperparameters.get("min_number_instances_per_leaf", ""),
                            ),
                            _info_item("Committees", hyperparameters.get("committees", "")),
                            _info_item(
                                "Instance-based corrections",
                                hyperparameters.get("instance_based_corrections", ""),
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.H6(
                                [html.I(className="bi bi-clipboard-data me-2 text-primary"), "Dataset & validation"],
                                className="details-subsection-title mb-3",
                            ),
                            _info_item("Number of instances", training.get("number_of_instances", "")),
                            _info_item("Validation", value_validation),
                            html.Div(
                            [
                                html.Div(
                                    "Training experiments ID",
                                    className="details-label",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            exp_id,
                                            className="training-id-box",
                                        )
                                        for exp_id in (
                                            training.get("experiments_ID", [])
                                            if isinstance(training.get("experiments_ID", []), list)
                                            else [training.get("experiments_ID", "")]
                                        )
                                        if exp_id
                                    ],
                                    className="training-id-container",
                                ),
                            ],
                            className="details-item",
                        )
                        ],
                        md=6,
                    ),
                ],
                className="g-3",
            ),
        ]
    )

    # -------- Inputs / outputs ----------------------------------------------
    inputs_body = html.Div(
        [
            _info_item("Input scaler", input_scaler, mono=True),
            html.P(
                f"{len(features)} feature(s) used as input.",
                className="text-muted small mb-3 mt-3",
            ),
            dbc.Accordion(id="features-accordion-details", always_open=True),
        ]
    )

    outputs_body = html.Div(
        [
            _info_item("Output scaler", output_scaler, mono=True),
            html.P(
                f"{len(outputs)} output(s) produced by the model.",
                className="text-muted small mb-3 mt-3",
            ),
            dbc.Accordion(id="outputs-accordion-details", always_open=True),
        ]
    )

    # -------- Action bar ----------------------------------------------------
    action_bar = dbc.Card(
        dbc.CardBody(
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            [html.I(className="bi bi-arrow-left me-1"), "Back to list"],
                            id="back-to-list",
                            color="secondary",
                            outline=True,
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Button(
                            [html.I(className="bi bi-download me-1"), "Download model"],
                            id="download-model",
                            color="primary",
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        html.Div(id="download-feedback", className="ms-3 fw-semibold"),
                    ),
                ],
                className="align-items-center g-2",
            )
        ),
        className="shadow-sm border-0 details-action-bar",
    )

    # -------- Compose page --------------------------------------------------
    return dbc.Container(
        [
            dcc.Store(id="features-store-details", data=features),
            dcc.Store(id="outputs-store-details", data=outputs if outputs else []),
            dcc.Download(id="download-model-file"),
            dcc.Store(
                id="edit-model-info",
                data={"project_id": project_id, "model_id": model_id},
            ),
            hero,
            _section_card("Identification", "bi-fingerprint", identification_body),
            _section_card("Model Description", "bi-card-text", description_body),
            _section_card(
                "Configuration & Deployment",
                "bi-gear-wide-connected",
                config_body,
            ),
            _section_card("Training Information", "bi-mortarboard", training_body),
            _section_card("Inputs", "bi-input-cursor-text", inputs_body, subtitle=f"{len(features)} feature(s)"),
            _section_card("Outputs", "bi-arrow-bar-right", outputs_body, subtitle=f"{len(outputs)} output(s)"),
            action_bar,
        ],
        fluid=True,
        className="details-page p-4",
    )

