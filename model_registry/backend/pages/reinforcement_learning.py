"""Reinforcement Learning — registry view (static / representative data).

Greenfield domain framed around bioprocess control: an agent learns a policy
that sets bioreactor actuators (e.g. feed rate) to maximise penicillin yield
while limiting substrate cost, trained against the IndPenSim simulator. Static
for now; a future `rl_policies` / `rl_episodes` schema + service would make it
live (mirrors the FL/XAI patterns).
"""
import math

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

TEAL = "#00a3a6"
DEEP = "#007E82"
SLATE = "#275662"
MUTED = "#9aa0a6"

_POLICIES = [
    {"name": "pen_feed_ppo", "algo": "PPO", "env": "IndPenSim-v0",
     "action": "feed_rate (continuous)", "episodes": "5,000", "reward": "312.4",
     "status": "training"},
    {"name": "temp_do_sac", "algo": "SAC", "env": "IndPenSim-v0",
     "action": "T + DO setpoints", "episodes": "8,200", "reward": "298.7",
     "status": "trained"},
    {"name": "feed_dqn", "algo": "DQN", "env": "IndPenSim-v0",
     "action": "feed step (discrete)", "episodes": "12,000", "reward": "271.0",
     "status": "trained"},
]


def _base(fig, height=300, title=None):
    fig.update_layout(
        template="plotly_white", height=height,
        margin=dict(l=10, r=10, t=42 if title else 12, b=10),
        title=dict(text=title, font=dict(size=13)) if title else None,
        font=dict(size=12), legend=dict(orientation="h", y=-0.2))
    return fig


def _status_badge(s):
    color = {"training": "success", "trained": "secondary", "deployed": "info"}.get(s, "light")
    return dbc.Badge(s, color=color, className="text-uppercase")


def _kpi(label, value, sub=None):
    return dbc.Card(dbc.CardBody([
        html.Div(label, className="text-muted small text-uppercase"),
        html.Div(value, style={"fontSize": "22px", "fontWeight": 600, "color": SLATE}),
        html.Div(sub, className="text-muted small") if sub else None,
    ]), className="shadow-sm h-100")


def _panel(title, body):
    return dbc.Card(dbc.CardBody([html.Div(title, className="fw-semibold mb-2"), body]),
                    className="shadow-sm h-100")


def _spec_card(title, items):
    lis = [html.Li([html.Strong(k + ": "), v]) for k, v in items]
    return _panel(title, html.Ul(lis, className="mb-0 small", style={"paddingLeft": "18px"}))


# ---- figures ----
def _reward_curve_fig():
    import random
    rng = random.Random(7)
    n = 120
    eps = [i * 42 for i in range(n)]          # up to ~5000 episodes
    smooth, raw, v = [], [], -40.0
    for i in range(n):
        v += (330 - v) * 0.045                # asymptotic learning toward ~330
        smooth.append(v)
        raw.append(v + rng.uniform(-38, 38))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=eps, y=raw, mode="lines", line=dict(color="#c9e3e4", width=1),
                             name="episode reward", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=eps, y=smooth, mode="lines", line=dict(color=TEAL, width=3),
                             name="moving average",
                             hovertemplate="ep %{x}: %{y:.0f}<extra></extra>"))
    fig.update_xaxes(title="training episode")
    fig.update_yaxes(title="episode reward")
    return _base(fig, 300)


def _rollout_fig():
    # one batch (~24 sampled steps over the fermentation): feed action + DO state
    steps = list(range(24))
    feed = [0.05 + 0.11 * (1 / (1 + math.exp(-(t - 8) / 2.0))) - (0.02 if t > 18 else 0) for t in steps]
    do = [7.8 - 3.2 * (1 / (1 + math.exp(-(t - 9) / 2.5))) + 0.3 * math.sin(t / 2) for t in steps]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=steps, y=feed, mode="lines", name="feed rate (action)",
                             line=dict(color=TEAL, width=3), yaxis="y1"))
    fig.add_trace(go.Scatter(x=steps, y=do, mode="lines", name="dissolved O₂ (state)",
                             line=dict(color=SLATE, width=2, dash="dot"), yaxis="y2"))
    fig.update_layout(
        yaxis=dict(title=dict(text="feed rate", font=dict(color=TEAL)),
                   tickfont=dict(color=TEAL)),
        yaxis2=dict(title=dict(text="DO (mg/L)", font=dict(color=SLATE)),
                    tickfont=dict(color=SLATE), overlaying="y", side="right"))
    fig.update_xaxes(title="batch time step")
    return _base(fig, 300)


def _compare_fig():
    metrics = ["Penicillin yield", "Episode reward", "Substrate used"]
    rl = [1.11, 1.0, 0.92]          # normalised to baseline = 1.0
    base = [1.0, 1.0, 1.0]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=metrics, y=rl, name="RL policy (PPO)", marker_color=TEAL,
                         hovertemplate="%{x}: %{y:.2f}×<extra></extra>"))
    fig.add_trace(go.Bar(x=metrics, y=base, name="PID / operator baseline", marker_color=MUTED,
                         hovertemplate="%{x}: %{y:.2f}×<extra></extra>"))
    fig.add_hline(y=1.0, line_width=1, line_dash="dot", line_color="#cbd5e1")
    fig.update_yaxes(title="relative to baseline (×)")
    fig.update_layout(barmode="group")
    return _base(fig, 300)


def _registry_table():
    header = html.Thead(html.Tr([
        html.Th("Policy"), html.Th("Algorithm"), html.Th("Environment"),
        html.Th("Action space"), html.Th("Episodes"), html.Th("Mean reward"), html.Th("Status")]))
    rows = []
    for p in _POLICIES:
        rows.append(html.Tr([
            html.Td(html.Strong(p["name"])),
            html.Td(dbc.Badge(p["algo"], color="light", text_color="dark", className="border")),
            html.Td(p["env"]), html.Td(p["action"]),
            html.Td(p["episodes"], className="text-end"),
            html.Td(p["reward"], className="text-end"),
            html.Td(_status_badge(p["status"]))]))
    return dbc.Table([header, html.Tbody(rows)], hover=True, responsive=True, className="align-middle")


def reinforcement_learning_layout(session_data=None):
    note = dbc.Alert(
        "Static preview — representative data. RL is a new domain: a future "
        "rl_policies / rl_episodes schema + service would make this live "
        "(same pattern as the FL and XAI views).",
        color="info", className="py-2 small")

    detail_header = dbc.Card(dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.Div([html.H5("pen_feed_ppo", className="d-inline me-2"),
                          dbc.Badge("PPO", color="primary", className="me-1"),
                          _status_badge("training")]),
                html.Div([
                    html.Span("env: IndPenSim-v0", className="text-muted small me-3"),
                    html.Span("goal: maximise penicillin yield − substrate cost", className="text-muted small"),
                ], className="mt-1"),
            ], md=12),
        ]),
    ]), className="shadow-sm mb-3")

    kpis = dbc.Row([
        dbc.Col(_kpi("Episodes", "5,000", "≈ 32 GPU-h"), md=3),
        dbc.Col(_kpi("Mean reward", "312.4", "last 100 episodes"), md=3),
        dbc.Col(_kpi("Best episode", "356.1", "round 4,780"), md=3),
        dbc.Col(_kpi("Yield uplift", "+11%", "vs PID baseline"), md=3),
    ], className="g-3 mb-3")

    specs = dbc.Row([
        dbc.Col(_spec_card("State (observation)", [
            ("Sensors", "temperature, pH, dissolved O₂"),
            ("Process", "biomass, substrate, vessel volume"),
            ("Phase", "fermentation stage"),
        ]), md=4),
        dbc.Col(_spec_card("Action", [
            ("Type", "continuous"),
            ("Variable", "sugar feed-rate setpoint"),
            ("Bounds", "0 – 0.20 L/h (safety-clipped)"),
        ]), md=4),
        dbc.Col(_spec_card("Reward", [
            ("Term +", "Δ penicillin concentration"),
            ("Term −", "λ · substrate consumed"),
            ("Penalty", "constraint violation (DO, pH)"),
        ]), md=4),
    ], className="g-3 mb-3")

    charts = dbc.Row([
        dbc.Col(_panel("Learning curve — reward over training", dcc.Graph(
            figure=_reward_curve_fig(), config={"displayModeBar": False})), lg=6),
        dbc.Col(_panel("Episode rollout — action vs. state", dcc.Graph(
            figure=_rollout_fig(), config={"displayModeBar": False})), lg=6),
    ], className="g-3 mb-3")

    compare = dbc.Row([
        dbc.Col(_panel("Learned policy vs. baseline controller", dcc.Graph(
            figure=_compare_fig(), config={"displayModeBar": False})), lg=12),
    ], className="g-3")

    return dbc.Container([
        html.H3("Reinforcement Learning", className="mb-1", style={"color": SLATE}),
        html.P("Agents that learn a control policy for the bioreactor — setting "
               "actuators to maximise a process reward, trained against the "
               "IndPenSim simulator.", className="text-muted"),
        note,
        html.H5("Policies", className="mb-2 mt-3"),
        _registry_table(),
        html.Hr(className="my-4"),
        html.H5("Policy detail", className="mb-3"),
        detail_header, kpis, specs, charts, compare,
        html.Div(style={"height": "30px"}),
    ], fluid=True, className="p-4")
