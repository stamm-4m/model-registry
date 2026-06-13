import logging

import dash_bootstrap_components as dbc
from dash import html, dcc

from model_registry.backend.services.model_service import get_model_metadata

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Small UI helpers (mirror the look-and-feel of details_model.py)
# ---------------------------------------------------------------------------
def _info_item(label, value, *, mono=False):
    val_classes = "details-value"
    if mono:
        val_classes += " details-value-mono"
    display_value = (
        value
        if value not in (None, "")
        else html.Span("—", className="text-muted fst-italic")
    )
    return html.Div(
        [
            html.Div(label, className="details-label"),
            html.Div(display_value, className=val_classes),
        ],
        className="details-item",
    )


def _section_card(title, icon, body, *, subtitle=None, header_image=None,
                  header_color=None):
    header_content = []
    if header_image:
        header_content.append(
            html.Img(
                src=header_image,
                style={
                    "height": "28px",
                    "marginRight": "10px",
                    "verticalAlign": "middle",
                },
            )
        )
    else:
        header_content.append(
            html.I(className=f"bi {icon} me-2 text-primary")
        )
    title_style = {"color": header_color} if header_color else None
    header_content.append(
        html.Span(title, className="details-section-title", style=title_style)
    )
    if subtitle:
        header_content.append(
            html.Small(subtitle, className="text-muted ms-3")
        )
    return dbc.Card(
        [
            dbc.CardHeader(
                html.Div(header_content, className="d-flex align-items-center"),
                className="bg-white border-0 pt-3 pb-2",
            ),
            dbc.CardBody(body),
        ],
        className="shadow-sm border-0 mb-4 details-card h-100",
    )


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
def add_upload_model_ibisba_layout(project_id, model_id, session_data=None):
    model, _ = get_model_metadata(project_id, model_id, session_data)
    if model is None:
        logger.error("Could not fetch metadata for %s/%s", project_id, model_id)
        return html.Div(
            dbc.Alert(
                "Could not load model information. Please make sure you are "
                "logged in and have permission to view this model.",
                color="danger",
            ),
            className="p-4",
        )
    model_information = (model.get("model_identification") or {}) if model else {}

    # -------- Hero -----------------------------------------------------------
    hero = dbc.Card(
        dbc.CardBody(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.I(className="bi bi-cloud-upload-fill text-primary me-2"),
                                    html.Span(
                                        "Publish to IBISBA Hub",
                                        className="text-muted small text-uppercase fw-semibold letter-spaced",
                                    ),
                                ],
                                className="mb-2",
                            ),
                            html.H2(
                                model_information.get("name") or model_id,
                                className="details-hero-title mb-1",
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        [
                                            html.I(className="bi bi-folder2-open me-1"),
                                            f"Project: {project_id}",
                                        ],
                                        className="me-3 text-muted small",
                                    ),
                                    html.Span(
                                        [
                                            html.I(className="bi bi-hash me-1"),
                                            f"ID: {model_information.get('ID', model_id)}",
                                        ],
                                        className="me-3 text-muted small",
                                    ),
                                    html.Span(
                                        [
                                            html.I(className="bi bi-tag me-1"),
                                            f"v{model_information.get('version')}"
                                            if model_information.get("version")
                                            else "—",
                                        ],
                                        className="me-3 text-muted small",
                                    ),
                                ],
                                className="d-flex flex-wrap",
                            ),
                        ],
                        md=12,
                    ),
                ],
                className="g-3",
            )
        ),
        className="shadow-sm border-0 mb-4 details-hero",
    )

    # -------- Left card: registry information --------------------------------
    registry_body = html.Div(
        [
            # Read-only display values
            dbc.Row(
                [
                    dbc.Col(_info_item("Project ID", project_id), md=6),
                    dbc.Col(
                        _info_item("Model ID", model_information.get("ID", "")),
                        md=6,
                    ),
                ],
                className="g-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        _info_item(
                            "Model UUID",
                            model_information.get("UUID", ""),
                            mono=True,
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        _info_item("Model DOI", model_information.get("doi", "")),
                        md=6,
                    ),
                ],
                className="g-3 mt-1",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        _info_item("Name", model_information.get("name", "")),
                        md=6,
                    ),
                    dbc.Col(
                        _info_item(
                            "Version", model_information.get("version", "")
                        ),
                        md=6,
                    ),
                ],
                className="g-3 mt-1",
            ),

            # Hidden inputs preserve the IDs that callbacks read with State()
            html.Div(
                [
                    dbc.Input(
                        id="projects-dropdown",
                        type="text",
                        value=project_id,
                        readonly=True,
                    ),
                    dbc.Input(
                        id="available-models-dropdown",
                        value=model_information.get("ID", ""),
                        readonly=True,
                    ),
                    dbc.Input(
                        id="edit_model_uuid",
                        type="text",
                        value=model_information.get("UUID", ""),
                        readonly=True,
                    ),
                    dbc.Input(
                        id="edit_model_doi",
                        type="text",
                        value=model_information.get("doi", ""),
                        readonly=True,
                    ),
                    dbc.Input(
                        id="edit_name",
                        type="text",
                        value=model_information.get("name", ""),
                        readonly=True,
                    ),
                    dbc.Input(
                        id="edit_model_version",
                        type="text",
                        value=model_information.get("version", ""),
                        readonly=True,
                    ),
                ],
                style={"display": "none"},
            ),

            html.Hr(className="my-4"),
            html.Div(
                [
                    dbc.Button(
                        [
                            html.I(className="bi bi-check2-circle me-1"),
                            "Continue",
                        ],
                        id="confirm-selection-btn",
                        color="success",
                    ),
                ],
                className="d-flex justify-content-end",
            ),
            dbc.Alert(
                "Project and model confirmed",
                id="selection-confirmed-alert",
                color="success",
                is_open=False,
                className="mt-3",
            ),
        ]
    )

    # -------- Right card: IBISBA hub information -----------------------------
    ibisba_body = dbc.Collapse(
        dbc.Form(
            [
                dbc.FormFloating(
                    [
                        dbc.Select(
                            id="model-project-id-ibisba",
                            options=[],
                            placeholder="Select a project in IBISBA hub",
                            required=True,
                        ),
                        dbc.Label("Project ID in IBISBA"),
                    ],
                    className="mb-3",
                ),
                dbc.FormFloating(
                    [
                        dbc.Input(
                            id="model-title",
                            type="text",
                            placeholder="Model title",
                            required=True,
                        ),
                        dbc.Label("Model title in FAIRDOM"),
                    ],
                    className="mb-3",
                ),
                html.Div(
                    [
                        dbc.Label(
                            "Model creators in IBISBA hub",
                            className="details-label mb-1",
                        ),
                        dcc.Dropdown(
                            id="model-creators",
                            options=[],
                            placeholder="Select one or more creators",
                            multi=True,
                            className="form-control p-0 border-0",
                        ),
                    ],
                    className="mb-3",
                ),
                html.Div(
                    [
                        dbc.Label(
                            "Model organisms in IBISBA hub",
                            className="details-label mb-1",
                        ),
                        dcc.Dropdown(
                            id="model-organisms",
                            options=[],
                            placeholder="Select one or more organisms",
                            value=[],
                            multi=True,
                            className="form-control p-0 border-0",
                        ),
                    ],
                    className="mb-3",
                ),
                html.Div(
                    [
                        dbc.Button(
                            [
                                html.I(className="bi bi-check2-circle me-1"),
                                "Continue",
                            ],
                            id="confirm-selection-ibisba-btn",
                            color="success",
                        ),
                    ],
                    className="d-flex justify-content-end",
                ),
                dbc.Alert(
                    "Project and model confirmed",
                    id="selection-confirmed-ibisba-alert",
                    color="success",
                    is_open=False,
                    className="mt-3",
                ),
            ]
        ),
        id="upload-form-collapse",
        is_open=False,
    )

    # -------- Action bar (push to IBISBA) ------------------------------------
    action_bar = dbc.Card(
        dbc.CardBody(
            dbc.Collapse(
                dbc.Form(
                    [
                        html.Div(
                            dbc.Button(
                                [
                                    html.I(className="bi bi-cloud-arrow-up me-1"),
                                    "Push model to IBISBA",
                                ],
                                id="upload-model-btn",
                                color="primary",
                            ),
                            className="text-center",
                        ),
                        html.Div(className="mt-4"),
                        html.Div(id="upload-status", className="text-start"),
                    ]
                ),
                id="boton-form-collapse",
                is_open=False,
            )
        ),
        className="shadow-sm border-0 details-action-bar",
    )

    # -------- Compose page ---------------------------------------------------
    return dbc.Container(
        [
            dcc.Store(id="metadata-yaml-path"),
            dcc.Store(id="model-file-name"),
            dcc.Store(id="model-file-path"),

            hero,

            dbc.Row(
                [
                    dbc.Col(
                        _section_card(
                            "Model Registry information",
                            "bi-database-fill",
                            registry_body,
                            header_image="/assets/logo.png",
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        _section_card(
                            "IBISBA Hub information",
                            "bi-cloud-fill",
                            ibisba_body,
                            header_image="/assets/icon-ibisba.jpeg",
                            header_color="#3f8814",
                        ),
                        md=6,
                    ),
                ],
                className="g-4",
            ),

            action_bar,

            # =========================
            # Modal confirmation
            # =========================
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(
                            "Confirm information for upload to the IBISBA Hub"
                        )
                    ),
                    dbc.ModalBody(id="confirm-upload-body"),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "Cancel",
                                id="cancel-upload-btn",
                                color="secondary",
                            ),
                            dbc.Button(
                                "Confirm upload",
                                id="confirm-upload-btn",
                                color="primary",
                            ),
                        ]
                    ),
                ],
                id="confirm-upload-modal",
                is_open=False,
            ),
        ],
        fluid=True,
        className="details-page p-4",
    )

