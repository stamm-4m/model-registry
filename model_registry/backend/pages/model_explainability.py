"""Model Explainability (XAI) detail view.

Opened from the "XAI" magnifying-glass column in the models grid
(/model-explainability/<project_id>/<model_id>). Gives a per-model,
explainability-first view of a single model.

DESIGN — HYBRID (Camilo, 2026-06-24):
  * A model-agnostic CORE that is ALWAYS shown (global importance, SHAP
    summary, partial dependence, local instance explanation).
  * A FAMILY-SPECIFIC section that SWAPS based on the model's `algorithm`
    family (trees -> structure + decision path; linear -> coefficients;
    kernel -> support vectors / ARD relevance; sequence nets -> temporal
    saliency; transformer -> attention; unsupervised -> loadings/clusters).

The figures here are ILLUSTRATIVE PLACEHOLDERS driven by the model's REAL
metadata (feature names, outputs, algorithm, hyper-parameters). They are
seeded deterministically per-model so they are stable between reloads.
Swapping to real explanations is a matter of replacing the `build_*`
figure helpers with ones that load the artifact and run SHAP / permutation
importance on a held-out dataset — the layout and wiring stay the same.

Component IDs are consumed by callbacks/callbacks_model_explainability.py.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html

from model_registry.backend.utils import utils_model_explainability_sections as xai_sections

# Reuse the loaders/normalisers the model form already uses so we read the
# exact same row + tolerate both the object and flat-list IO shapes.
try:
    from model_registry.backend.pages.model_upload import _fetch_model_row, _io_items
except Exception:  # pragma: no cover - defensive

    def _fetch_model_row(slug, session_data):
        return {}

    def _io_items(value):
        if isinstance(value, list):
            return value
        return []


# ---------------------------------------------------------------------------
# Algorithm family -> XAI profile
# ---------------------------------------------------------------------------
# Profiles drive the family-specific section. Keys mirror STAMM_ALGORITHMS
# (utils/utils_template_ui.py).
_PROFILE_OF = {
    "decision_tree": "tree_single",
    "m5": "tree_single",
    "cubist": "tree_single",
    "random_forest": "tree_ensemble",
    "gradient_boosting": "tree_ensemble",
    "ensemble": "tree_ensemble",
    "linear_regression": "linear",
    "logistic_regression": "linear",
    "pls": "linear",
    "svm": "kernel",
    "gaussian_process": "kernel",
    "neural_network": "neural_seq",
    "rnn": "neural_seq",
    "cnn": "neural_seq",
    "transformer": "attention",
    "pca": "unsupervised",
    "kmeans": "unsupervised",
    "custom": "generic",
}

_FAMILY_LABEL = {
    "decision_tree": "Decision Tree",
    "random_forest": "Random Forest",
    "gradient_boosting": "Gradient Boosting",
    "ensemble": "Ensemble",
    "svm": "Support Vector Machine",
    "linear_regression": "Linear Regression",
    "logistic_regression": "Logistic Regression",
    "neural_network": "Neural Network",
    "rnn": "Recurrent Neural Network",
    "cnn": "Convolutional Neural Network",
    "transformer": "Transformer",
    "gaussian_process": "Gaussian Process",
    "pls": "Partial Least Squares",
    "pca": "Principal Component Analysis",
    "kmeans": "K-Means Clustering",
    "cubist": "Cubist (rule-based)",
    "m5": "M5 Model Tree",
    "custom": "Custom / Other",
}

# Human description of the methods each family unlocks (shown in the header).
_METHODS_FOR = {
    "tree_single": [
        "Tree structure",
        "Decision path",
        "Impurity importance",
        "Rule list",
    ],
    "tree_ensemble": [
        "Impurity importance",
        "Feature interactions",
        "Tree-SHAP",
        "Representative tree",
    ],
    "linear": ["Signed coefficients", "Standardised weights", "Intercept / bias"],
    "kernel": ["Support-vector profile", "ARD relevance", "Predictive uncertainty"],
    "neural_seq": ["Temporal saliency", "Integrated gradients", "Sequence attribution"],
    "attention": ["Attention maps", "Token / step attribution"],
    "unsupervised": ["Component loadings", "Explained variance", "Cluster profiles"],
    "generic": ["Model-agnostic only"],
}

_CORE_METHODS = [
    "Permutation importance",
    "SHAP summary",
    "Partial dependence",
    "Local SHAP",
]


def _feature_list(row) -> list[str]:
    feats = []
    for it in _io_items(row.get("inputs")):
        if isinstance(it, dict) and it.get("name"):
            feats.append(str(it["name"]))
        elif isinstance(it, str):
            feats.append(it)
    return feats or [f"feature_{i + 1}" for i in range(6)]


def _output_list(row) -> list[str]:
    outs = []
    for it in _io_items(row.get("outputs")):
        if isinstance(it, dict) and it.get("name"):
            outs.append(str(it["name"]))
        elif isinstance(it, str):
            outs.append(it)
    return outs or ["target"]


def _data_upload_card(features, outputs, supervised):
    """Upload a CSV to recompute the data-backed panels on YOUR data instead of
    the sampled background. Columns must match the model's stored input names;
    an optional target column (the model's output name) unlocks permutation
    importance."""
    if not supervised:
        return None
    out = ", ".join(outputs) if outputs else "—"
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.I(className="bi bi-upload me-2"),
                        html.Span("Test with your own data", className="fw-semibold"),
                    ],
                    className="mb-1",
                ),
                html.Div(
                    [
                        "Upload a CSV to recompute SHAP and partial dependence on your data "
                        "(and permutation importance if the target column is present). Input "
                        "columns must match the model's stored feature names: ",
                        html.Code(", ".join(features) or "—"),
                        ". Optional target column: ",
                        html.Code(out),
                        ".",
                    ],
                    className="text-muted small mb-2",
                ),
                dcc.Upload(
                    id="xai-data-upload",
                    children=html.Div(
                        ["Drag & drop or ", html.A("select a .csv file")]
                    ),
                    accept=".csv",
                    multiple=False,
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "8px",
                        "textAlign": "center",
                    },
                ),
                html.Div(id="xai-data-status", className="small mt-2"),
            ]
        ),
        className="shadow-sm mb-3",
    )




def _method_chips(methods, color):
    return html.Div([dbc.Badge(m, color=color, className="me-1 mb-1") for m in methods])


def _missing_model_view():
    return html.Div(
        [
            dbc.Alert(
                [
                    html.H5("No model selected", className="alert-heading"),
                    html.P(
                        "Open this view from the magnifying-glass (XAI) icon next to a "
                        "model in the registry to explore its explanations."
                    ),
                ],
                color="secondary",
            ),
        ],
        style={"padding": "20px"},
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def model_explainability_layout(project_id=None, model_id=None, session_data=None):
    """XAI detail view for one model.

    Back-compatible: called with no args (legacy /model-explainability link)
    it renders a 'select a model' prompt.
    """
    if not (project_id and model_id):
        return _missing_model_view()

    row = _fetch_model_row(model_id, session_data) if session_data else {}
    model_name = row.get("model_name") or row.get("slug") or model_id
    algorithm = (row.get("algorithm") or "").strip()
    profile = _PROFILE_OF.get(algorithm, "generic")
    family_label = _FAMILY_LABEL.get(algorithm, algorithm or "Unknown family")
    model_type = row.get("model_type") or (
        "interpretable" if profile in ("tree_single", "linear") else "—"
    )
    version = row.get("version") or "—"
    status = row.get("status") or "—"
    authors = row.get("authors") or row.get("learner") or "—"
    features = _feature_list(row)
    outputs = _output_list(row)
    supervised = profile != "unsupervised"
    seed_key = model_id

    live = None
    try:
        from model_registry.backend.services import xai_service

        live = xai_service.explain(
            project_id, model_id, family=profile, session_data=session_data
        )
    except Exception as exc:  # never let explainer issues break the page
        __import__("logging").getLogger(__name__).info(
            "xai_service unavailable: %s", exc
        )
        live = None

    type_color = {"interpretable": "success", "black_box": "dark"}.get(
        model_type, "secondary"
    )

    header = dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.H4(
                                            model_name, className="d-inline mb-0 me-2"
                                        ),
                                        dbc.Badge(
                                            family_label,
                                            color="primary",
                                            className="me-1",
                                        ),
                                        dbc.Badge(
                                            model_type,
                                            color=type_color,
                                            className="me-1",
                                        ),
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.Span(
                                            f"v{version}",
                                            className="text-muted small me-3",
                                        ),
                                        html.Span(
                                            f"status: {status}",
                                            className="text-muted small me-3",
                                        ),
                                        html.Span(
                                            f"author: {authors}",
                                            className="text-muted small me-3",
                                        ),
                                        html.Span(
                                            f"{len(features)} inputs → {len(outputs)} output(s)",
                                            className="text-muted small",
                                        ),
                                    ],
                                    className="mt-1",
                                ),
                            ],
                            md=7,
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    "Applicable methods",
                                    className="small text-uppercase text-muted mb-1",
                                ),
                                _method_chips(_CORE_METHODS, "info"),
                                html.Div(className="mt-1"),
                                _method_chips(_METHODS_FOR.get(profile, []), "primary"),
                            ],
                            md=5,
                        ),
                    ]
                ),
            ]
        ),
        className="shadow-sm mb-3",
    )

    caps = (live or {}).get("capabilities") or []
    live_ok = bool(live and live.get("ok") and caps)
    if live_ok:
        _cap_labels = {
            "impurity": "impurity importance",
            "rules": "decision rules",
            "tree": "tree structure",
            "coef": "coefficients",
            "pdp": "partial dependence",
            "shap": "SHAP",
        }
        shown = ", ".join(_cap_labels.get(c, c) for c in caps)
        note = dbc.Alert(
            [
                html.I(className="bi bi-broadcast me-2"),
                html.Span(
                    f"LIVE via scikit-learn on the {live.get('model_class', 'model')} "
                    f"artifact: {shown}. "
                ),
                html.Span(
                    "SHAP / partial dependence are evaluated over a background sampled "
                    "from each feature's declared operating range; permutation importance "
                    "stays a placeholder (no labelled dataset shipped).",
                    className="text-muted",
                ),
            ],
            color="success",
            className="py-2 small",
        )
    else:
        note = dbc.Alert(
            [
                html.I(className="bi bi-info-circle me-2"),
                "Prototype — illustrative placeholders from the model's metadata. The artifact "
                "could not be explained as an sklearn model here (R / keras models, or "
                "scikit-learn / shap unavailable in this environment).",
            ],
            color="warning",
            className="py-2 small",
        )

    store = dcc.Store(
        id="xai-model-store",
        data={
            "model_id": model_id,
            "project_id": project_id,
            "seed_key": seed_key,
            "features": features,
            "outputs": outputs,
            "profile": profile,
            "pdp": (live or {}).get("pdp"),
            "shap_instances": (live or {}).get("shap_instances"),
            "supervised": supervised,
        },
    )

    return html.Div(
        [
            store,
            dbc.Row(
                [
                    dbc.Col(
                        html.A(
                            [
                                html.I(className="bi bi-arrow-left me-1"),
                                "Back to models",
                            ],
                            href="/",
                            className="text-decoration-none small",
                        ),
                        width="auto",
                    ),
                ],
                className="mb-2",
            ),
            header,
            note,
            _data_upload_card(features, outputs, supervised),
            html.H5("Model-agnostic explanations", className="mb-2"),
            html.Div(
                xai_sections.core_section(features, outputs, seed_key, supervised, live),
                id="xai-core-container",
            ),
            html.Hr(className="my-4"),
            html.H5(
                [
                    "Family-specific — ",
                    html.Span(family_label, className="text-primary"),
                ],
                className="mb-2",
            ),
            xai_sections.family_section(profile, features, outputs, seed_key, live),
            html.Div(style={"height": "30px"}),
        ],
        style={"padding": "20px"},
    )
