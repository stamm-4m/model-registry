"""Utility helpers for the XAI detail view.

This module hosts reusable figure builders and deterministic placeholder
generators that are shared by page layouts and callbacks.
"""

from __future__ import annotations

import hashlib
import math
import random

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import html

PRIMARY = "#2c7be5"
ACCENT = "#00b894"
WARN = "#e17055"
MUTED = "#6c757d"


def _seed(*parts) -> int:
    h = hashlib.md5("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(h[:8], 16)


def _rng(*parts) -> random.Random:
    return random.Random(_seed(*parts))


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
    fig.add_trace(
        go.Scatter(
            x=xs + xs[::-1],
            y=upper + lower[::-1],
            fill="toself",
            fillcolor="rgba(44,123,229,0.12)",
            line=dict(width=0),
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=mean,
            mode="lines",
            line=dict(color=PRIMARY, width=3),
            hovertemplate=f"{feature}=%{{x:.2f}} -> %{{y:.2f}}<extra></extra>",
        )
    )
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
    fig = go.Figure(
        go.Waterfall(
            orientation="v",
            measure=["relative"] * len(top),
            x=top,
            y=contribs,
            connector=dict(line=dict(color=MUTED)),
            increasing=dict(marker=dict(color=PRIMARY)),
            decreasing=dict(marker=dict(color=WARN)),
        )
    )
    out = outputs[0] if outputs else "output"
    fig.update_yaxes(title=f"contribution to {out}")
    fig.update_xaxes(tickangle=-30)
    return _base_layout(
        fig,
        height=340,
        title=f"E[f(x)]={base_val:.2f} -> prediction for instance {instance}",
    )


def build_pdp_fig_real(feature, xs, ys):
    fig = go.Figure(
        go.Scatter(
            x=list(xs),
            y=list(ys),
            mode="lines",
            line=dict(color=PRIMARY, width=3),
            hovertemplate=f"{feature}=%{{x:.2f}} -> %{{y:.3f}}<extra></extra>",
        )
    )
    fig.update_xaxes(title=f"{feature}")
    fig.update_yaxes(title="partial dependence")
    return _base_layout(fig, height=320)


def build_local_waterfall_fig_real(pairs, base, pred, out_name="output"):
    names = [p[0] for p in pairs]
    vals = [round(float(p[1]), 4) for p in pairs]
    fig = go.Figure(
        go.Waterfall(
            orientation="v",
            measure=["relative"] * len(names),
            x=names,
            y=vals,
            connector=dict(line=dict(color=MUTED)),
            increasing=dict(marker=dict(color=PRIMARY)),
            decreasing=dict(marker=dict(color=WARN)),
        )
    )
    fig.update_yaxes(title=f"contribution to {out_name}")
    fig.update_xaxes(tickangle=-30)
    return _base_layout(
        fig, height=340, title=f"E[f(x)]={base:.2f} -> prediction {pred:.2f}"
    )


def build_importance_fig(features, seed_key, method="Permutation"):
    rng = _rng(seed_key, method)
    vals = sorted([rng.uniform(0.02, 1.0) for _ in features])
    feats = [f for _, f in sorted(zip(vals, features))]
    vals = sorted(vals)
    fig = go.Figure(
        go.Bar(
            x=vals,
            y=feats,
            orientation="h",
            marker=dict(color=vals, colorscale="Blues", cmin=0, cmax=1),
            hovertemplate="%{y}: %{x:.3f}<extra></extra>",
        )
    )
    fig.update_xaxes(title=f"{method} importance (delta score)")
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
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="markers",
                marker=dict(
                    size=6,
                    color=cols,
                    colorscale="RdBu",
                    reversescale=True,
                    showscale=(i == 0),
                    colorbar=dict(title="feat.<br>value", thickness=10)
                    if i == 0
                    else None,
                ),
                hoverinfo="skip",
            )
        )
    fig.update_yaxes(tickmode="array", tickvals=list(range(len(order))), ticktext=order)
    fig.update_xaxes(title="SHAP value (impact on output)")
    fig.add_vline(x=0, line_width=1, line_color=MUTED)
    return _base_layout(fig, height=max(260, 26 * len(features)))


def build_coef_fig(features, seed_key):
    rng = _rng(seed_key, "coef")
    vals = [rng.uniform(-1.5, 1.5) for _ in features]
    pairs = sorted(zip(vals, features), key=lambda p: p[0])
    vals = [p[0] for p in pairs]
    feats = [p[1] for p in pairs]
    colors = [PRIMARY if v >= 0 else WARN for v in vals]
    fig = go.Figure(
        go.Bar(
            x=vals,
            y=feats,
            orientation="h",
            marker_color=colors,
            hovertemplate="%{y}: %{x:.3f}<extra></extra>",
        )
    )
    fig.add_vline(x=0, line_width=1, line_color=MUTED)
    fig.update_xaxes(title="standardised coefficient (beta)")
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
    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=f,
            y=f,
            colorscale="Purples",
            hovertemplate="%{y} x %{x}: %{z:.2f}<extra></extra>",
        )
    )
    fig.update_xaxes(tickangle=-30)
    return _base_layout(
        fig, height=360, title="Feature interaction strength (Friedman's H)"
    )


def build_tree_fig(features, seed_key):
    """Small illustrative decision tree (node-link)."""
    rng = _rng(seed_key, "tree")
    f = features or ["feature"]
    nodes = {
        "n0": (0.5, 1.0),
        "n1": (0.25, 0.55),
        "n2": (0.75, 0.55),
        "l1": (0.12, 0.1),
        "l2": (0.38, 0.1),
        "l3": (0.62, 0.1),
        "l4": (0.88, 0.1),
    }
    edges = [
        ("n0", "n1"),
        ("n0", "n2"),
        ("n1", "l1"),
        ("n1", "l2"),
        ("n2", "l3"),
        ("n2", "l4"),
    ]
    fig = go.Figure()
    for a, b in edges:
        fig.add_trace(
            go.Scatter(
                x=[nodes[a][0], nodes[b][0]],
                y=[nodes[a][1], nodes[b][1]],
                mode="lines",
                line=dict(color=MUTED, width=1.5),
                hoverinfo="skip",
            )
        )
    split_feats = [f[rng.randrange(len(f))] for _ in range(3)]
    thr = [round(rng.uniform(0, 1), 2) for _ in range(3)]
    decision = {
        "n0": f"{split_feats[0]} <= {thr[0]}",
        "n1": f"{split_feats[1]} <= {thr[1]}",
        "n2": f"{split_feats[2]} <= {thr[2]}",
    }
    leaves = {k: round(rng.uniform(0, 1), 2) for k in ("l1", "l2", "l3", "l4")}
    for k, (x, y) in nodes.items():
        is_leaf = k.startswith("l")
        label = f"{leaves[k]:.2f}" if is_leaf else decision[k]
        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                marker=dict(
                    size=46 if not is_leaf else 34,
                    color=ACCENT if is_leaf else PRIMARY,
                    line=dict(color="white", width=2),
                ),
                text=[label],
                textposition="middle center",
                textfont=dict(size=9, color="white"),
                hoverinfo="text",
                hovertext=("leaf prediction" if is_leaf else "split node"),
            )
        )
    fig.update_xaxes(visible=False, range=[0, 1])
    fig.update_yaxes(visible=False, range=[-0.05, 1.1])
    return _base_layout(fig, height=340, title="Representative decision path (depth 2)")


def build_rule_list(features, seed_key):
    rng = _rng(seed_key, "rules")
    f = features or ["feature"]
    rows = []
    for _ in range(4):
        a = f[rng.randrange(len(f))]
        b = f[rng.randrange(len(f))]
        out = round(rng.uniform(0, 1), 2)
        cov = round(rng.uniform(5, 40), 1)
        rows.append(
            html.Tr(
                [
                    html.Td(
                        html.Code(
                            f"IF {a} <= {round(rng.uniform(0, 1), 2)} AND {b} > {round(rng.uniform(0, 1), 2)}"
                        )
                    ),
                    html.Td(f"{out:.2f}", className="text-end"),
                    html.Td(f"{cov:.0f}%", className="text-end text-muted"),
                ]
            )
        )
    return dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Rule"),
                        html.Th("Prediction", className="text-end"),
                        html.Th("Coverage", className="text-end"),
                    ]
                )
            )
        ]
        + [html.Tbody(rows)],
        bordered=False,
        hover=True,
        size="sm",
        className="mb-0",
    )


def build_ard_fig(features, seed_key):
    rng = _rng(seed_key, "ard")
    vals = sorted([1.0 / rng.uniform(0.3, 3.0) for _ in features])
    feats = [f for _, f in sorted(zip(vals, features))]
    fig = go.Figure(
        go.Bar(
            x=sorted(vals),
            y=feats,
            orientation="h",
            marker=dict(color=sorted(vals), colorscale="Teal"),
            hovertemplate="%{y}: relevance %{x:.2f}<extra></extra>",
        )
    )
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
    fig.add_trace(
        go.Scatter(
            x=xs + xs[::-1],
            y=upper + lower[::-1],
            fill="toself",
            fillcolor="rgba(0,184,148,0.15)",
            line=dict(width=0),
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(x=xs, y=mean, mode="lines", line=dict(color=ACCENT, width=2))
    )
    fig.update_xaxes(title="time step")
    fig.update_yaxes(title="prediction +/- 2sigma")
    return _base_layout(fig, height=320, title="Predictive uncertainty (95% band)")


def build_temporal_saliency(features, seed_key):
    rng = _rng(seed_key, "saliency")
    f = features[:8]
    steps = 24
    z = [
        [abs(rng.gauss(0, 1)) * (1 + 0.5 * math.sin(t / 3 + i)) for t in range(steps)]
        for i in range(len(f))
    ]
    fig = go.Figure(
        go.Heatmap(
            z=z,
            y=f,
            x=[f"t-{steps - t}" for t in range(steps)],
            colorscale="Inferno",
            hovertemplate="%{y} @ %{x}: %{z:.2f}<extra></extra>",
        )
    )
    fig.update_xaxes(title="time step (lag)", showticklabels=False)
    return _base_layout(
        fig, height=360, title="Temporal saliency |d yhat / d xt| (feature x time)"
    )


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
    for r in range(steps):
        s = sum(z[r])
        z[r] = [x / s for x in z[r]]
    labels = [f"t-{steps - t}" for t in range(steps)]
    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=labels,
            y=labels,
            colorscale="Viridis",
            hovertemplate="query %{y} <- key %{x}: %{z:.2f}<extra></extra>",
        )
    )
    fig.update_xaxes(title="key (attended-to step)", showticklabels=False)
    fig.update_yaxes(title="query step", showticklabels=False)
    return _base_layout(fig, height=360, title="Self-attention weights (head average)")


def build_pca_loadings(features, seed_key):
    rng = _rng(seed_key, "loadings")
    f = features[:10]
    pcs = [f"PC{i + 1}" for i in range(4)]
    z = [[rng.uniform(-1, 1) for _ in pcs] for _ in f]
    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=pcs,
            y=f,
            colorscale="RdBu",
            zmid=0,
            hovertemplate="%{y} on %{x}: %{z:.2f}<extra></extra>",
        )
    )
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
    pcs = [f"PC{i + 1}" for i in range(len(ev))]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=pcs, y=ev, marker_color=PRIMARY, name="explained"))
    fig.add_trace(
        go.Scatter(
            x=pcs, y=cum, mode="lines+markers", line=dict(color=WARN), name="cumulative"
        )
    )
    fig.update_yaxes(title="explained variance ratio")
    fig.update_layout(showlegend=True, legend=dict(orientation="h", y=1.12))
    return _base_layout(fig, height=320, title="Explained variance")


def build_importance_fig_real(
    pairs, top=12, xtitle="impurity importance (Gini / variance reduction)"
):
    pairs = list(pairs)[:top]
    pairs = sorted(pairs, key=lambda p: p[1])
    feats = [p[0] for p in pairs]
    vals = [p[1] for p in pairs]
    fig = go.Figure(
        go.Bar(
            x=vals,
            y=feats,
            orientation="h",
            marker=dict(color=vals, colorscale="Purples"),
            hovertemplate="%{y}: %{x:.4f}<extra></extra>",
        )
    )
    fig.update_xaxes(title=xtitle)
    return _base_layout(fig, height=max(260, 26 * len(feats)))


def build_tree_fig_real(subtree):
    pos = {
        "n0": (0.5, 1.0),
        "n1": (0.25, 0.55),
        "n2": (0.75, 0.55),
        "l1": (0.12, 0.1),
        "l2": (0.38, 0.1),
        "l3": (0.62, 0.1),
        "l4": (0.88, 0.1),
    }
    edges = [
        ("n0", "n1"),
        ("n0", "n2"),
        ("n1", "l1"),
        ("n1", "l2"),
        ("n2", "l3"),
        ("n2", "l4"),
    ]

    def lbl(k):
        return (subtree.get(k) or {}).get("label", "")

    def is_leaf(k):
        return (subtree.get(k) or {}).get("leaf", True)

    fig = go.Figure()
    for a, b in edges:
        if lbl(a) and lbl(b):
            fig.add_trace(
                go.Scatter(
                    x=[pos[a][0], pos[b][0]],
                    y=[pos[a][1], pos[b][1]],
                    mode="lines",
                    line=dict(color=MUTED, width=1.5),
                    hoverinfo="skip",
                )
            )
    for k, (x, y) in pos.items():
        if not lbl(k):
            continue
        leaf = is_leaf(k)
        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                marker=dict(
                    size=34 if leaf else 48,
                    color=ACCENT if leaf else PRIMARY,
                    line=dict(color="white", width=2),
                ),
                text=[lbl(k)],
                textposition="middle center",
                textfont=dict(size=9, color="white"),
                hoverinfo="text",
                hovertext=("leaf prediction" if leaf else "split node"),
            )
        )
    fig.update_xaxes(visible=False, range=[0, 1])
    fig.update_yaxes(visible=False, range=[-0.05, 1.1])
    return _base_layout(
        fig, height=340, title="Representative decision path (depth 2, from artifact)"
    )


def build_rule_list_real(rules_text, max_lines=40):
    lines = (rules_text or "").splitlines()
    if len(lines) > max_lines:
        lines = lines[:max_lines] + ["... (truncated)"]
    return html.Pre(
        "\n".join(lines),
        style={
            "maxHeight": "320px",
            "overflow": "auto",
            "fontSize": "11px",
            "whiteSpace": "pre",
            "margin": 0,
            "fontFamily": "var(--bs-font-monospace, monospace)",
        },
    )


def build_coef_fig_real(pairs, top=14):
    pairs = list(pairs)[:top]
    pairs = sorted(pairs, key=lambda p: p[1])
    feats = [p[0] for p in pairs]
    vals = [p[1] for p in pairs]
    colors = [PRIMARY if v >= 0 else WARN for v in vals]
    fig = go.Figure(
        go.Bar(
            x=vals,
            y=feats,
            orientation="h",
            marker_color=colors,
            hovertemplate="%{y}: %{x:.4f}<extra></extra>",
        )
    )
    fig.add_vline(x=0, line_width=1, line_color=MUTED)
    fig.update_xaxes(title="coefficient (beta)")
    return _base_layout(fig, height=max(260, 26 * len(feats)))


def build_shap_summary_fig_real(summary, top=10):
    feats = (summary.get("features") or [])[:top]
    points = summary.get("points") or {}
    fig = go.Figure()
    for i, f in enumerate(feats):
        pt = points.get(f, {})
        sh = pt.get("shap", [])
        fv = pt.get("fval", [0.5] * len(sh))
        ys = [i + ((hash((f, k)) % 1000) / 1000.0 - 0.5) * 0.6 for k in range(len(sh))]
        fig.add_trace(
            go.Scatter(
                x=sh,
                y=ys,
                mode="markers",
                marker=dict(
                    size=6,
                    color=fv,
                    colorscale="RdBu",
                    reversescale=True,
                    cmin=0,
                    cmax=1,
                    showscale=(i == 0),
                    colorbar=dict(title="feat.<br>value", thickness=10)
                    if i == 0
                    else None,
                ),
                hoverinfo="skip",
            )
        )
    fig.update_yaxes(tickmode="array", tickvals=list(range(len(feats))), ticktext=feats)
    fig.update_xaxes(title="SHAP value (impact on output)")
    fig.add_vline(x=0, line_width=1, line_color=MUTED)
    return _base_layout(fig, height=max(260, 26 * len(feats)))
