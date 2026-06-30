"""Presentation helpers for XAI explainability sections.

Keeps Dash view composition out of the page entrypoint while delegating
chart generation to utils_model_explainability.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html

from model_registry.backend.utils import utils_model_explainability as xai_utils


def live_badge(ok):
    if ok:
        return dbc.Badge(
            [html.I(className="bi bi-broadcast me-1"), "live · sklearn"],
            color="success",
            className="mb-2",
        )
    return dbc.Badge("illustrative placeholder", color="secondary", className="mb-2")


def graph_component(fig, gid=None):
    kw = dict(figure=fig, config={"displayModeBar": False})
    if gid:
        kw["id"] = gid
    return dcc.Graph(**kw)


_PANEL_HELP = {
    "Global feature importance": "Ranks inputs by how much the model's accuracy drops when that input is "
    "randomly shuffled — a longer bar means the model leans on it more. Needs "
    "labelled data: upload a CSV that includes the target column to compute it.",
    "SHAP summary": "Each dot is one sample. Left/right shows whether that feature pushed the "
    "prediction down/up; colour shows whether the feature's value was low (blue) "
    "or high (red). Features are ordered top-to-bottom by overall impact.",
    "Partial dependence": "How the predicted output changes as ONE feature varies, averaging over all "
    "the others. An upward slope means higher feature values give higher "
    "predictions. Pick a feature in the dropdown.",
    "Local explanation": "Explains ONE prediction: each bar is how much a feature pushed it above "
    "(blue) or below (red) the average. The bars add up from the baseline "
    "E[f(x)] to the final prediction. Pick an instance in the dropdown.",
    "Impurity-based importance": "How much each feature reduced error across the tree's splits, read straight "
    "from the trained model. Fast and exact, but can over-credit features with "
    "many distinct values — cross-check against the SHAP summary.",
    "Feature interactions": "How strongly pairs of features combine beyond their individual effects. "
    "Darker cells mean a stronger interaction.",
    "Decision structure": "A representative path through the tree: each split node tests "
    "'feature ≤ threshold', leaves show the predicted value. For a forest this "
    "is ONE example tree (the first), not the whole ensemble's combined logic.",
    "Decision rules": "The same tree written as IF/THEN rules (scikit-learn's export_text), "
    "truncated to depth 3. For an ensemble it's one representative tree.",
    "Model coefficients": "The weight the linear model gives each feature. Positive (blue) raises the "
    "prediction, negative (red) lowers it; larger magnitude = stronger effect. "
    "Most comparable when the inputs are on similar scales.",
    "ARD relevance / kernel weighting": "Inverse length-scales: a higher value means the model treats that feature "
    "as more relevant to the prediction.",
    "Predictive uncertainty": "The shaded band is the model's confidence around its prediction — wider "
    "means less certain.",
    "Temporal saliency": "For sequence models: how sensitive the prediction is to each feature at "
    "each time step. Brighter = more influential at that point in the window.",
    "Integrated gradients": "Attributes the prediction to each feature relative to a baseline input — "
    "bars to the right increased the output, to the left decreased it.",
    "Attention map": "Which time steps the model paid attention to when predicting; brighter "
    "cells are the steps it weighted most.",
    "Step attribution": "How much each feature contributed to this prediction.",
    "Component loadings": "How much each original feature contributes to each component / cluster — "
    "the recipe of each component.",
    "Explained variance": "How much of the data's total variation each component captures; the line "
    "is the running cumulative share.",
}


def _slug(text):
    return "".join(c.lower() if c.isalnum() else "-" for c in str(text)).strip("-")


def panel(title, body, subtitle=None, tag=None, help_text=None):
    resolved_help = help_text or _PANEL_HELP.get(title)
    header = [html.Span(title, className="fw-semibold")]
    if resolved_help:
        hid = "xai-help-" + _slug(title)
        header.append(
            html.I(
                className="bi bi-question-circle text-muted ms-2",
                id=hid,
                style={"cursor": "pointer", "fontSize": "0.9rem"},
                title="How to read this chart",
            )
        )
        header.append(
            dbc.Popover(
                dbc.PopoverBody(resolved_help, className="small"),
                target=hid,
                trigger="hover focus",
                placement="top",
            )
        )
    if tag:
        header.append(
            dbc.Badge(tag, color="light", text_color="secondary", className="ms-2 border")
        )
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(header, className="d-flex align-items-center mb-1"),
                html.Div(subtitle, className="text-muted small mb-2") if subtitle else None,
                body,
            ]
        ),
        className="shadow-sm h-100",
    )


def _tree_family(profile, live, features, seed_key):
    ok = bool(live and live.get("ok"))

    if ok and live.get("importances"):
        imp_fig = xai_utils.build_importance_fig_real(live["importances"])
        imp_sub = f"From {live.get('model_class', 'model')}.feature_importances_ — real, read from the artifact."
    else:
        imp_fig = xai_utils.build_importance_fig(features, seed_key, "Impurity")
        imp_sub = "Gini / variance reduction (placeholder — artifact not loadable here)."

    tree_fig = (
        xai_utils.build_tree_fig_real(live["subtree"])
        if ok and live.get("subtree")
        else xai_utils.build_tree_fig(features, seed_key)
    )
    rules_body = (
        xai_utils.build_rule_list_real(live["rules_text"])
        if ok and live.get("rules_text")
        else xai_utils.build_rule_list(features, seed_key)
    )
    rules_sub = (
        "The model's actual learned rules (sklearn export_text)."
        if ok and live.get("rules_text")
        else "Illustrative rules (placeholder)."
    )

    rows = [
        dbc.Row(
            [
                dbc.Col(
                    panel(
                        "Impurity-based importance",
                        graph_component(imp_fig),
                        imp_sub,
                        tag=(live.get("model_class") if ok else None),
                    ),
                    lg=12,
                )
            ],
            className="g-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    panel("Decision structure", graph_component(tree_fig), "A representative decision path."),
                    lg=6,
                ),
                dbc.Col(panel("Decision rules", rules_body, rules_sub), lg=6),
            ],
            className="g-3 mt-1",
        ),
    ]
    if profile == "tree_ensemble":
        rows.append(
            dbc.Row(
                [
                    dbc.Col(
                        panel(
                            "Feature interactions",
                            graph_component(xai_utils.build_interaction_heatmap(features, seed_key)),
                            "Pairwise interaction strength (placeholder — needs a dataset).",
                        ),
                        lg=12,
                    )
                ],
                className="g-3 mt-1",
            )
        )
    return html.Div([live_badge(ok)] + rows)


def family_section(profile, features, outputs, seed_key, live=None):
    if profile in ("tree_single", "tree_ensemble"):
        return _tree_family(profile, live, features, seed_key)
    if profile == "linear":
        live_ok = bool(live and live.get("ok") and live.get("coef"))
        if live_ok:
            coef_fig = xai_utils.build_coef_fig_real(live["coef"])
            sub = f"Real coefficients from {live.get('model_class', 'model')}.coef_" + (
                f" (intercept {live['intercept']:.3f})"
                if live.get("intercept") is not None
                else ""
            )
        else:
            coef_fig = xai_utils.build_coef_fig(features, seed_key)
            sub = "Sign + magnitude of each weight (placeholder)."
        return html.Div(
            [
                live_badge(live_ok),
                dbc.Row(
                    [dbc.Col(panel("Model coefficients", graph_component(coef_fig), sub), lg=12)],
                    className="g-3",
                ),
            ]
        )
    if profile == "kernel":
        return dbc.Row(
            [
                dbc.Col(
                    panel(
                        "ARD relevance / kernel weighting",
                        graph_component(xai_utils.build_ard_fig(features, seed_key)),
                        "Inverse length-scales — higher = more relevant.",
                    ),
                    lg=6,
                ),
                dbc.Col(
                    panel(
                        "Predictive uncertainty",
                        graph_component(xai_utils.build_uncertainty_fig(seed_key)),
                        "Confidence band around predictions.",
                    ),
                    lg=6,
                ),
            ],
            className="g-3",
        )
    if profile == "neural_seq":
        return dbc.Row(
            [
                dbc.Col(
                    panel(
                        "Temporal saliency",
                        graph_component(xai_utils.build_temporal_saliency(features, seed_key)),
                        "Gradient magnitude over the input window.",
                    ),
                    lg=7,
                ),
                dbc.Col(
                    panel(
                        "Integrated gradients",
                        graph_component(xai_utils.build_integrated_gradients(features, seed_key)),
                        "Attribution vs. a baseline input.",
                    ),
                    lg=5,
                ),
            ],
            className="g-3",
        )
    if profile == "attention":
        return dbc.Row(
            [
                dbc.Col(
                    panel(
                        "Attention map",
                        graph_component(xai_utils.build_attention_fig(features, seed_key)),
                        "Which steps the model attends to.",
                    ),
                    lg=7,
                ),
                dbc.Col(
                    panel(
                        "Step attribution",
                        graph_component(xai_utils.build_integrated_gradients(features, seed_key)),
                        "Per-feature attribution.",
                    ),
                    lg=5,
                ),
            ],
            className="g-3",
        )
    if profile == "unsupervised":
        return dbc.Row(
            [
                dbc.Col(
                    panel(
                        "Component loadings",
                        graph_component(xai_utils.build_pca_loadings(features, seed_key)),
                        "Feature contribution to each component / cluster.",
                    ),
                    lg=6,
                ),
                dbc.Col(
                    panel(
                        "Explained variance",
                        graph_component(xai_utils.build_variance_fig(seed_key)),
                        "How much structure each component captures.",
                    ),
                    lg=6,
                ),
            ],
            className="g-3",
        )
    return dbc.Alert(
        "No interpretable internals are exposed for this algorithm family. "
        "Only the model-agnostic methods above apply.",
        color="light",
        className="border",
    )


def core_section(features, outputs, seed_key, supervised, live=None):
    if not supervised:
        return dbc.Alert(
            "This is an unsupervised model — target-based attributions "
            "(SHAP, partial dependence) do not apply. See the structural "
            "explanations below.",
            color="light",
            className="border",
        )

    ok = bool(live and live.get("ok"))
    bg = (live or {}).get("background", "")
    feat_opts = [{"label": f, "value": f} for f in features]
    f0 = features[0] if features else None

    if ok and live.get("shap_summary"):
        shap_fig = xai_utils.build_shap_summary_fig_real(live["shap_summary"])
        shap_sub = f"Real SHAP values ({live.get('model_class', 'model')}); {bg}."
        shap_tag = "live · shap"
    else:
        shap_fig = xai_utils.build_shap_summary_fig(features, seed_key)
        shap_sub = "Per-sample SHAP values; colour = feature value (placeholder)."
        shap_tag = "placeholder"

    perm = (live or {}).get("perm_importance")
    if ok and perm:
        imp_fig = xai_utils.build_importance_fig_real(
            perm, xtitle="permutation importance (mean score drop)"
        )
        imp_sub = f"Permutation importance on {bg}."
        imp_tag = "live · sklearn"
    else:
        imp_fig = xai_utils.build_importance_fig(features, seed_key)
        imp_sub = "Permutation importance needs labels — upload data with a target column to compute it."
        imp_tag = "placeholder"
    imp_panel = panel(
        "Global feature importance", graph_component(imp_fig), imp_sub, tag=imp_tag
    )

    row1 = dbc.Row(
        [
            dbc.Col(imp_panel, lg=6),
            dbc.Col(panel("SHAP summary", graph_component(shap_fig), shap_sub, tag=shap_tag), lg=6),
        ],
        className="g-3",
    )

    pdp = (live or {}).get("pdp") or {}
    if ok and f0 in pdp:
        pdp_fig = xai_utils.build_pdp_fig_real(f0, pdp[f0]["x"], pdp[f0]["y"])
    else:
        pdp_fig = xai_utils.build_pdp_fig(f0 or "feature", seed_key)
    pdp_tag = "live · sklearn" if (ok and pdp) else "placeholder"

    inst = (live or {}).get("shap_instances") or {}
    if ok and "1" in inst:
        d = inst["1"]
        local_fig = xai_utils.build_local_waterfall_fig_real(
            d["pairs"],
            d.get("base", 0.0),
            d.get("pred", 0.0),
            (outputs or ["output"])[0],
        )
    else:
        local_fig = xai_utils.build_local_waterfall_fig(features, outputs, seed_key, 1)
    local_tag = "live · shap" if (ok and inst) else "placeholder"

    row2 = dbc.Row(
        [
            dbc.Col(
                panel(
                    "Partial dependence",
                    html.Div(
                        [
                            dcc.Dropdown(
                                id="xai-pdp-feature",
                                options=feat_opts,
                                value=f0,
                                clearable=False,
                                className="mb-2",
                            ),
                            graph_component(pdp_fig, gid="xai-pdp-graph"),
                        ]
                    ),
                    "Average model response as one feature varies.",
                    tag=pdp_tag,
                ),
                lg=6,
            ),
            dbc.Col(
                panel(
                    "Local explanation",
                    html.Div(
                        [
                            dcc.Dropdown(
                                id="xai-instance-select",
                                options=[
                                    {"label": f"Instance #{i}", "value": i}
                                    for i in range(1, 9)
                                ],
                                value=1,
                                clearable=False,
                                className="mb-2",
                            ),
                            graph_component(local_fig, gid="xai-local-graph"),
                        ]
                    ),
                    "Why the model made one specific prediction.",
                    tag=local_tag,
                ),
                lg=6,
            ),
        ],
        className="g-3 mt-1",
    )
    return html.Div([row1, row2])
