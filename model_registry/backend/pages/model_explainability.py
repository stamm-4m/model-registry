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

import hashlib
import math
import random
from typing import List

import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go

from model_registry.backend.components.top_toolbar import top_toolbar

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
    "decision_tree":       "tree_single",
    "m5":                  "tree_single",
    "cubist":              "tree_single",
    "random_forest":       "tree_ensemble",
    "gradient_boosting":   "tree_ensemble",
    "ensemble":            "tree_ensemble",
    "linear_regression":   "linear",
    "logistic_regression": "linear",
    "pls":                 "linear",
    "svm":                 "kernel",
    "gaussian_process":    "kernel",
    "neural_network":      "neural_seq",
    "rnn":                 "neural_seq",
    "cnn":                 "neural_seq",
    "transformer":         "attention",
    "pca":                 "unsupervised",
    "kmeans":              "unsupervised",
    "custom":              "generic",
}

_FAMILY_LABEL = {
    "decision_tree": "Decision Tree", "random_forest": "Random Forest",
    "gradient_boosting": "Gradient Boosting", "ensemble": "Ensemble",
    "svm": "Support Vector Machine", "linear_regression": "Linear Regression",
    "logistic_regression": "Logistic Regression", "neural_network": "Neural Network",
    "rnn": "Recurrent Neural Network", "cnn": "Convolutional Neural Network",
    "transformer": "Transformer", "gaussian_process": "Gaussian Process",
    "pls": "Partial Least Squares", "pca": "Principal Component Analysis",
    "kmeans": "K-Means Clustering", "cubist": "Cubist (rule-based)",
    "m5": "M5 Model Tree", "custom": "Custom / Other",
}

# Human description of the methods each family unlocks (shown in the header).
_METHODS_FOR = {
    "tree_single":   ["Tree structure", "Decision path", "Impurity importance", "Rule list"],
    "tree_ensemble": ["Impurity importance", "Feature interactions", "Tree-SHAP", "Representative tree"],
    "linear":        ["Signed coefficients", "Standardised weights", "Intercept / bias"],
    "kernel":        ["Support-vector profile", "ARD relevance", "Predictive uncertainty"],
    "neural_seq":    ["Temporal saliency", "Integrated gradients", "Sequence attribution"],
    "attention":     ["Attention maps", "Token / step attribution"],
    "unsupervised":  ["Component loadings", "Explained variance", "Cluster profiles"],
    "generic":       ["Model-agnostic only"],
}

_CORE_METHODS = ["Permutation importance", "SHAP summary", "Partial dependence", "Local SHAP"]

PRIMARY = "#2c7be5"
ACCENT = "#00b894"
WARN = "#e17055"
MUTED = "#6c757d"


# ---------------------------------------------------------------------------
# Deterministic pseudo-data helpers (placeholder figures from real metadata)
# ---------------------------------------------------------------------------
def _seed(*parts) -> int:
    h = hashlib.md5("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(h[:8], 16)


def _rng(*parts) -> random.Random:
    return random.Random(_seed(*parts))


def _feature_list(row) -> List[str]:
    feats = []
    for it in _io_items(row.get("inputs")):
        if isinstance(it, dict) and it.get("name"):
            feats.append(str(it["name"]))
        elif isinstance(it, str):
            feats.append(it)
    return feats or [f"feature_{i+1}" for i in range(6)]


def _output_list(row) -> List[str]:
    outs = []
    for it in _io_items(row.get("outputs")):
        if isinstance(it, dict) and it.get("name"):
            outs.append(str(it["name"]))
        elif isinstance(it, str):
            outs.append(it)
    return outs or ["target"]


def _base_layout(fig, height=320, title=None):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=10, r=10, t=40 if title else 12, b=10),
        title=dict(text=title, font=dict(size=14)) if title else None,
        font=dict(size=12),
        showlegend=False,
    )
    return fig


# ---- shared / core figures -------------------------------------------------
def build_importance_fig(features, seed_key, method="Permutation"):
    rng = _rng(seed_key, method)
    vals = sorted([rng.uniform(0.02, 1.0) for _ in features])
    feats = [f for _, f in sorted(zip(vals, features))]
    vals = sorted(vals)
    fig = go.Figure(go.Bar(
        x=vals, y=feats, orientation="h",
        marker=dict(color=vals, colorscale="Blues", cmin=0, cmax=1),
        hovertemplate="%{y}: %{x:.3f}<extra></extra>",
    ))
    fig.update_xaxes(title=f"{method} importance (Δ score)")
    return _base_layout(fig, height=max(260, 26 * len(features)))


def build_shap_summary_fig(features, seed_key):
    """Beeswarm-style SHAP summary (jittered points coloured by feature value)."""
    rng = _rng(seed_key, "shap")
    order = sorted(features, key=lambda f: rng.random())
    fig = go.Figure()
    for i, f in enumerate(order):
        n = 40
        spread = rng.uniform(0.15, 0.9)
        xs = [rng.gauss(0, spread) for _ in range(n)]
        cols = [(x - min(xs)) / (max(xs) - min(xs) + 1e-9) for x in xs]
        ys = [i + rng.uniform(-0.18, 0.18) for _ in range(n)]
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="markers",
            marker=dict(size=6, color=cols, colorscale="RdBu", reversescale=True,
                        showscale=(i == 0),
                        colorbar=dict(title="feat.<br>value", thickness=10) if i == 0 else None),
            hoverinfo="skip",
        ))
    fig.update_yaxes(tickmode="array", tickvals=list(range(len(order))), ticktext=order)
    fig.update_xaxes(title="SHAP value (impact on output)")
    fig.add_vline(x=0, line_width=1, line_color=MUTED)
    return _base_layout(fig, height=max(260, 26 * len(features)))


def build_pdp_fig(feature, seed_key):
    rng = _rng(seed_key, "pdp", feature)
    xs = [i / 30 for i in range(31)]
    base = rng.uniform(-1, 1)
    slope = rng.uniform(-2, 2)
    curv = rng.uniform(-3, 3)
    mean = [base + slope * x + curv * (x - 0.5) ** 2 for x in xs]
    band = rng.uniform(0.1, 0.4)
    upper = [m + band for m in mean]
    lower = [m - band for m in mean]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs + xs[::-1], y=upper + lower[::-1], fill="toself",
                             fillcolor="rgba(44,123,229,0.12)", line=dict(width=0),
                             hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=xs, y=mean, mode="lines", line=dict(color=PRIMARY, width=3),
                             hovertemplate=f"{feature}=%{{x:.2f}} → %{{y:.2f}}<extra></extra>"))
    fig.update_xaxes(title=f"{feature} (normalised)")
    fig.update_yaxes(title="Partial dependence")
    return _base_layout(fig, height=320, title=None)


def build_local_waterfall_fig(features, outputs, seed_key, instance):
    rng = _rng(seed_key, "local", instance)
    top = features[:8]
    contribs = [rng.uniform(-1, 1) for _ in top]
    base_val = rng.uniform(0.2, 0.8)
    order = sorted(range(len(top)), key=lambda i: -abs(contribs[i]))
    top = [top[i] for i in order]
    contribs = [round(contribs[i], 3) for i in order]
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative"] * len(top),
        x=top, y=contribs,
        connector=dict(line=dict(color=MUTED)),
        increasing=dict(marker=dict(color=PRIMARY)),
        decreasing=dict(marker=dict(color=WARN)),
    ))
    out = outputs[0] if outputs else "output"
    fig.update_yaxes(title=f"contribution to {out}")
    fig.update_xaxes(tickangle=-30)
    return _base_layout(fig, height=340,
                        title=f"E[f(x)]={base_val:.2f} → prediction for instance {instance}")


# ---- family-specific figures ----------------------------------------------
def build_coef_fig(features, seed_key):
    rng = _rng(seed_key, "coef")
    vals = [rng.uniform(-1.5, 1.5) for _ in features]
    pairs = sorted(zip(vals, features), key=lambda p: p[0])
    vals = [p[0] for p in pairs]
    feats = [p[1] for p in pairs]
    colors = [PRIMARY if v >= 0 else WARN for v in vals]
    fig = go.Figure(go.Bar(x=vals, y=feats, orientation="h", marker_color=colors,
                           hovertemplate="%{y}: %{x:.3f}<extra></extra>"))
    fig.add_vline(x=0, line_width=1, line_color=MUTED)
    fig.update_xaxes(title="standardised coefficient (β)")
    return _base_layout(fig, height=max(260, 26 * len(features)))


def build_interaction_heatmap(features, seed_key):
    rng = _rng(seed_key, "interact")
    f = features[:8]
    n = len(f)
    z = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            v = 0 if i == j else round(rng.uniform(0, 1), 2)
            z[i][j] = z[j][i] = v
    fig = go.Figure(go.Heatmap(z=z, x=f, y=f, colorscale="Purples",
                               hovertemplate="%{y} × %{x}: %{z:.2f}<extra></extra>"))
    fig.update_xaxes(tickangle=-30)
    return _base_layout(fig, height=360, title="Feature interaction strength (Friedman's H)")


def build_tree_fig(features, seed_key):
    """Small illustrative decision tree (node-link)."""
    rng = _rng(seed_key, "tree")
    f = features or ["feature"]
    # positions for a depth-2 tree
    nodes = {
        "n0": (0.5, 1.0), "n1": (0.25, 0.55), "n2": (0.75, 0.55),
        "l1": (0.12, 0.1), "l2": (0.38, 0.1), "l3": (0.62, 0.1), "l4": (0.88, 0.1),
    }
    edges = [("n0", "n1"), ("n0", "n2"), ("n1", "l1"), ("n1", "l2"),
             ("n2", "l3"), ("n2", "l4")]
    fig = go.Figure()
    for a, b in edges:
        fig.add_trace(go.Scatter(x=[nodes[a][0], nodes[b][0]], y=[nodes[a][1], nodes[b][1]],
                                 mode="lines", line=dict(color=MUTED, width=1.5), hoverinfo="skip"))
    split_feats = [f[rng.randrange(len(f))] for _ in range(3)]
    thr = [round(rng.uniform(0, 1), 2) for _ in range(3)]
    decision = {
        "n0": f"{split_feats[0]} ≤ {thr[0]}",
        "n1": f"{split_feats[1]} ≤ {thr[1]}",
        "n2": f"{split_feats[2]} ≤ {thr[2]}",
    }
    leaves = {k: round(rng.uniform(0, 1), 2) for k in ("l1", "l2", "l3", "l4")}
    for k, (x, y) in nodes.items():
        is_leaf = k.startswith("l")
        label = f"{leaves[k]:.2f}" if is_leaf else decision[k]
        fig.add_trace(go.Scatter(
            x=[x], y=[y], mode="markers+text",
            marker=dict(size=46 if not is_leaf else 34,
                        color=ACCENT if is_leaf else PRIMARY,
                        line=dict(color="white", width=2)),
            text=[label], textposition="middle center",
            textfont=dict(size=9, color="white"), hoverinfo="text",
            hovertext=("leaf prediction" if is_leaf else "split node")))
    fig.update_xaxes(visible=False, range=[0, 1])
    fig.update_yaxes(visible=False, range=[-0.05, 1.1])
    return _base_layout(fig, height=340, title="Representative decision path (depth 2)")


def build_rule_list(features, seed_key):
    rng = _rng(seed_key, "rules")
    f = features or ["feature"]
    rows = []
    for i in range(4):
        a = f[rng.randrange(len(f))]
        b = f[rng.randrange(len(f))]
        out = round(rng.uniform(0, 1), 2)
        cov = round(rng.uniform(5, 40), 1)
        rows.append(html.Tr([
            html.Td(html.Code(f"IF {a} ≤ {round(rng.uniform(0,1),2)} AND {b} > {round(rng.uniform(0,1),2)}")),
            html.Td(f"{out:.2f}", className="text-end"),
            html.Td(f"{cov:.0f}%", className="text-end text-muted"),
        ]))
    return dbc.Table(
        [html.Thead(html.Tr([html.Th("Rule"), html.Th("Prediction", className="text-end"),
                             html.Th("Coverage", className="text-end")]))]
        + [html.Tbody(rows)],
        bordered=False, hover=True, size="sm", className="mb-0")


def build_ard_fig(features, seed_key):
    rng = _rng(seed_key, "ard")
    vals = sorted([1.0 / rng.uniform(0.3, 3.0) for _ in features])
    feats = [f for _, f in sorted(zip(vals, features))]
    fig = go.Figure(go.Bar(x=sorted(vals), y=feats, orientation="h",
                           marker=dict(color=sorted(vals), colorscale="Teal"),
                           hovertemplate="%{y}: relevance %{x:.2f}<extra></extra>"))
    fig.update_xaxes(title="ARD relevance (1 / length-scale)")
    return _base_layout(fig, height=max(260, 26 * len(features)))


def build_uncertainty_fig(seed_key):
    rng = _rng(seed_key, "unc")
    xs = list(range(40))
    mean = []
    v = rng.uniform(0.2, 0.8)
    for _ in xs:
        v += rng.uniform(-0.06, 0.06)
        mean.append(v)
    band = [0.05 + 0.02 * (i % 7) for i in xs]
    upper = [m + 2 * b for m, b in zip(mean, band)]
    lower = [m - 2 * b for m, b in zip(mean, band)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs + xs[::-1], y=upper + lower[::-1], fill="toself",
                             fillcolor="rgba(0,184,148,0.15)", line=dict(width=0), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=xs, y=mean, mode="lines", line=dict(color=ACCENT, width=2)))
    fig.update_xaxes(title="time step")
    fig.update_yaxes(title="prediction ± 2σ")
    return _base_layout(fig, height=320, title="Predictive uncertainty (95% band)")


def build_temporal_saliency(features, seed_key):
    rng = _rng(seed_key, "saliency")
    f = features[:8]
    steps = 24
    z = [[abs(rng.gauss(0, 1)) * (1 + 0.5 * math.sin(t / 3 + i)) for t in range(steps)] for i in range(len(f))]
    fig = go.Figure(go.Heatmap(z=z, y=f, x=[f"t-{steps-t}" for t in range(steps)],
                               colorscale="Inferno",
                               hovertemplate="%{y} @ %{x}: %{z:.2f}<extra></extra>"))
    fig.update_xaxes(title="time step (lag)", showticklabels=False)
    return _base_layout(fig, height=360, title="Temporal saliency |∂ŷ/∂xₜ| (feature × time)")


def build_integrated_gradients(features, seed_key):
    rng = _rng(seed_key, "ig")
    f = features[:8]
    vals = [rng.uniform(-1, 1) for _ in f]
    pairs = sorted(zip(vals, f), key=lambda p: p[0])
    vals = [p[0] for p in pairs]
    feats = [p[1] for p in pairs]
    colors = [PRIMARY if v >= 0 else WARN for v in vals]
    fig = go.Figure(go.Bar(x=vals, y=feats, orientation="h", marker_color=colors))
    fig.add_vline(x=0, line_width=1, line_color=MUTED)
    fig.update_xaxes(title="integrated-gradient attribution")
    return _base_layout(fig, height=max(260, 26 * len(f)))


def build_attention_fig(features, seed_key):
    rng = _rng(seed_key, "attn")
    steps = 12
    z = [[rng.random() for _ in range(steps)] for _ in range(steps)]
    # softmax-ish per row
    for r in range(steps):
        s = sum(z[r])
        z[r] = [x / s for x in z[r]]
    labels = [f"t-{steps-t}" for t in range(steps)]
    fig = go.Figure(go.Heatmap(z=z, x=labels, y=labels, colorscale="Viridis",
                               hovertemplate="query %{y} ← key %{x}: %{z:.2f}<extra></extra>"))
    fig.update_xaxes(title="key (attended-to step)", showticklabels=False)
    fig.update_yaxes(title="query step", showticklabels=False)
    return _base_layout(fig, height=360, title="Self-attention weights (head average)")


def build_pca_loadings(features, seed_key):
    rng = _rng(seed_key, "loadings")
    f = features[:10]
    pcs = [f"PC{i+1}" for i in range(4)]
    z = [[rng.uniform(-1, 1) for _ in pcs] for _ in f]
    fig = go.Figure(go.Heatmap(z=z, x=pcs, y=f, colorscale="RdBu", zmid=0,
                               hovertemplate="%{y} on %{x}: %{z:.2f}<extra></extra>"))
    return _base_layout(fig, height=max(300, 28 * len(f)), title="Component loadings")


def build_variance_fig(seed_key):
    rng = _rng(seed_key, "var")
    ev = sorted([rng.uniform(0.02, 1) for _ in range(8)], reverse=True)
    s = sum(ev)
    ev = [x / s for x in ev]
    cum = []
    acc = 0
    for x in ev:
        acc += x
        cum.append(acc)
    pcs = [f"PC{i+1}" for i in range(len(ev))]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=pcs, y=ev, marker_color=PRIMARY, name="explained"))
    fig.add_trace(go.Scatter(x=pcs, y=cum, mode="lines+markers", line=dict(color=WARN), name="cumulative"))
    fig.update_yaxes(title="explained variance ratio")
    fig.update_layout(showlegend=True, legend=dict(orientation="h", y=1.12))
    return _base_layout(fig, height=320, title="Explained variance")


# ---------------------------------------------------------------------------
# REAL explainer figures (POC) — built from sklearn artifact output
# ---------------------------------------------------------------------------
def build_importance_fig_real(pairs, top=12, xtitle="impurity importance (Gini / variance reduction)"):
    """Horizontal bar of real impurity importances. pairs = [(name, value), ...]."""
    pairs = list(pairs)[:top]
    pairs = sorted(pairs, key=lambda p: p[1])  # ascending -> largest on top
    feats = [p[0] for p in pairs]
    vals = [p[1] for p in pairs]
    fig = go.Figure(go.Bar(
        x=vals, y=feats, orientation="h",
        marker=dict(color=vals, colorscale="Purples"),
        hovertemplate="%{y}: %{x:.4f}<extra></extra>",
    ))
    fig.update_xaxes(title=xtitle)
    return _base_layout(fig, height=max(260, 26 * len(feats)))


def build_tree_fig_real(subtree):
    """Depth-2 decision graphic from a real walked sklearn tree."""
    pos = {
        "n0": (0.5, 1.0), "n1": (0.25, 0.55), "n2": (0.75, 0.55),
        "l1": (0.12, 0.1), "l2": (0.38, 0.1), "l3": (0.62, 0.1), "l4": (0.88, 0.1),
    }
    edges = [("n0", "n1"), ("n0", "n2"), ("n1", "l1"), ("n1", "l2"),
             ("n2", "l3"), ("n2", "l4")]

    def lbl(k):
        return (subtree.get(k) or {}).get("label", "")

    def is_leaf(k):
        return (subtree.get(k) or {}).get("leaf", True)

    fig = go.Figure()
    for a, b in edges:
        if lbl(a) and lbl(b):
            fig.add_trace(go.Scatter(x=[pos[a][0], pos[b][0]], y=[pos[a][1], pos[b][1]],
                                     mode="lines", line=dict(color=MUTED, width=1.5),
                                     hoverinfo="skip"))
    for k, (x, y) in pos.items():
        if not lbl(k):
            continue
        leaf = is_leaf(k)
        fig.add_trace(go.Scatter(
            x=[x], y=[y], mode="markers+text",
            marker=dict(size=34 if leaf else 48,
                        color=ACCENT if leaf else PRIMARY,
                        line=dict(color="white", width=2)),
            text=[lbl(k)], textposition="middle center",
            textfont=dict(size=9, color="white"),
            hoverinfo="text", hovertext=("leaf prediction" if leaf else "split node")))
    fig.update_xaxes(visible=False, range=[0, 1])
    fig.update_yaxes(visible=False, range=[-0.05, 1.1])
    return _base_layout(fig, height=340, title="Representative decision path (depth 2, from artifact)")


def build_rule_list_real(rules_text, max_lines=40):
    lines = (rules_text or "").splitlines()
    if len(lines) > max_lines:
        lines = lines[:max_lines] + ["... (truncated)"]
    return html.Pre("\n".join(lines), style={
        "maxHeight": "320px", "overflow": "auto", "fontSize": "11px",
        "whiteSpace": "pre", "margin": 0, "fontFamily": "var(--bs-font-monospace, monospace)"})


def _live_badge(ok):
    if ok:
        return dbc.Badge([html.I(className="bi bi-broadcast me-1"), "live · sklearn"],
                         color="success", className="mb-2")
    return dbc.Badge("illustrative placeholder", color="secondary", className="mb-2")


def _data_upload_card(features, outputs, supervised):
    """Upload a CSV to recompute the data-backed panels on YOUR data instead of
    the sampled background. Columns must match the model's stored input names;
    an optional target column (the model's output name) unlocks permutation
    importance."""
    if not supervised:
        return None
    out = ", ".join(outputs) if outputs else "—"
    return dbc.Card(dbc.CardBody([
        html.Div([html.I(className="bi bi-upload me-2"),
                  html.Span("Test with your own data", className="fw-semibold")],
                 className="mb-1"),
        html.Div([
            "Upload a CSV to recompute SHAP and partial dependence on your data "
            "(and permutation importance if the target column is present). Input "
            "columns must match the model's stored feature names: ",
            html.Code(", ".join(features) or "—"),
            ". Optional target column: ", html.Code(out), ".",
        ], className="text-muted small mb-2"),
        dcc.Upload(
            id="xai-data-upload",
            children=html.Div(["Drag & drop or ", html.A("select a .csv file")]),
            accept=".csv", multiple=False,
            style={"width": "100%", "height": "60px", "lineHeight": "60px",
                   "borderWidth": "1px", "borderStyle": "dashed",
                   "borderRadius": "8px", "textAlign": "center"}),
        html.Div(id="xai-data-status", className="small mt-2"),
    ]), className="shadow-sm mb-3")


def build_coef_fig_real(pairs, top=14):
    pairs = list(pairs)[:top]
    pairs = sorted(pairs, key=lambda p: p[1])  # ascending for horizontal bars
    feats = [p[0] for p in pairs]
    vals = [p[1] for p in pairs]
    colors = [PRIMARY if v >= 0 else WARN for v in vals]
    fig = go.Figure(go.Bar(x=vals, y=feats, orientation="h", marker_color=colors,
                           hovertemplate="%{y}: %{x:.4f}<extra></extra>"))
    fig.add_vline(x=0, line_width=1, line_color=MUTED)
    fig.update_xaxes(title="coefficient (β)")
    return _base_layout(fig, height=max(260, 26 * len(feats)))


def build_pdp_fig_real(feature, xs, ys):
    fig = go.Figure(go.Scatter(x=list(xs), y=list(ys), mode="lines",
                               line=dict(color=PRIMARY, width=3),
                               hovertemplate=f"{feature}=%{{x:.2f}} → %{{y:.3f}}<extra></extra>"))
    fig.update_xaxes(title=f"{feature}")
    fig.update_yaxes(title="partial dependence")
    return _base_layout(fig, height=320)


def build_shap_summary_fig_real(summary, top=10):
    feats = (summary.get("features") or [])[:top]
    points = summary.get("points") or {}
    fig = go.Figure()
    for i, f in enumerate(feats):
        pt = points.get(f, {})
        sh = pt.get("shap", [])
        fv = pt.get("fval", [0.5] * len(sh))
        ys = [i + ((hash((f, k)) % 1000) / 1000.0 - 0.5) * 0.6 for k in range(len(sh))]
        fig.add_trace(go.Scatter(
            x=sh, y=ys, mode="markers",
            marker=dict(size=6, color=fv, colorscale="RdBu", reversescale=True,
                        cmin=0, cmax=1, showscale=(i == 0),
                        colorbar=dict(title="feat.<br>value", thickness=10) if i == 0 else None),
            hoverinfo="skip"))
    fig.update_yaxes(tickmode="array", tickvals=list(range(len(feats))), ticktext=feats)
    fig.update_xaxes(title="SHAP value (impact on output)")
    fig.add_vline(x=0, line_width=1, line_color=MUTED)
    return _base_layout(fig, height=max(260, 26 * len(feats)))


def build_local_waterfall_fig_real(pairs, base, pred, out_name="output"):
    names = [p[0] for p in pairs]
    vals = [round(float(p[1]), 4) for p in pairs]
    fig = go.Figure(go.Waterfall(
        orientation="v", measure=["relative"] * len(names), x=names, y=vals,
        connector=dict(line=dict(color=MUTED)),
        increasing=dict(marker=dict(color=PRIMARY)),
        decreasing=dict(marker=dict(color=WARN))))
    fig.update_yaxes(title=f"contribution to {out_name}")
    fig.update_xaxes(tickangle=-30)
    return _base_layout(fig, height=340,
                        title=f"E[f(x)]={base:.2f} → prediction {pred:.2f}")


# ---------------------------------------------------------------------------
# UI building blocks
# ---------------------------------------------------------------------------
def _graph(fig, gid=None):
    kw = dict(figure=fig, config={"displayModeBar": False})
    if gid:
        kw["id"] = gid
    return dcc.Graph(**kw)


# Plain-language "how to read this chart" guidance, shown via a hover popover
# on a ? icon in each panel header. Keyed by the panel title.
_PANEL_HELP = {
    "Global feature importance":
        "Ranks inputs by how much the model's accuracy drops when that input is "
        "randomly shuffled — a longer bar means the model leans on it more. Needs "
        "labelled data: upload a CSV that includes the target column to compute it.",
    "SHAP summary":
        "Each dot is one sample. Left/right shows whether that feature pushed the "
        "prediction down/up; colour shows whether the feature's value was low (blue) "
        "or high (red). Features are ordered top-to-bottom by overall impact.",
    "Partial dependence":
        "How the predicted output changes as ONE feature varies, averaging over all "
        "the others. An upward slope means higher feature values give higher "
        "predictions. Pick a feature in the dropdown.",
    "Local explanation":
        "Explains ONE prediction: each bar is how much a feature pushed it above "
        "(blue) or below (red) the average. The bars add up from the baseline "
        "E[f(x)] to the final prediction. Pick an instance in the dropdown.",
    "Impurity-based importance":
        "How much each feature reduced error across the tree's splits, read straight "
        "from the trained model. Fast and exact, but can over-credit features with "
        "many distinct values — cross-check against the SHAP summary.",
    "Feature interactions":
        "How strongly pairs of features combine beyond their individual effects. "
        "Darker cells mean a stronger interaction.",
    "Decision structure":
        "A representative path through the tree: each split node tests "
        "'feature ≤ threshold', leaves show the predicted value. For a forest this "
        "is ONE example tree (the first), not the whole ensemble's combined logic.",
    "Decision rules":
        "The same tree written as IF/THEN rules (scikit-learn's export_text), "
        "truncated to depth 3. For an ensemble it's one representative tree.",
    "Model coefficients":
        "The weight the linear model gives each feature. Positive (blue) raises the "
        "prediction, negative (red) lowers it; larger magnitude = stronger effect. "
        "Most comparable when the inputs are on similar scales.",
    "ARD relevance / kernel weighting":
        "Inverse length-scales: a higher value means the model treats that feature "
        "as more relevant to the prediction.",
    "Predictive uncertainty":
        "The shaded band is the model's confidence around its prediction — wider "
        "means less certain.",
    "Temporal saliency":
        "For sequence models: how sensitive the prediction is to each feature at "
        "each time step. Brighter = more influential at that point in the window.",
    "Integrated gradients":
        "Attributes the prediction to each feature relative to a baseline input — "
        "bars to the right increased the output, to the left decreased it.",
    "Attention map":
        "Which time steps the model paid attention to when predicting; brighter "
        "cells are the steps it weighted most.",
    "Step attribution":
        "How much each feature contributed to this prediction.",
    "Component loadings":
        "How much each original feature contributes to each component / cluster — "
        "the recipe of each component.",
    "Explained variance":
        "How much of the data's total variation each component captures; the line "
        "is the running cumulative share.",
}


def _slug(text):
    return "".join(c.lower() if c.isalnum() else "-" for c in str(text)).strip("-")


def _panel(title, body, subtitle=None, tag=None, help=None):
    help_text = help or _PANEL_HELP.get(title)
    header = [html.Span(title, className="fw-semibold")]
    if help_text:
        hid = "xai-help-" + _slug(title)
        header.append(html.I(className="bi bi-question-circle text-muted ms-2",
                             id=hid, style={"cursor": "pointer", "fontSize": "0.9rem"},
                             title="How to read this chart"))
        header.append(dbc.Popover(dbc.PopoverBody(help_text, className="small"),
                                   target=hid, trigger="hover focus", placement="top"))
    if tag:
        header.append(dbc.Badge(tag, color="light", text_color="secondary",
                                className="ms-2 border"))
    return dbc.Card(dbc.CardBody([
        html.Div(header, className="d-flex align-items-center mb-1"),
        html.Div(subtitle, className="text-muted small mb-2") if subtitle else None,
        body,
    ]), className="shadow-sm h-100")


def _method_chips(methods, color):
    return html.Div([dbc.Badge(m, color=color, className="me-1 mb-1") for m in methods])


def _missing_model_view():
    return html.Div([
        dbc.Alert([
            html.H5("No model selected", className="alert-heading"),
            html.P("Open this view from the magnifying-glass (XAI) icon next to a "
                   "model in the registry to explore its explanations."),
        ], color="secondary"),
    ], style={"padding": "20px"})


# ---------------------------------------------------------------------------
# Family-specific section
# ---------------------------------------------------------------------------
def _tree_family(profile, live, features, outputs, seed_key, family_label):
    """Tree-based families (RF/GBM/HGB/CART). Uses REAL sklearn output when the
    artifact loads (`live.ok`), otherwise illustrative placeholders."""
    ok = bool(live and live.get("ok"))

    if ok and live.get("importances"):
        imp_fig = build_importance_fig_real(live["importances"])
        imp_sub = f"From {live.get('model_class', 'model')}.feature_importances_ — real, read from the artifact."
    else:
        imp_fig = build_importance_fig(features, seed_key, "Impurity")
        imp_sub = "Gini / variance reduction (placeholder — artifact not loadable here)."

    tree_fig = build_tree_fig_real(live["subtree"]) if ok and live.get("subtree") \
        else build_tree_fig(features, seed_key)
    rules_body = build_rule_list_real(live["rules_text"]) if ok and live.get("rules_text") \
        else build_rule_list(features, seed_key)
    rules_sub = "The model's actual learned rules (sklearn export_text)." if ok and live.get("rules_text") \
        else "Illustrative rules (placeholder)."

    rows = [
        dbc.Row([dbc.Col(_panel("Impurity-based importance", _graph(imp_fig), imp_sub,
                                tag=(live.get("model_class") if ok else None)), lg=12)],
                className="g-3"),
        dbc.Row([
            dbc.Col(_panel("Decision structure", _graph(tree_fig),
                           "A representative decision path."), lg=6),
            dbc.Col(_panel("Decision rules", rules_body, rules_sub), lg=6),
        ], className="g-3 mt-1"),
    ]
    if profile == "tree_ensemble":
        rows.append(dbc.Row([dbc.Col(_panel(
            "Feature interactions", _graph(build_interaction_heatmap(features, seed_key)),
            "Pairwise interaction strength (placeholder — needs a dataset)."), lg=12)],
            className="g-3 mt-1"))
    return html.Div([_live_badge(ok)] + rows)


def _family_section(profile, features, outputs, seed_key, family_label, live=None):
    if profile in ("tree_single", "tree_ensemble"):
        return _tree_family(profile, live, features, outputs, seed_key, family_label)
    if profile == "linear":
        live_ok = bool(live and live.get("ok") and live.get("coef"))
        if live_ok:
            coef_fig = build_coef_fig_real(live["coef"])
            sub = (f"Real coefficients from {live.get('model_class', 'model')}.coef_"
                   + (f" (intercept {live['intercept']:.3f})" if live.get("intercept") is not None else ""))
        else:
            coef_fig = build_coef_fig(features, seed_key)
            sub = "Sign + magnitude of each weight (placeholder)."
        return html.Div([
            _live_badge(live_ok),
            dbc.Row([dbc.Col(_panel("Model coefficients", _graph(coef_fig), sub), lg=12)],
                    className="g-3"),
        ])
    if profile == "kernel":
        return dbc.Row([
            dbc.Col(_panel("ARD relevance / kernel weighting",
                           _graph(build_ard_fig(features, seed_key)),
                           "Inverse length-scales — higher = more relevant."), lg=6),
            dbc.Col(_panel("Predictive uncertainty",
                           _graph(build_uncertainty_fig(seed_key)),
                           "Confidence band around predictions."), lg=6),
        ], className="g-3")
    if profile == "neural_seq":
        return dbc.Row([
            dbc.Col(_panel("Temporal saliency",
                           _graph(build_temporal_saliency(features, seed_key)),
                           "Gradient magnitude over the input window."), lg=7),
            dbc.Col(_panel("Integrated gradients",
                           _graph(build_integrated_gradients(features, seed_key)),
                           "Attribution vs. a baseline input."), lg=5),
        ], className="g-3")
    if profile == "attention":
        return dbc.Row([
            dbc.Col(_panel("Attention map",
                           _graph(build_attention_fig(features, seed_key)),
                           "Which steps the model attends to."), lg=7),
            dbc.Col(_panel("Step attribution",
                           _graph(build_integrated_gradients(features, seed_key)),
                           "Per-feature attribution."), lg=5),
        ], className="g-3")
    if profile == "unsupervised":
        return dbc.Row([
            dbc.Col(_panel("Component loadings",
                           _graph(build_pca_loadings(features, seed_key)),
                           "Feature contribution to each component / cluster."), lg=6),
            dbc.Col(_panel("Explained variance",
                           _graph(build_variance_fig(seed_key)),
                           "How much structure each component captures."), lg=6),
        ], className="g-3")
    # generic / custom
    return dbc.Alert(
        "No interpretable internals are exposed for this algorithm family. "
        "Only the model-agnostic methods above apply.",
        color="light", className="border")


# ---------------------------------------------------------------------------
# Core (model-agnostic) section
# ---------------------------------------------------------------------------
def _core_section(features, outputs, seed_key, supervised, live=None):
    if not supervised:
        return dbc.Alert(
            "This is an unsupervised model — target-based attributions "
            "(SHAP, partial dependence) do not apply. See the structural "
            "explanations below.", color="light", className="border")

    ok = bool(live and live.get("ok"))
    bg = (live or {}).get("background", "")
    feat_opts = [{"label": f, "value": f} for f in features]
    f0 = features[0] if features else None

    # SHAP summary — real when available
    if ok and live.get("shap_summary"):
        shap_fig = build_shap_summary_fig_real(live["shap_summary"])
        shap_sub = f"Real SHAP values ({live.get('model_class', 'model')}); {bg}."
        shap_tag = "live · shap"
    else:
        shap_fig = build_shap_summary_fig(features, seed_key)
        shap_sub = "Per-sample SHAP values; colour = feature value (placeholder)."
        shap_tag = "placeholder"

    # Permutation importance — real when an uploaded dataset carried a target
    perm = (live or {}).get("perm_importance")
    if ok and perm:
        imp_fig = build_importance_fig_real(perm, xtitle="permutation importance (mean score drop)")
        imp_sub = f"Permutation importance on {bg}."
        imp_tag = "live · sklearn"
    else:
        imp_fig = build_importance_fig(features, seed_key)
        imp_sub = "Permutation importance needs labels — upload data with a target column to compute it."
        imp_tag = "placeholder"
    imp_panel = _panel("Global feature importance", _graph(imp_fig), imp_sub, tag=imp_tag)

    row1 = dbc.Row([
        dbc.Col(imp_panel, lg=6),
        dbc.Col(_panel("SHAP summary", _graph(shap_fig), shap_sub, tag=shap_tag), lg=6),
    ], className="g-3")

    # Partial dependence — real curve when available
    pdp = (live or {}).get("pdp") or {}
    if ok and f0 in pdp:
        pdp_fig = build_pdp_fig_real(f0, pdp[f0]["x"], pdp[f0]["y"])
    else:
        pdp_fig = build_pdp_fig(f0 or "feature", seed_key)
    pdp_tag = "live · sklearn" if (ok and pdp) else "placeholder"

    # Local SHAP — real instance when available
    inst = (live or {}).get("shap_instances") or {}
    if ok and "1" in inst:
        d = inst["1"]
        local_fig = build_local_waterfall_fig_real(
            d["pairs"], d.get("base", 0.0), d.get("pred", 0.0),
            (outputs or ["output"])[0])
    else:
        local_fig = build_local_waterfall_fig(features, outputs, seed_key, 1)
    local_tag = "live · shap" if (ok and inst) else "placeholder"

    row2 = dbc.Row([
        dbc.Col(_panel("Partial dependence", html.Div([
            dcc.Dropdown(id="xai-pdp-feature", options=feat_opts, value=f0,
                         clearable=False, className="mb-2"),
            _graph(pdp_fig, gid="xai-pdp-graph"),
        ]), "Average model response as one feature varies.", tag=pdp_tag), lg=6),
        dbc.Col(_panel("Local explanation", html.Div([
            dcc.Dropdown(id="xai-instance-select",
                         options=[{"label": f"Instance #{i}", "value": i} for i in range(1, 9)],
                         value=1, clearable=False, className="mb-2"),
            _graph(local_fig, gid="xai-local-graph"),
        ]), "Why the model made one specific prediction.", tag=local_tag), lg=6),
    ], className="g-3 mt-1")
    return html.Div([row1, row2])


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
    model_type = row.get("model_type") or ("interpretable"
                                           if profile in ("tree_single", "linear") else "—")
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
        live = xai_service.explain(project_id, model_id, family=profile, session_data=session_data)
    except Exception as exc:  # never let explainer issues break the page
        __import__("logging").getLogger(__name__).info("xai_service unavailable: %s", exc)
        live = None

    type_color = {"interpretable": "success", "black_box": "dark"}.get(model_type, "secondary")

    header = dbc.Card(dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4(model_name, className="d-inline mb-0 me-2"),
                    dbc.Badge(family_label, color="primary", className="me-1"),
                    dbc.Badge(model_type, color=type_color, className="me-1"),
                ]),
                html.Div([
                    html.Span(f"v{version}", className="text-muted small me-3"),
                    html.Span(f"status: {status}", className="text-muted small me-3"),
                    html.Span(f"author: {authors}", className="text-muted small me-3"),
                    html.Span(f"{len(features)} inputs → {len(outputs)} output(s)",
                              className="text-muted small"),
                ], className="mt-1"),
            ], md=7),
            dbc.Col([
                html.Div("Applicable methods", className="small text-uppercase text-muted mb-1"),
                _method_chips(_CORE_METHODS, "info"),
                html.Div(className="mt-1"),
                _method_chips(_METHODS_FOR.get(profile, []), "primary"),
            ], md=5),
        ]),
    ]), className="shadow-sm mb-3")

    caps = (live or {}).get("capabilities") or []
    live_ok = bool(live and live.get("ok") and caps)
    if live_ok:
        _cap_labels = {"impurity": "impurity importance", "rules": "decision rules",
                       "tree": "tree structure", "coef": "coefficients",
                       "pdp": "partial dependence", "shap": "SHAP"}
        shown = ", ".join(_cap_labels.get(c, c) for c in caps)
        note = dbc.Alert([
            html.I(className="bi bi-broadcast me-2"),
            html.Span(f"LIVE via scikit-learn on the {live.get('model_class', 'model')} "
                      f"artifact: {shown}. "),
            html.Span("SHAP / partial dependence are evaluated over a background sampled "
                      "from each feature's declared operating range; permutation importance "
                      "stays a placeholder (no labelled dataset shipped).",
                      className="text-muted"),
        ], color="success", className="py-2 small")
    else:
        note = dbc.Alert([
            html.I(className="bi bi-info-circle me-2"),
            "Prototype — illustrative placeholders from the model's metadata. The artifact "
            "could not be explained as an sklearn model here (R / keras models, or "
            "scikit-learn / shap unavailable in this environment).",
        ], color="warning", className="py-2 small")

    store = dcc.Store(id="xai-model-store", data={
        "model_id": model_id, "project_id": project_id, "seed_key": seed_key,
        "features": features, "outputs": outputs, "profile": profile,
        "pdp": (live or {}).get("pdp"),
        "shap_instances": (live or {}).get("shap_instances"),
        "supervised": supervised,
    })

    return html.Div([
        store,
        dbc.Row([
            dbc.Col(html.A([html.I(className="bi bi-arrow-left me-1"), "Back to models"],
                           href="/", className="text-decoration-none small"), width="auto"),
        ], className="mb-2"),
        header,
        note,
        _data_upload_card(features, outputs, supervised),
        html.H5("Model-agnostic explanations", className="mb-2"),
        html.Div(_core_section(features, outputs, seed_key, supervised, live),
                 id="xai-core-container"),
        html.Hr(className="my-4"),
        html.H5([f"Family-specific — ", html.Span(family_label, className="text-primary")],
                className="mb-2"),
        _family_section(profile, features, outputs, seed_key, family_label, live),
        html.Div(style={"height": "30px"}),
    ], style={"padding": "20px"})
