"""Callbacks for template selection and configuration in model upload."""

import json
import logging
from dash import Input, Output, State, html, ctx, ALL, callback, MATCH
import dash_bootstrap_components as dbc
from model_registry.backend.utils.utils_template_ui import (
    get_template_fields_by_algorithm,
    STAMM_ALGORITHMS,
)


logger = logging.getLogger(__name__)

# All possible template field IDs across all algorithms
_ALL_TEMPLATE_FIELD_IDS = [
    # Random Forest, Decision Tree, Gradient Boosting
    "template-n-estimators", "template-max-depth", "template-min-samples-split",
    "template-max-features", "template-criterion", "template-learning-rate",
    
    # SVM
    "template-kernel", "template-c", "template-gamma",
    
    # Neural Network, RNN
    "template-hidden-layers", "template-activation", "template-batch-size",
    "template-hidden-units", "template-num-layers", "template-dropout",
    
    # Cubist, M5
    "template-committees", "template-instance-corrections", "template-min-instances",
    "template-pruned", "template-smoothed",
    
    # Linear Regression, Logistic Regression
    "template-fit-intercept", "template-positive", "template-penalty", "template-solver",
    
    # PLS, PCA
    "template-n-components", "template-scale", "template-whiten",
    
    # K-Means
    "template-n-clusters", "template-init", "template-max-iter",
    
    # Gaussian Process
    "template-alpha",
    
    # Ensemble
    "template-ensemble-method", "template-num-estimators",
    
    # CNN
    "template-num-filters", "template-kernel-size", "template-pool-size",
    
    # Transformer
    "template-d-model", "template-num-heads",
    
    # Custom
    "template-custom-config",
]


def register_template_callbacks(app):
    """Register all template-related callbacks."""

    # Callback: Show/hide and populate template config fields
    @app.callback(
        Output("template-config-container", "style"),
        Output("template-config-fields", "children"),
        Output("template-config-store", "data"),
        Input("template-algorithm-selector", "value"),
        prevent_initial_call=True,
    )
    def update_template_fields(selected_algorithm):
        """Update template fields based on selected algorithm."""
        if not selected_algorithm:
            return (
                {"display": "none"},
                html.P("Select an algorithm to see template-specific fields.", 
                       className="text-muted"),
                {}
            )

        # Get template fields for this algorithm
        fields = get_template_fields_by_algorithm(selected_algorithm)
        if not fields:
            return (
                {"display": "none"},
                html.P(f"No template fields defined for {selected_algorithm}.", 
                       className="text-muted"),
                {}
            )

        # Build field components
        field_components = []
        field_data = {"algorithm": selected_algorithm, "fields": {}}

        for field in fields:
            field_id = field.get("id")
            field_type = field.get("type", "number")
            field_name = field.get("name", "")
            field_value = field.get("value")
            field_required = field.get("required", False)
            field_placeholder = field.get("placeholder", "")

            # Store field metadata
            field_data["fields"][field_id] = {
                "name": field_name,
                "type": field_type,
                "required": field_required,
                "default_value": field_value,
            }

            # Create appropriate input component
            if field_type == "checkbox":
                component = html.Div(
                    [
                        dbc.Checkbox(
                            id=field_id,
                            value=field_value or False,
                            className="me-2",
                        ),
                        html.Label(field_name, htmlFor=field_id),
                    ],
                    className="d-flex align-items-center mb-3",
                )
            elif field_type == "textarea":
                component = dbc.FormFloating([
                    dbc.Textarea(
                        id=field_id,
                        placeholder=field_placeholder or field_name,
                        style=field.get("style", {}),
                        value=field_value or "",
                    ),
                    dbc.Label(field_name),
                ], className="mb-3")
            else:
                # Number, text, etc.
                input_props = {
                    "id": field_id,
                    "type": field_type,
                    "placeholder": field_placeholder or field_name,
                    "value": field_value or "",
                }
                if "step" in field:
                    input_props["step"] = field["step"]
                if "min" in field:
                    input_props["min"] = field["min"]
                if "max" in field:
                    input_props["max"] = field["max"]

                component = dbc.FormFloating([
                    dbc.Input(**input_props),
                    dbc.Label(field_name),
                ], className="mb-3")

            # Add required marker if needed
            if field_required:
                field_components.append(
                    html.Div([
                        component,
                        html.Small(
                            "* Required field",
                            className="text-danger ms-2 d-block"
                        )
                    ])
                )
            else:
                field_components.append(component)

        return (
            {"display": "block"},
            field_components,
            field_data,
        )

    # Callback: Collect template values before save (triggered by save button)
    @app.callback(
        Output("template-config-store", "data", allow_duplicate=True),
        Input("save-ml-model-config", "n_clicks"),
        State("template-algorithm-selector", "value"),
        State("template-config-store", "data"),
        # Include all possible template field states
        *[State(field_id, "value") for field_id in _ALL_TEMPLATE_FIELD_IDS],
        prevent_initial_call=True,
    )
    def collect_template_config(n_clicks, selected_algorithm, current_store, *field_values):
        """Collect all template field values into store before saving."""
        if not selected_algorithm or not current_store:
            return current_store or {}

        # Map field IDs to their values
        field_value_map = dict(zip(_ALL_TEMPLATE_FIELD_IDS, field_values))

        # Get the fields for this algorithm
        fields = get_template_fields_by_algorithm(selected_algorithm)
        field_ids = [f.get("id") for f in fields]

        # Build config object with collected values
        config = {
            "algorithm": selected_algorithm,
            "fields": {},
            "values": {}
        }

        for field in fields:
            field_id = field.get("id")
            field_name = field.get("name", "")
            field_type = field.get("type", "number")
            field_value = field_value_map.get(field_id)

            # Store metadata
            config["fields"][field_id] = {
                "name": field_name,
                "type": field_type,
                "required": field.get("required", False),
            }

            # Store collected value
            config["values"][field_id] = field_value

            logger.debug(f"Collected {field_id} = {field_value} ({field_type})")

        # Store collected values
        current_store["config"] = config
        logger.info(f"Template config collected for algorithm {selected_algorithm}: {config['values']}")

        return current_store

    # Callback: Reset template config when algorithm is cleared
    @app.callback(
        Output("template-config-store", "data", allow_duplicate=True),
        Input("template-algorithm-selector", "value"),
        State("template-config-store", "data"),
        prevent_initial_call=True,
    )
    def reset_template_on_clear(selected_algorithm, current_store):
        """Clear template config when no algorithm is selected."""
        if not selected_algorithm:
            return {}
        return current_store

