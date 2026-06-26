"""
Drift Detectors — registry page (under Models, below Dynamic Models).

CRUD over drift-detector PACKS (the versioned `stamm-drift-detectors` pip
package, shipped as a zip). The operator can ADD a pack (upload a slim
`drift_detectors/` archive), UPDATE it (re-upload the same name+version),
DELETE it, and ACTIVATE (pin/deploy) one pack per name.

Uploading a pack LISTS the detectors found inside it (read-only) — it does
NOT edit the drift_detectors catalog. The detector metadata is parsed and
stored on the pack row; "View detectors" shows that list per pack. The
Airflow DAG later runs the pinned pack. See [[project_drift_detector_packs]].

Component IDs are consumed by callbacks/callbacks_drift_detectors.py.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from model_registry.backend.utils.utils_sidebar import get_user_role


def _upload_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Add / update detector pack")),
            dbc.ModalBody(
                [
                    html.P(
                        "Upload a drift_detectors pack archive (.zip). The slim "
                        "drift_detectors/ package is enough — benchmarks, tests "
                        "and use-cases are ignored. The detectors inside are "
                        "listed (read-only) and stored with the pack. Uploading "
                        "the same name + version updates that pack.",
                        className="text-muted",
                        style={"fontSize": "0.85rem"},
                    ),
                    dcc.Upload(
                        id="dp-upload",
                        children=html.Div(
                            ["Drag & drop or ", html.A("select a .zip file")]
                        ),
                        accept=".zip",
                        multiple=False,
                        className="dp-upload-box",
                        style={
                            "width": "100%",
                            "height": "90px",
                            "lineHeight": "90px",
                            "borderWidth": "1px",
                            "borderStyle": "dashed",
                            "borderRadius": "8px",
                            "textAlign": "center",
                            "marginBottom": "1rem",
                        },
                    ),
                    html.Div(
                        id="dp-upload-filename",
                        className="text-success mb-2",
                        style={"fontSize": "0.85rem"},
                    ),
                    dbc.Label("Pack name (optional)"),
                    dbc.Input(
                        id="dp-upload-name",
                        placeholder="stamm-drift-detectors",
                        className="mb-2",
                    ),
                    dbc.Label("Notes (optional)"),
                    dbc.Textarea(
                        id="dp-upload-notes",
                        placeholder="release notes…",
                        className="mb-2",
                    ),
                    dbc.Checkbox(
                        id="dp-upload-activate",
                        label="Activate (deploy) this pack after adding",
                        value=False,
                        className="mb-2",
                    ),
                    html.Div(id="dp-upload-feedback"),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Cancel", id="dp-upload-cancel", color="secondary", outline=True
                    ),
                    dbc.Button("Upload", id="dp-upload-submit", color="primary"),
                ]
            ),
        ],
        id="dp-upload-modal",
        is_open=False,
        size="lg",
    )


def _detectors_modal():
    """Read-only listing of the detectors inside a selected pack."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(id="dp-detectors-title")),
            dbc.ModalBody(
                html.Div(id="dp-detectors-body"),
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Close", id="dp-detectors-close", color="secondary", outline=True
                ),
            ),
        ],
        id="dp-detectors-modal",
        is_open=False,
        size="lg",
        scrollable=True,
    )


def drift_detectors_layout(session_data=None):
    role, _ = get_user_role(session_data)
    if not session_data or not session_data.get("authenticated"):
        return dbc.Container(
            [
                html.H3("Access Denied", className="text-danger mt-4"),
                html.P("Please sign in to manage drift detectors."),
            ]
        )

    header = html.Div(
        [
            html.Div(
                [
                    html.H2("Drift Detectors"),
                    html.Div(
                        "Manage drift-detector packs (versioned .zip packages). "
                        "Add, update, delete or deploy a pack; open one to view "
                        "the detectors it ships.",
                        className="page-sub",
                    ),
                ]
            ),
            html.Div(
                dbc.Button(
                    [html.I(className="bi bi-upload me-2"), "Add pack"],
                    id="btn-open-dp-upload",
                    color="primary",
                ),
                className="ms-auto",
            ),
        ],
        className="d-flex align-items-start mb-3",
    )

    packs_section = html.Div(
        [
            html.H4("Detector packs", className="mt-2"),
            dcc.Loading(html.Div(id="dp-packs-table"), type="default"),
        ],
        className="mb-4",
    )

    return dbc.Container(
        [
            dcc.Store(id="dp-refresh-trigger", data=0),
            # Holds the currently-rendered packs so "View detectors" can read the
            # detector list without an extra round-trip.
            dcc.Store(id="dp-packs-store", data=[]),
            dbc.Toast(
                id="dp-toast",
                header="Drift detectors",
                is_open=False,
                dismissable=True,
                duration=4000,
                icon="primary",
                style={"position": "fixed", "top": 20, "right": 20, "zIndex": 1999},
            ),
            header,
            packs_section,
            _upload_modal(),
            _detectors_modal(),
        ],
        fluid=True,
        className="content-page",
    )
