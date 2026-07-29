"""Dynamic Models — mechanistic/kinetic model registry (live list + CRUD).

Mirrors ML Soft Sensors: lists the dynamic models (from `/api/v1/dynamic_model`)
with add / edit / delete, and a detailed metadata view per model. The rich
metadata lives in the row's `information` JSON (type, process, state variables,
parameters, equations, assumptions, references, run conditions, calibration).
Simulation trajectories are representative for now (a lab runs the model
locally/microservice and uploads sims later; the registry then computes derived
variables). Static fallback if the API is empty. Callbacks in
`callbacks/callbacks_dynamic_models.py`.
"""
import json
import math

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_ag_grid as dag

from model_registry.backend.services import dynamic_models_service as dms

TEAL = "#00a3a6"
DEEP = "#007E82"
SLATE = "#275662"
WARN = "#e17055"
MUTED = "#9aa0a6"

TYPES = ["unstructured", "unstructured kinetic", "structured", "hybrid"]
STATUSES = ["draft", "calibrated", "deployed"]

_STATE_VARS = [
    ("X", "Biomass concentration", "g/L", "0.1", "Viable P. chrysogenum biomass"),
    ("S", "Substrate (glucose)", "g/L", "15.0", "Growth-limiting carbon source"),
    ("P", "Penicillin titer", "g/L", "0.0", "Product concentration"),
    ("DO", "Dissolved oxygen", "mg/L", "8.0", "Aeration / O2 limitation state"),
    ("V", "Broth volume", "L", "58000", "Working volume (fed-batch)"),
    ("CO2", "Off-gas CO2", "%", "0.04", "Metabolic activity indicator"),
]
_PARAMS = [
    ("mu_max", "0.11", "1/h", "fitted", "Maximum specific growth rate"),
    ("K_s", "0.15", "g/L", "literature", "Monod half-saturation (substrate)"),
    ("K_DO", "0.50", "mg/L", "literature", "O2 half-saturation constant"),
    ("Y_xs", "0.47", "g/g", "fitted", "Biomass yield on substrate"),
    ("Y_ps", "1.20", "g/g", "fitted", "Penicillin yield on substrate"),
    ("m_s", "0.014", "g/g/h", "literature", "Maintenance coefficient"),
    ("q_p_max", "0.0055", "g/g/h", "fitted", "Max specific penicillin production"),
    ("K_p", "2e-4", "g/L", "fitted", "Product-inhibition constant"),
    ("k_h", "0.010", "1/h", "literature", "Penicillin hydrolysis rate"),
    ("k_La", "120", "1/h", "fitted", "Oxygen transfer coefficient"),
    ("k_d", "0.008", "1/h", "fitted", "Biomass death/lysis rate"),
]
_EQUATIONS = ("dX/dt = (mu - k_d)*X\ndS/dt = -(1/Y_xs)*mu*X - m_s*X + F*S_f/V\n"
              "dP/dt = q_p*X - k_h*P\ndV/dt = F\n"
              "mu   = mu_max * S/(K_s+S) * DO/(K_DO+DO)\n"
              "q_p  = q_p_max * S/(K_s+S) * K_p/(K_p+P)")
_ASSUMPTIONS = [
    "Well-mixed single-compartment bioreactor.",
    "Temperature and pH held at setpoint by control loops.",
    "Single growth-limiting substrate (glucose).",
    "No explicit lag phase; morphology not resolved (unstructured).",
    "Oxygen transfer via constant k_La; no CO2 inhibition modelled.",
]


def _indpensim_info():
    return {
        "type": "unstructured kinetic", "process": "Penicillin fed-batch fermentation",
        "status": "calibrated",
        "state_variables": [{"symbol": s[0], "name": s[1], "units": s[2],
                             "initial": s[3], "description": s[4]} for s in _STATE_VARS],
        "parameters": [{"name": p[0], "value": p[1], "units": p[2],
                        "source": p[3], "description": p[4]} for p in _PARAMS],
        "equations": _EQUATIONS, "assumptions": _ASSUMPTIONS,
        "references": "Goldrick et al. 2015 - doi:10.1016/j.jbiotec.2014.10.029",
        "run_conditions": {"initial_conditions": "X=0.1, S=15, P=0 g/L; V=58 kL",
                           "feed_profile": "exponential (0-60 h) then constant",
                           "duration": "230 h", "solver": "CVODE (BDF), rtol 1e-6"},
        "calibration": [{"state": "Biomass X", "rmse": "1.8 g/L", "r2": "0.97", "vs": "batches 1-40"},
                        {"state": "Substrate S", "rmse": "0.6 g/L", "r2": "0.94", "vs": "batches 1-40"},
                        {"state": "Penicillin P", "rmse": "0.09 g/L", "r2": "0.96", "vs": "batches 1-40"}],
    }


_STATIC_MODELS = [
    {"id": "static-indpensim", "name": "IndPenSim penicillin", "version": "2.0",
     "url_endpoint": None, "information": _indpensim_info()},
    {"id": "static-ecoli", "name": "E. coli fed-batch", "version": "1.1",
     "url_endpoint": "http://r-api:8501/dynamic/ecoli",
     "information": {"type": "structured", "process": "Recombinant protein production",
                     "status": "calibrated",
                     "state_variables": [{"symbol": "X", "name": "Biomass", "units": "g/L", "initial": "0.5", "description": "E. coli DCW"},
                                         {"symbol": "S", "name": "Glucose", "units": "g/L", "initial": "20", "description": "Carbon source"},
                                         {"symbol": "A", "name": "Acetate", "units": "g/L", "initial": "0", "description": "Overflow metabolite"}],
                     "parameters": [{"name": "mu_max", "value": "0.55", "units": "1/h", "source": "fitted", "description": "Max growth rate"}],
                     "equations": "dX/dt = mu*X\ndS/dt = -q_s*X + F*S_f/V", "assumptions": ["Overflow metabolism above critical growth rate"],
                     "references": "internal calibration, TBI pilot plant",
                     "run_conditions": {"duration": "30 h", "solver": "LSODA"}, "calibration": []}},
    {"id": "static-monod", "name": "Monod biomass", "version": "1.0", "url_endpoint": None,
     "information": {"type": "unstructured", "process": "Generic microbial growth", "status": "draft",
                     "state_variables": [{"symbol": "X", "name": "Biomass", "units": "g/L", "initial": "0.1", "description": "Cell conc."},
                                         {"symbol": "S", "name": "Substrate", "units": "g/L", "initial": "10", "description": "Limiting nutrient"}],
                     "parameters": [{"name": "mu_max", "value": "0.4", "units": "1/h", "source": "literature", "description": "Max growth rate"}],
                     "equations": "dX/dt = mu*X\nmu = mu_max*S/(K_s+S)", "assumptions": ["Batch culture"],
                     "references": "Monod 1949", "run_conditions": {"duration": "24 h", "solver": "RK45"}, "calibration": []}},
]


# ---- helpers ----
def _info(m):
    info = (m or {}).get("information") or {}
    if isinstance(info, str):
        try:
            info = json.loads(info)
        except Exception:
            info = {}
    return info if isinstance(info, dict) else {}


def _base(fig, height=320):
    fig.update_layout(template="plotly_white", height=height,
                      margin=dict(l=10, r=10, t=12, b=10), font=dict(size=12),
                      legend=dict(orientation="h", y=-0.22))
    return fig


def _status_badge(s):
    color = {"calibrated": "success", "draft": "secondary", "deployed": "info",
             "fitted": "info", "literature": "light", "uploaded": "secondary",
             "endpoint": "primary", "remote": "primary"}.get(s, "light")
    tc = "dark" if s in ("literature",) else None
    return dbc.Badge(s or "—", color=color, text_color=tc, className="text-uppercase")


def _kpi(label, value, sub=None):
    return dbc.Card(dbc.CardBody([
        html.Div(label, className="text-muted small text-uppercase"),
        html.Div(value, style={"fontSize": "22px", "fontWeight": 600, "color": SLATE}),
        html.Div(sub, className="text-muted small") if sub else None,
    ]), className="shadow-sm h-100")


def _panel(title, body, tag=None):
    head = [html.Span(title, className="fw-semibold")]
    if tag:
        head.append(dbc.Badge(tag, color="light", text_color="secondary", className="ms-2 border"))
    return dbc.Card(dbc.CardBody([html.Div(head, className="mb-2"), body]),
                    className="shadow-sm h-100")


def _table(header, rows, **kw):
    return dbc.Table([html.Thead(html.Tr([html.Th(h) for h in header])),
                      html.Tbody([html.Tr([html.Td(c) for c in r]) for r in rows]
                                 or [html.Tr([html.Td("—") for _ in header])])],
                     hover=True, size="sm", className="align-middle mb-0", **kw)


def _sim():
    t = list(range(0, 232, 6))
    X, S, P = [], [], []
    for h in t:
        X.append(round(0.1 + 40.0 / (1 + math.exp(-(h - 70) / 22)), 3))
        S.append(round(max(15.0 * math.exp(-h / 45) + 0.4, 0.1), 3))
        P.append(round(2.1 / (1 + math.exp(-(h - 110) / 28)), 3))
    return t, X, S, P


def _traj_fig():
    t, X, S, P = _sim()
    mt = t[2::3]
    mp = [round(P[i] * (1.05 if i % 2 else 0.95), 3) for i in range(2, len(t), 3)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=X, name="Biomass X", line=dict(color=DEEP, width=3), yaxis="y1"))
    fig.add_trace(go.Scatter(x=t, y=S, name="Substrate S", line=dict(color=MUTED, width=2, dash="dot"), yaxis="y1"))
    fig.add_trace(go.Scatter(x=t, y=P, name="Penicillin P (sim)", line=dict(color=TEAL, width=3), yaxis="y2"))
    fig.add_trace(go.Scatter(x=mt, y=mp, name="P (measured)", mode="markers",
                             marker=dict(color=WARN, size=7, symbol="circle-open"), yaxis="y2"))
    fig.update_layout(yaxis=dict(title="X, S (g/L)"),
                      yaxis2=dict(title="P (g/L)", overlaying="y", side="right", showgrid=False),
                      xaxis=dict(title="fermentation time (h)"))
    return _base(fig, 340)


def _derived_fig():
    t, X, S, P = _sim()
    mu = [0.0]
    for i in range(1, len(t)):
        mu.append(round(max((math.log(X[i]) - math.log(X[i - 1])) / (t[i] - t[i - 1]), 0.0), 4))
    fig = go.Figure(go.Scatter(x=t, y=mu, line=dict(color=TEAL, width=3)))
    fig.update_xaxes(title="time (h)"); fig.update_yaxes(title="μ (1/h)")
    return _base(fig, 300)


# ---- builders shared by layout + callbacks ----
_GRID_COLS = [
    {"headerName": "Model", "field": "name", "flex": 2},
    {"headerName": "Type", "field": "type", "flex": 1},
    {"headerName": "Process", "field": "process", "flex": 2},
    {"headerName": "Version", "field": "version", "width": 90},
    {"headerName": "Status", "field": "status", "width": 110},
    {"headerName": "Details", "field": "details", "cellRenderer": "DetailsIconRenderer",
     "width": 80, "filter": False, "sortable": False},
    {"headerName": "Edit", "field": "edit", "cellRenderer": "EditIconRenderer",
     "width": 70, "filter": False, "sortable": False},
    {"headerName": "Delete", "field": "delete", "cellRenderer": "DeleteIconRenderer",
     "width": 80, "filter": False, "sortable": False},
]


def grid_rows(models):
    rows = []
    for m in models:
        info = _info(m)
        rows.append({"id": m.get("id"), "name": m.get("name") or "—",
                     "type": info.get("type", "—"), "process": info.get("process", "—"),
                     "version": m.get("version", "—"), "status": info.get("status", "draft"),
                     "details": "", "edit": "", "delete": ""})
    return rows


def dm_grid(models):
    return dag.AgGrid(
        id="dm-grid", columnDefs=_GRID_COLS, rowData=grid_rows(models),
        defaultColDef={"sortable": True, "filter": True, "resizable": True},
        dashGridOptions={"rowHeight": 45, "getRowId": "params.data.id"},
        columnSize="responsiveSizeToFit", style={"height": 280})


def build_detail(model):
    if not model:
        return dbc.Alert("Select a dynamic model to see its detail.", color="light", className="border")
    info = _info(model)
    svars = info.get("state_variables", [])
    params = info.get("parameters", [])
    run = info.get("run_conditions", {}) or {}
    calib = info.get("calibration", []) or []
    src = "endpoint" if model.get("url_endpoint") else "uploaded"

    header = dbc.Card(dbc.CardBody([
        html.Div([html.H5(model.get("name") or "—", className="d-inline me-2"),
                  dbc.Badge(info.get("type", "—"), color="primary", className="me-1"),
                  _status_badge(info.get("status", "draft"))]),
        html.Div([
            html.Span(f"process: {info.get('process', '—')}", className="text-muted small me-3"),
            html.Span(f"v{model.get('version', '—')}", className="text-muted small me-3"),
            html.Span(f"source: {src}"
                      + (f" ({model.get('url_endpoint')})" if model.get("url_endpoint") else ""),
                      className="text-muted small"),
        ], className="mt-1"),
    ]), className="shadow-sm mb-3")

    kpis = dbc.Row([
        dbc.Col(_kpi("State variables", str(len(svars))), md=3),
        dbc.Col(_kpi("Parameters", str(len(params))), md=3),
        dbc.Col(_kpi("Type", info.get("type", "—")), md=3),
        dbc.Col(_kpi("Status", info.get("status", "draft")), md=3),
    ], className="g-3 mb-3")

    definition = dbc.Row([
        dbc.Col(_panel("State variables", _table(
            ["Symbol", "Variable", "Units", "Initial", "Description"],
            [[v.get("symbol"), v.get("name"), v.get("units"), v.get("initial"), v.get("description")]
             for v in svars])), lg=6),
        dbc.Col(_panel("Parameters", _table(
            ["Parameter", "Value", "Units", "Source", "Description"],
            [[p.get("name"), p.get("value"), p.get("units"), _status_badge(p.get("source")), p.get("description")]
             for p in params])), lg=6),
    ], className="g-3 mb-3")

    equations = dbc.Row([
        dbc.Col(_panel("Governing equations", html.Pre(
            info.get("equations", "—"),
            style={"fontSize": "12px", "margin": 0, "whiteSpace": "pre-wrap",
                   "fontFamily": "var(--bs-font-monospace, monospace)"})), lg=6),
        dbc.Col(_panel("Assumptions", html.Ul(
            [html.Li(a) for a in info.get("assumptions", [])] or [html.Li("—")],
            className="mb-0 small", style={"paddingLeft": "18px"})), lg=6),
    ], className="g-3 mb-3")

    sim = dbc.Row([
        dbc.Col(_panel("State trajectories — measured vs simulated",
                       dcc.Graph(figure=_traj_fig(), config={"displayModeBar": False}),
                       tag="representative"), lg=7),
        dbc.Col(_panel("Derived — specific growth rate μ(t)", html.Div([
            dcc.Graph(figure=_derived_fig(), config={"displayModeBar": False}),
            html.Div("Registry-computed from the uploaded biomass trajectory.",
                     className="text-muted small mt-1"),
        ]), tag="registry-computed"), lg=5),
    ], className="g-3 mb-3")

    bottom = dbc.Row([
        dbc.Col(_panel("Calibration / validation", _table(
            ["State", "RMSE", "R²", "vs"],
            [[c.get("state"), c.get("rmse"), c.get("r2"), c.get("vs")] for c in calib])), lg=6),
        dbc.Col(_panel("Run conditions + references", html.Div([
            _table(["Setting", "Value"], [[k.replace("_", " "), v] for k, v in run.items()]),
            html.Div([html.Strong("References: "), info.get("references", "—")],
                     className="small text-muted mt-2"),
        ])), lg=6),
    ], className="g-3")

    return html.Div([header, kpis, definition, equations, sim, bottom])


_METADATA_TEMPLATE = json.dumps({
    "state_variables": [{"symbol": "X", "name": "Biomass", "units": "g/L",
                         "initial": "0.1", "description": ""}],
    "parameters": [{"name": "mu_max", "value": "0.4", "units": "1/h",
                    "source": "literature", "description": ""}],
    "equations": "dX/dt = mu*X", "assumptions": [], "references": "",
    "run_conditions": {"duration": "", "solver": ""}, "calibration": [],
}, indent=2)


def _modal():
    def field(label, comp):
        return dbc.Row([dbc.Label(label, width=3), dbc.Col(comp, width=9)], className="mb-2")
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id="dm-modal-title")),
        dbc.ModalBody([
            field("Name", dbc.Input(id="dm-in-name", placeholder="IndPenSim penicillin")),
            field("Version", dbc.Input(id="dm-in-version", value="1.0")),
            field("Type", dcc.Dropdown(id="dm-in-type",
                  options=[{"label": t, "value": t} for t in TYPES], value="unstructured kinetic")),
            field("Process", dbc.Input(id="dm-in-process", placeholder="Penicillin fed-batch")),
            field("Status", dcc.Dropdown(id="dm-in-status",
                  options=[{"label": s, "value": s} for s in STATUSES], value="draft")),
            field("Endpoint URL", dbc.Input(id="dm-in-endpoint",
                  placeholder="(optional) http://host/dynamic/...")),
            dbc.Label("Metadata (JSON: state variables, parameters, equations, …)",
                      className="small text-muted"),
            dbc.Textarea(id="dm-in-info", style={"height": "180px", "fontFamily": "monospace",
                                                 "fontSize": "12px"}),
            html.Div(id="dm-modal-msg", className="small text-danger mt-1"),
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="dm-modal-cancel", color="secondary", outline=True),
            dbc.Button("Save", id="dm-modal-save", color="primary"),
        ]),
    ], id="dm-modal", is_open=False, size="lg")


def dynamic_models_layout(session_data=None):
    models, session_data = dms.list_dynamic_models(session_data) if session_data else ([], session_data)
    live = bool(models)
    if not live:
        models = _STATIC_MODELS

    note = dbc.Alert(
        ("Live — reading dynamic models from the registry API. Simulation "
         "trajectories are representative until a run is uploaded." if live else
         "Static preview — the API returned no dynamic models (apply the seed, or add "
         "one). Trajectories are representative."),
        color=("success" if live else "info"), className="py-2 small")

    page_header = html.Div([
        html.Div([
            html.H2([html.I(className="bi bi-graph-up me-2 text-primary"), "Dynamic Models"],
                    className="page-title mb-1"),
            html.P("First-principles / kinetic models of the bioprocess — parameters, "
                   "equations, simulations and validation.", className="text-muted mb-0"),
        ], className="page-header-text"),
        html.Div([
            dbc.Badge([html.I(className="bi bi-diagram-3 me-1"),
                       f"{len(models)} model" + ("s" if len(models) != 1 else "")],
                      color="light", text_color="primary", className="me-2 px-3 py-2 border"),
            dbc.Button([html.I(className="bi bi-plus-lg me-1"), "Add dynamic model"],
                       id="dm-add", color="primary"),
        ], className="page-header-actions"),
    ], className="page-header d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2")

    return dbc.Container([
        dcc.Store(id="dm-store", data={"models": models, "live": live}),
        dcc.Store(id="dm-editing-id", data=None),
        dcc.Store(id="dm-delete-id", data=None),
        dcc.ConfirmDialog(id="dm-delete-confirm",
                          message="Delete this dynamic model? This cannot be undone."),
        dbc.Toast(id="dm-toast", header="Dynamic Models", is_open=False, dismissable=True,
                  duration=4000, icon="primary",
                  style={"position": "fixed", "top": 20, "right": 20, "zIndex": 1990}),
        _modal(),
        page_header,
        note,
        dbc.Card(dbc.CardBody(dm_grid(models)), className="shadow-sm mb-4"),
        html.Div(style={"height": "30px"}),
    ], fluid=True, className="p-4")


def _find_model(model_id, session_data=None):
    """Resolve a dynamic model by id — live via the API, else static fallback."""
    models, session_data = (dms.list_dynamic_models(session_data)
                            if session_data else ([], session_data))
    if not models:
        models = _STATIC_MODELS
    return next((m for m in models if str(m.get("id")) == str(model_id)), None)


def dynamic_model_detail_layout(model_id, session_data=None):
    """Full-page detail view for a single dynamic model (opened from the grid)."""
    model = _find_model(model_id, session_data)

    back = dbc.Button([html.I(className="bi bi-arrow-left me-1"), "Back to Dynamic Models"],
                      href="/dynamic-models", color="link", className="px-0 text-decoration-none")

    if not model:
        return dbc.Container([
            back,
            dbc.Alert("Dynamic model not found. It may have been deleted.",
                      color="warning", className="mt-3"),
        ], fluid=True, className="p-4")

    page_header = html.Div([
        html.Div([
            html.H2([html.I(className="bi bi-graph-up me-2 text-primary"),
                     model.get("name") or "Dynamic model"], className="page-title mb-1"),
            html.P("First-principles / kinetic model — parameters, equations, "
                   "simulations and validation.", className="text-muted mb-0"),
        ], className="page-header-text"),
        html.Div(back, className="page-header-actions"),
    ], className="page-header d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2")

    return dbc.Container([
        page_header,
        build_detail(model),
        html.Div(style={"height": "30px"}),
    ], fluid=True, className="p-4")
