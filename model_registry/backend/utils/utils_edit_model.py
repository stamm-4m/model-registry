import logging
import uuid
from datetime import datetime

import dash_bootstrap_components as dbc

logger = logging.getLogger(__name__)

def normalize_date(value):
    if not value:
        return None

    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        pass
    try:
        return datetime.strptime(value, "%d-%m-%Y").date().isoformat()
    except ValueError:
        return None
    
def get_value_from_list_of_dicts(data, key, default=""):
    if not isinstance(data, list):
        return default
    for item in data:
        if isinstance(item, dict) and key in item:
            return item[key]
    return default

def package_row(index, package="", version=""):
    return dbc.Row(
        [
            dbc.Col(
                dbc.FormFloating(
                    [
                        dbc.Input(
                            id={"type": "package-name", "index": index},
                            type="text",
                            placeholder="Package name",
                            value=package,
                        ),
                        dbc.Label("Package"),
                    ]
                ),
                md=5,
            ),
            dbc.Col(
                dbc.FormFloating(
                    [
                        dbc.Input(
                            id={"type": "package-version", "index": index},
                            type="text",
                            placeholder="Version",
                            value=version,
                        ),
                        dbc.Label("Version"),
                    ]
                ),
                md=5,
            ),
            dbc.Col(
                dbc.Button(
                    "🗑️",
                    id={"type": "remove-package", "index": index},
                    color="danger",
                    outline=True,
                    className="mt-2",
                ),
                md=2,
            ),
        ],
        id={"type": "package-row", "index": index},
        className="mb-2",
        align="center",
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
                        ),
                        dbc.Label("Description"),
                    ]
                ),

                dbc.Button(
                    "🗑 Remove feature",
                    id={"type": "remove-feature", "fid": fid},
                    color="danger",
                    outline=True,
                    size="sm",
                    className="mt-3",
                    type="button",
                ),
            ]
        ),
        className="mb-3 shadow-sm",
    )

        
def feature_item(feature):
    return dbc.AccordionItem(
        item_id=feature["id"],
        title=feature["name"] or "New feature",
        children=[feature_card(feature)],
    )

def new_feature():
    return {
        "id": str(uuid.uuid4()),
        "name": "",
        "type": "",
        "units": "",
        "lag": 0,
        "feature_scaling": "none",
        "expected_range": {"min": None, "max": None},
        "description": "",
    }

def normalize_features(features):
    normalized = []

    for f in features or []:
        f = f.copy()
        if "id" not in f:
            f["id"] = str(uuid.uuid4())
        normalized.append(f)

    return normalized

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
                        ),
                        dbc.Label("Description"),
                    ]
                ),

                dbc.Button(
                    "🗑 Remove output",
                    id={"type": "remove-output", "fid": fid},
                    color="danger",
                    outline=True,
                    size="sm",
                    className="mt-3",
                    type="button",
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

def new_output():
    return {
        "id": str(uuid.uuid4()),
        "name": "",
        "description": "",
        "units": "",
        "forecast_horizon": 0,
        "feature_scaling": "none",
        "expected_range": {"min": None, "max": None},
    }