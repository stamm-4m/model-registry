"""Federated Learning — registry view (LIVE + fallback).

Reads federations / participants from the registry API (`/api/v1/federations`,
`/api/v1/federation_participants`) via `services.federations_service`, and
supports basic CRUD on federations (add / edit / delete) from the UI. If the
API returns nothing or errors, it falls back to a static representative preview
so the page always renders. Callbacks live in
`callbacks/callbacks_federated_learning.py`.
"""
import json

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from model_registry.backend.services import federations_service as fl

TEAL = "#00a3a6"
DEEP = "#007E82"
SLATE = "#275662"
RAMP = ["#00a3a6", "#007E82", "#3f8f95", "#7fb3b8", "#b9d6d8"]

# (label shown, value stored) — value MUST match the federations_strategy_check
STRATEGIES = [("FedAvg", "fedavg"), ("FedProx", "fedprox"), ("FedOpt", "fedopt"),
              ("FedMedian", "fedmedian"), ("SCAFFOLD", "scaffold"), ("Custom", "custom")]
_STRAT_LABEL = {v: l for l, v in STRATEGIES}


def _strategy_label(v):
    return _STRAT_LABEL.get(v, v or "—")
PRIVACY = ["none", "differential_privacy"]
STATUSES = ["planning", "running", "completed"]

# ---- static fallback (normalised to the live shape) ----
_STATIC_FEDS = [
    {"id": "static-biomass", "slug": "biomass_fed_v1", "name": "Biomass soft-sensor FL",
     "aggregation_strategy": "fedavg", "privacy_mechanism": "differential_privacy",
     "privacy_params": {"epsilon": 3.0}, "rounds_planned": 10, "rounds_completed": 7,
     "status": "running"},
    {"id": "static-pen", "slug": "penicillin_yield_fed", "name": "Penicillin yield FL",
     "aggregation_strategy": "fedprox", "privacy_mechanism": "none",
     "privacy_params": {}, "rounds_planned": 12, "rounds_completed": 12, "status": "completed"},
    {"id": "static-ecoli", "slug": "ecoli_softsensor_fed", "name": "E. coli soft-sensor FL",
     "aggregation_strategy": "fedavg", "privacy_mechanism": "differential_privacy",
     "privacy_params": {"epsilon": 1.0}, "rounds_planned": 8, "rounds_completed": 2, "status": "running"},
]
_STATIC_PARTS = [
    {"federation_id": "static-biomass", "project_id": "P0001", "role": "coordinator", "local_dataset_size": 42300, "last_contribution_round": 7},
    {"federation_id": "static-biomass", "project_id": "P0002", "role": "participant", "local_dataset_size": 31850, "last_contribution_round": 7},
    {"federation_id": "static-biomass", "project_id": "P0003", "role": "participant", "local_dataset_size": 18470, "last_contribution_round": 6},
    {"federation_id": "static-pen", "project_id": "P0001", "role": "coordinator", "local_dataset_size": 55000, "last_contribution_round": 12},
    {"federation_id": "static-pen", "project_id": "P0002", "role": "participant", "local_dataset_size": 28000, "last_contribution_round": 12},
    {"federation_id": "static-ecoli", "project_id": "P0002", "role": "coordinator", "local_dataset_size": 20000, "last_contribution_round": 2},
    {"federation_id": "static-ecoli", "project_id": "P0003", "role": "participant", "local_dataset_size": 9220, "last_contribution_round": 1},
]


# ---- small helpers ----
def _priv_params(fed):
    pp = fed.get("privacy_params") or {}
    if isinstance(pp, str):
        try:
            pp = json.loads(pp)
        except Exception:
            pp = {}
    return pp if isinstance(pp, dict) else {}


def _priv_label(fed):
    mech = fed.get("privacy_mechanism") or "none"
    if mech in (None, "none"):
        return "none"
    eps = _priv_params(fed).get("epsilon")
    return f"DP (ε={eps})" if eps is not None else "DP"


def _apply_labels(parts, labels):
    for p in (parts or []):
        pid = str(p.get("project_id"))
        p["project_label"] = (labels or {}).get(pid, p.get("project_id"))
    return parts


def _parts_for(fed, participants):
    fid = fed.get("id")
    return [p for p in participants if str(p.get("federation_id")) == str(fid)]


def _status_badge(s):
    color = {"running": "success", "completed": "secondary", "planning": "info",
             "coordinator": "primary", "participant": "light"}.get(s, "light")
    tc = "dark" if s in ("participant",) else None
    return dbc.Badge(s, color=color, text_color=tc, className="text-uppercase")


def _rounds_bar(done, planned):
    done = done or 0; planned = planned or 1
    pct = int(100 * done / planned) if planned else 0
    return html.Div([
        html.Div(style={"height": "6px", "borderRadius": "3px", "background": "#e5e7eb",
                        "overflow": "hidden", "width": "90px", "display": "inline-block",
                        "verticalAlign": "middle"},
                 children=html.Div(style={"width": f"{pct}%", "height": "100%", "background": TEAL})),
        html.Small(f" {done}/{planned}", className="text-muted"),
    ])


def _base(fig, height=300):
    fig.update_layout(template="plotly_white", height=height,
                      margin=dict(l=10, r=10, t=12, b=10), font=dict(size=12),
                      legend=dict(orientation="h", y=-0.2))
    return fig


def _kpi(label, value, sub=None):
    return dbc.Card(dbc.CardBody([
        html.Div(label, className="text-muted small text-uppercase"),
        html.Div(value, style={"fontSize": "22px", "fontWeight": 600, "color": SLATE}),
        html.Div(sub, className="text-muted small") if sub else None,
    ]), className="shadow-sm h-100")


def _panel(title, body):
    return dbc.Card(dbc.CardBody([html.Div(title, className="fw-semibold mb-2"), body]),
                    className="shadow-sm h-100")


# ---- figures (representative shape, sized to the federation) ----
def _convergence_fig(rounds_done):
    n = max(2, int(rounds_done or 7))
    xs = list(range(1, n + 1))
    ys, v = [], 0.42
    for _ in xs:
        v += (0.85 - v) * 0.28
        ys.append(round(v, 3))
    fig = go.Figure(go.Scatter(x=xs, y=ys, mode="lines+markers",
                               line=dict(color=TEAL, width=3), marker=dict(size=7)))
    fig.update_xaxes(title="aggregation round", dtick=1)
    fig.update_yaxes(title="global model R²")
    return _base(fig)


def _contribution_fig(parts, rounds_done):
    n = max(2, int(rounds_done or 7))
    xs = list(range(1, n + 1))
    total = sum((p.get("local_dataset_size") or 0) for p in parts) or 1
    fig = go.Figure()
    for i, p in enumerate(parts[:5]):
        w = (p.get("local_dataset_size") or 0) / total
        fig.add_trace(go.Bar(x=xs, y=[round(w, 3)] * n, name=p.get("project_id", "?"),
                             marker_color=RAMP[i % len(RAMP)]))
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title="aggregation round", dtick=1)
    fig.update_yaxes(title="contribution weight")
    return _base(fig)


def _dataset_fig(parts):
    labs = [p.get("project_label") or p.get("project_id", "?") for p in parts]
    sizes = [p.get("local_dataset_size") or 0 for p in parts]
    if not labs:
        labs, sizes = ["—"], [0]
    order = sorted(range(len(labs)), key=lambda i: sizes[i])
    labs = [labs[i] for i in order]; sizes = [sizes[i] for i in order]
    fig = go.Figure(go.Bar(x=sizes, y=labs, orientation="h",
                           marker=dict(color=sizes, colorscale=[[0, "#b9d6d8"], [1, TEAL]])))
    fig.update_xaxes(title="local dataset size (samples)")
    return _base(fig, 260)


def _rounds_for(fed, rounds):
    fid = str(fed.get("id"))
    rs = [r for r in (rounds or []) if str(r.get("federation_id")) == fid]
    return sorted(rs, key=lambda r: r.get("round_number") or 0)


def _contrib_dict(r):
    c = r.get("contributions") or {}
    if isinstance(c, str):
        try:
            c = json.loads(c)
        except Exception:
            c = {}
    return c if isinstance(c, dict) else {}


def _json_field(fed, key):
    v = fed.get(key) or {}
    if isinstance(v, str):
        try:
            v = json.loads(v)
        except Exception:
            v = {}
    return v if isinstance(v, dict) else {}


def _convergence_fig_real(rfed):
    xs = [r.get("round_number") for r in rfed]
    ys = [float(r.get("global_metric_value") or 0) for r in rfed]
    fig = go.Figure(go.Scatter(x=xs, y=ys, mode="lines+markers",
                               line=dict(color=TEAL, width=3), marker=dict(size=7),
                               hovertemplate="round %{x}: %{y:.3f}<extra></extra>"))
    fig.update_xaxes(title="aggregation round", dtick=1)
    name = (rfed[0].get("global_metric_name") if rfed else None) or "metric"
    fig.update_yaxes(title=f"global model {name}")
    return _base(fig)


def _contribution_fig_real(rfed):
    xs = [r.get("round_number") for r in rfed]
    keys = []
    for r in rfed:
        for k in _contrib_dict(r):
            if k not in keys:
                keys.append(k)
    fig = go.Figure()
    for i, k in enumerate(keys[:6]):
        ys = [float(_contrib_dict(r).get(k, 0)) for r in rfed]
        fig.add_trace(go.Bar(x=xs, y=ys, name=k, marker_color=RAMP[i % len(RAMP)]))
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title="aggregation round", dtick=1)
    fig.update_yaxes(title="contribution weight")
    return _base(fig)


def _config_panel(fed):
    sp = _json_field(fed, "strategy_params")
    ms = _json_field(fed, "model_spec")

    def kv(k, v):
        return html.Div([html.Span(f"{k}: ", className="text-muted small"),
                         html.Span(str(v), className="small")])

    body = html.Div([
        kv("strategy", _strategy_label(fed.get("aggregation_strategy"))),
        kv("strategy params", sp or "—"),
        kv("privacy", _priv_label(fed)),
        html.Hr(className="my-2"),
        html.Div("Shared model spec", className="fw-semibold small mb-1"),
        kv("framework", f"{ms.get('framework', '—')} {ms.get('version', '')}".strip()),
        kv("architecture", ms.get("architecture", "—")),
        kv("inputs", ", ".join(ms.get("inputs", []) or []) or "—"),
        kv("outputs", ", ".join(ms.get("outputs", []) or []) or "—"),
    ])
    return _panel("Federation config", body)


# ---- builders shared by layout + callbacks ----
def fed_options(feds):
    return [{"label": f.get("name") or f.get("slug"), "value": f.get("id")} for f in feds]


def _participants_cell(count, pf, pid):
    items = [html.Div([html.Span(p.get("project_label") or p.get("project_id", "—"),
                                 className="fw-semibold"),
                       " — ",
                       html.Span(p.get("role") or "participant", className="text-muted small")],
                      className="mb-1")
             for p in pf] or [html.Div("no participants", className="text-muted small")]
    return html.Span([
        html.Span(f"{count} ", className="me-1"),
        html.I(className="bi bi-people-fill", id=pid,
               style={"cursor": "pointer", "color": TEAL}),
        dbc.Popover([dbc.PopoverHeader("Participants"), dbc.PopoverBody(items)],
                    target=pid, trigger="hover focus", placement="left"),
    ])


def build_overview(feds, participants):
    header = html.Thead(html.Tr([
        html.Th("Federation"), html.Th("Strategy"), html.Th("Privacy"),
        html.Th("Rounds"), html.Th("Participants"), html.Th("Status")]))
    rows = []
    for f in feds:
        pf = _parts_for(f, participants)
        pc = len(pf)
        pid = "fl-parts-" + str(f.get("id"))
        rows.append(html.Tr([
            html.Td([html.Strong(f.get("name") or f.get("slug")),
                     html.Div(f.get("slug"), className="text-muted small")]),
            html.Td(dbc.Badge(_strategy_label(f.get("aggregation_strategy")), color="light",
                              text_color="dark", className="border")),
            html.Td(_priv_label(f)),
            html.Td(_rounds_bar(f.get("rounds_completed"), f.get("rounds_planned"))),
            html.Td(_participants_cell(pc, pf, pid), className="text-center"),
            html.Td(_status_badge(f.get("status") or "planning")),
        ]))
    return dbc.Table([header, html.Tbody(rows)], hover=True, responsive=True, className="align-middle")


def _participants_table(parts):
    header = html.Thead(html.Tr([
        html.Th("Project"), html.Th("Role"), html.Th("Local samples"), html.Th("Last round")]))
    rows = []
    for p in parts:
        ds = p.get("local_dataset_size")
        rows.append(html.Tr([
            html.Td(p.get("project_label") or p.get("project_id", "—")), html.Td(_status_badge(p.get("role") or "participant")),
            html.Td(f"{ds:,}" if isinstance(ds, int) else "—", className="text-end"),
            html.Td(str(p.get("last_contribution_round") or "—"), className="text-center")]))
    return dbc.Table([header, html.Tbody(rows)], hover=True, size="sm", className="align-middle mb-0")


def build_detail(fed, participants, rounds=None):
    if not fed:
        return dbc.Alert("Select a federation to see its detail.", color="light", className="border")
    parts = _parts_for(fed, participants)
    total = sum((p.get("local_dataset_size") or 0) for p in parts)
    header = dbc.Card(dbc.CardBody(dbc.Row([
        dbc.Col([
            html.Div([html.H5(fed.get("name") or fed.get("slug"), className="d-inline me-2"),
                      _status_badge(fed.get("status") or "planning")]),
            html.Div([
                html.Span(_strategy_label(fed.get("aggregation_strategy")), className="text-muted small me-3"),
                html.Span(f"privacy: {_priv_label(fed)}", className="text-muted small me-3"),
                html.Span(f"slug: {fed.get('slug')}", className="text-muted small"),
            ], className="mt-1"),
        ], md=8),
        dbc.Col([
            dbc.Button([html.I(className="bi bi-pencil me-1"), "Edit"], id="fl-edit",
                       color="outline-primary", size="sm", className="me-2"),
            dbc.Button([html.I(className="bi bi-trash me-1"), "Delete"], id="fl-delete",
                       color="outline-danger", size="sm"),
        ], md=4, className="text-md-end"),
    ])), className="shadow-sm mb-3")

    kpis = dbc.Row([
        dbc.Col(_kpi("Participants", str(len(parts))), md=3),
        dbc.Col(_kpi("Rounds", f"{fed.get('rounds_completed', 0)} / {fed.get('rounds_planned', 0)}"), md=3),
        dbc.Col(_kpi("Total samples", f"{total:,}"), md=3),
        dbc.Col(_kpi("Strategy", _strategy_label(fed.get("aggregation_strategy"))), md=3),
    ], className="g-3 mb-3")

    rfed = _rounds_for(fed, rounds)
    has_rounds = bool(rfed)
    conv = _convergence_fig_real(rfed) if has_rounds else _convergence_fig(fed.get("rounds_completed"))
    contrib = (_contribution_fig_real(rfed)
               if any(_contrib_dict(r) for r in rfed)
               else _contribution_fig(parts, fed.get("rounds_completed")))
    tag = "live" if has_rounds else "representative"
    charts = dbc.Row([
        dbc.Col(_panel(f"Convergence — global model per round ({tag})",
                       dcc.Graph(figure=conv, config={"displayModeBar": False})), lg=6),
        dbc.Col(_panel(f"Contribution weight per round ({tag})",
                       dcc.Graph(figure=contrib, config={"displayModeBar": False})), lg=6),
    ], className="g-3 mb-3")

    bottom = dbc.Row([
        dbc.Col(_panel("Participants", _participants_table(parts)), lg=5),
        dbc.Col(_panel("Local dataset sizes",
                       dcc.Graph(figure=_dataset_fig(parts), config={"displayModeBar": False})), lg=4),
        dbc.Col(_config_panel(fed), lg=3),
    ], className="g-3")
    return html.Div([header, kpis, charts, bottom])


def _modal():
    def field(label, comp):
        return dbc.Row([dbc.Label(label, width=4), dbc.Col(comp, width=8)], className="mb-2")
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id="fl-modal-title")),
        dbc.ModalBody([
            field("Name", dbc.Input(id="fl-in-name", placeholder="Penicillin yield FL")),
            field("Slug", dbc.Input(id="fl-in-slug", placeholder="penicillin_yield_fed")),
            field("Strategy", dcc.Dropdown(id="fl-in-strategy",
                  options=[{"label": l, "value": v} for l, v in STRATEGIES], value="fedavg")),
            field("Privacy", dcc.Dropdown(id="fl-in-privacy",
                  options=[{"label": s, "value": s} for s in PRIVACY], value="none")),
            field("Epsilon (ε)", dbc.Input(id="fl-in-epsilon", type="number", placeholder="3.0")),
            field("Rounds planned", dbc.Input(id="fl-in-rounds", type="number", value=10)),
            field("Status", dcc.Dropdown(id="fl-in-status",
                  options=[{"label": s, "value": s} for s in STATUSES], value="planning")),
            html.Div(id="fl-modal-msg", className="small text-danger mt-1"),
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="fl-modal-cancel", color="secondary", outline=True),
            dbc.Button("Save", id="fl-modal-save", color="primary"),
        ]),
    ], id="fl-modal", is_open=False)


def _sdk_callout():
    return dbc.Card(dbc.CardBody(dbc.Row([
        dbc.Col(html.I(className="bi bi-box-seam",
                       style={"fontSize": "30px", "color": TEAL}),
                width="auto", className="align-self-center"),
        dbc.Col([
            html.Div([html.Strong("Participate with the STAMM SDK"),
                      dbc.Badge("Python", color="light", text_color="dark",
                                className="ms-2 border")]),
            html.Div("Labs train the shared model locally and contribute their "
                     "updates through the client library — no raw data leaves the site.",
                     className="text-muted small mb-1"),
            html.Code("pip install stamm-sdk",
                      style={"background": "#eef6f6", "color": DEEP,
                             "padding": "3px 8px", "borderRadius": "4px"}),
        ], className="align-self-center"),
        dbc.Col(dbc.Button([html.I(className="bi bi-box-arrow-up-right me-1"),
                            "View on PyPI"],
                           href="https://pypi.org/project/stamm-sdk/", target="_blank",
                           color="primary", size="sm"),
                width="auto", className="align-self-center text-md-end"),
    ], className="g-2 align-items-center")),
        className="shadow-sm mb-3", style={"borderLeft": f"4px solid {TEAL}"})


def federated_learning_layout(session_data=None):
    feds, session_data = fl.list_federations(session_data) if session_data else ([], session_data)
    parts, session_data = fl.list_participants(session_data) if session_data else ([], session_data)
    rounds, session_data = fl.list_rounds(session_data) if session_data else ([], session_data)
    labels, session_data = fl.project_label_map(session_data) if session_data else ({}, session_data)
    _apply_labels(parts, labels)
    live = bool(feds)
    if not live:
        feds, parts = _STATIC_FEDS, _STATIC_PARTS

    note_txt = ("Live — reading federations from the registry API." if live else
                "Static preview — the API returned no federations yet (apply the FL "
                "seed, or add one below). Figures use representative data.")
    note = dbc.Alert([html.I(className="bi bi-broadcast me-2" if live else "bi bi-info-circle me-2"),
                      note_txt], color=("success" if live else "info"), className="py-2 small")

    first = feds[0] if feds else None
    return dbc.Container([
        dcc.Store(id="fl-store", data={"federations": feds, "participants": parts, "rounds": rounds, "live": live}),
        dcc.Store(id="fl-editing-id", data=None),
        dcc.ConfirmDialog(id="fl-delete-confirm",
                          message="Delete this federation? This cannot be undone."),
        dbc.Toast(id="fl-toast", header="Federated Learning", is_open=False, dismissable=True,
                  duration=4000, icon="primary",
                  style={"position": "fixed", "top": 20, "right": 20, "zIndex": 1990}),
        _modal(),

        dbc.Row([
            dbc.Col(html.H3("Federated Learning", className="mb-1", style={"color": SLATE}), md=8),
            dbc.Col(dbc.Button([html.I(className="bi bi-plus-lg me-1"), "Add federation"],
                               id="fl-add", color="primary"), md=4, className="text-md-end align-self-center"),
        ]),
        html.P("Collaborative training across labs without sharing raw data — each "
               "site trains locally, only model updates are aggregated.", className="text-muted"),
        note,
        _sdk_callout(),
        html.H5("Federations", className="mb-2 mt-3"),
        html.Div(build_overview(feds, parts), id="fl-overview"),
        html.Hr(className="my-4"),
        dbc.Row([
            dbc.Col(html.H5("Federation detail", className="mb-0 align-self-center"), md=6),
            dbc.Col(dcc.Dropdown(id="fl-select", options=fed_options(feds),
                                 value=first.get("id") if first else None, clearable=False), md=6),
        ], className="mb-3 align-items-center"),
        html.Div(build_detail(first, parts, rounds), id="fl-detail"),
        html.Div(style={"height": "30px"}),
    ], fluid=True, className="p-4")
