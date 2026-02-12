import logging
from dash import html

import dash_bootstrap_components as dbc

logger = logging.getLogger(__name__)

def package_row(index, package="", version=""):
    return dbc.Row(
        [
            dbc.Col(
                html.Div([
                        dbc.Label(
                            "Package",
                            className="fw-semibold"
                            
                        ),
                        html.Div(children=package,className="fw-bold text-muted")
                    ]
                ),
                md=5,
            ),
            dbc.Col(
                html.Div([
                        dbc.Label(
                            "Version",
                            className="fw-semibold"
                        ),
                        html.Div(children=version,className="fw-bold text-muted")
                    ]
                ),
                md=5,
            ),
            
        ],
        className="mb-2",
        align="center",
    )

def feature_item(feature):
    return dbc.AccordionItem(
        item_id=feature["id"],
        title=feature["name"] or "New feature",
        children=[feature_card(feature)],
    )

def feature_card(feature):
    fid = feature["id"]

    return dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.FormFloating(
                                [
                                    dbc.Input(
                                        id={"type": "feature-name", "fid": fid},
                                        value=feature.get("name", ""),
                                        placeholder="Feature name",
                                        disabled=True
                                    ),
                                    dbc.Label("Name"),
                                ]
                            ),
                            md=6,
                        ),
                        dbc.Col(
                            dbc.FormFloating(
                                [
                                    dbc.Input(
                                        id={"type": "feature-type", "fid": fid},
                                        value=feature.get("type", ""),
                                        placeholder="Type",
                                        disabled=True
                                    ),
                                    dbc.Label("Type"),
                                ]
                            ),
                            md=6,
                        ),
                    ],
                    className="mb-3",
                ),

                dbc.Row(
                    [
                        dbc.Col(
                            dbc.FormFloating(
                                [
                                    dbc.Input(
                                        id={"type": "feature-units", "fid": fid},
                                        value=feature.get("units", ""),
                                        placeholder="Units",
                                        disabled=True
                                    ),
                                    dbc.Label("Units"),
                                ]
                            ),
                            md=3,
                        ),
                        dbc.Col(
                            dbc.FormFloating(
                                [
                                    dbc.Input(
                                        id={"type": "feature-lag", "fid": fid},
                                        type="number",
                                        value=feature.get("lag", 0),
                                        placeholder="Lag",
                                        disabled=True
                                    ),
                                    dbc.Label("Lag"),
                                ]
                            ),
                            md=2,
                        ),
                        dbc.Col(
                            dbc.FormFloating(
                                [
                                    dbc.Select(
                                        id={"type": "feature-scaling", "fid": fid},
                                        options=[
                                            {"label": "None", "value": "none"},
                                            {"label": "Standard", "value": "standard"},
                                            {"label": "Min-Max", "value": "minmax"},
                                        ],
                                        value=feature.get("feature_scaling", "none"),
                                        disabled=True
                                    ),
                                    dbc.Label("Scaling"),
                                ]
                            ),
                            md=3,
                        ),

                        dbc.Col(
                            dbc.FormFloating(
                                [
                                    dbc.Input(
                                        id={"type": "feature-min", "fid": fid},
                                        type="number",
                                        value=feature.get("expected_range", {}).get("min"),
                                        placeholder="Min",
                                        disabled=True
                                    ),
                                    dbc.Label("Min"),
                                ]
                            ),
                            md=2,
                        ),
                        dbc.Col(
                            dbc.FormFloating(
                                [
                                    dbc.Input(
                                        id={"type": "feature-max", "fid": fid},
                                        type="number",
                                        value=feature.get("expected_range", {}).get("max"),
                                        placeholder="Max",
                                        disabled=True
                                    ),
                                    dbc.Label("Max"),
                                ]
                            ),
                            md=2,
                        ),
                    ],
                    className="mb-3",
                ),

                dbc.FormFloating(
                    [
                        dbc.Textarea(
                            id={"type": "feature-description", "fid": fid},
                            value=feature.get("description", ""),
                            placeholder="Description",
                            style={"height": "80px"},
                            disabled=True
                        ),
                        dbc.Label("Description"),
                    ]
                ),
            ]
        ),
        className="mb-3 shadow-sm",
    )

###
# outputs
###
def output_card(fid, output=None):
    output = output or {}

    return dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.FormFloating(
                                [
                                    dbc.Input(
                                        id={"type": "output-name", "fid": fid},
                                        value=output.get("name", ""),
                                        placeholder="Output name",
                                        disabled=True
                                    ),
                                    dbc.Label("Name"),
                                ]
                            ),
                            md=6,
                        ),
                        dbc.Col(
                            dbc.FormFloating(
                                [
                                    dbc.Input(
                                        id={"type": "output-units", "fid": fid},
                                        value=output.get("units", ""),
                                        placeholder="Units",
                                        disabled=True
                                    ),
                                    dbc.Label("Units"),
                                ]
                            ),
                            md=6,
                        ),
                    ],
                    className="mb-3",
                ),

                dbc.Row(
                    [
                        dbc.Col(
                            dbc.FormFloating(
                                [
                                    dbc.Input(
                                        id={"type": "output-horizon", "fid": fid},
                                        type="number",
                                        value=output.get("forecast_horizon", 0),
                                        placeholder="Forecast horizon",
                                        disabled=True
                                    ),
                                    dbc.Label("Forecast horizon"),
                                ]
                            ),
                            md=4,
                        ),
                        dbc.Col(
                            dbc.FormFloating(
                                [
                                    dbc.Select(
                                        id={"type": "output-scaling", "fid": fid},
                                        options=[
                                            {"label": "None", "value": "none"},
                                            {"label": "Standard", "value": "standard"},
                                            {"label": "Min-Max", "value": "minmax"},
                                        ],
                                        value=output.get("feature_scaling", "none"),
                                        disabled=True
                                    ),
                                    dbc.Label("Scaling"),
                                ]
                            ),
                            md=4,
                        ),
                        dbc.Col(
                            dbc.FormFloating(
                                [
                                    dbc.Input(
                                        id={"type": "output-min", "fid": fid},
                                        type="number",
                                        value=output.get("expected_range", {}).get("min"),
                                        placeholder="Min",
                                        disabled=True
                                    ),
                                    dbc.Label("Min"),
                                ]
                            ),
                            md=2,
                        ),
                        dbc.Col(
                            dbc.FormFloating(
                                [
                                    dbc.Input(
                                        id={"type": "output-max", "fid": fid},
                                        type="number",
                                        value=output.get("expected_range", {}).get("max"),
                                        placeholder="Max",
                                        disabled=True
                                    ),
                                    dbc.Label("Max"),
                                ]
                            ),
                            md=2,
                        ),
                    ],
                    className="mb-3",
                ),

                dbc.FormFloating(
                    [
                        dbc.Textarea(
                            id={"type": "output-description", "fid": fid},
                            value=output.get("description", ""),
                            placeholder="Description",
                            style={"height": "80px"},
                            disabled=True
                        ),
                        dbc.Label("Description"),
                    ]
                ),

                
            ]
        ),
        className="mb-3 shadow-sm",
    )
def output_item(output):
    fid = output["id"]

    title = output.get("name") or "New output"

    return dbc.AccordionItem(
        item_id=fid,
        title=title,
        children=[output_card(fid, output)],
    )