"""Template UI components and helpers for model upload."""

import dash_bootstrap_components as dbc
from dash import dcc, html

# All 18 STAMM algorithm families
STAMM_ALGORITHMS = {
    "decision_tree": "Decision Tree",
    "random_forest": "Random Forest",
    "gradient_boosting": "Gradient Boosting",
    "ensemble": "Ensemble",
    "svm": "Support Vector Machine (SVM)",
    "linear_regression": "Linear Regression",
    "logistic_regression": "Logistic Regression",
    "neural_network": "Neural Network",
    "rnn": "Recurrent Neural Network (RNN)",
    "cnn": "Convolutional Neural Network (CNN)",
    "transformer": "Transformer",
    "gaussian_process": "Gaussian Process",
    "pls": "Partial Least Squares (PLS)",
    "pca": "Principal Component Analysis (PCA)",
    "kmeans": "K-Means Clustering",
    "cubist": "Cubist (Rule-based)",
    "m5": "M5 Model Tree",
    "custom": "Custom/Other",
}


def algorithm_selector_dropdown(value=None, disabled=False):
    """Create dropdown component for learner family selection (lives in Description tab)."""
    return html.Div(
        [
            dbc.Label(
                "Learner Family",
                className="fw-semibold text-muted small text-uppercase mb-1",
            ),
            dcc.Dropdown(
                id="template-algorithm-selector",
                options=[
                    {"label": label, "value": algo}
                    for algo, label in sorted(
                        STAMM_ALGORITHMS.items(), key=lambda x: x[1]
                    )
                ],
                value=value,
                placeholder="Select algorithm family…",
                clearable=True,
                disabled=disabled,
            ),
        ],
        className="mb-3",
    )


def template_config_section():
    """Create section for template-specific configuration fields."""
    return html.Div(
        [
            html.H4(
                "Learner Hyperparameters", className="mb-4", id="template-config-header"
            ),
            html.Div(
                id="template-config-fields",
                children=html.P(
                    "Select an algorithm family above to load its standard hyperparameters.",
                    className="text-muted",
                ),
            ),
        ],
        id="template-config-container",
        style={"display": "none"},
    )


def hyperparameter_input(
    label: str,
    input_id: str,
    input_type: str = "number",
    placeholder: str = None,
    required: bool = False,
):
    """Create a floating label input for hyperparameters."""
    return dbc.FormFloating(
        [
            dbc.Input(
                id=input_id,
                type=input_type,
                placeholder=placeholder or label,
            ),
            dbc.Label(label),
        ],
        className="mb-3",
    )


def required_marker():
    """Create a visual marker for required fields."""
    return html.Span(" *", className="text-danger")


def get_template_fields_by_algorithm(algorithm: str):
    """Return template-specific field definitions for an algorithm.

    Returns list of field definitions: {name, id, type, required, placeholder, help_text}
    """
    fields_map = {
        "random_forest": [
            {
                "name": "Number of Estimators",
                "id": "template-n-estimators",
                "type": "number",
                "required": True,
                "value": 100,
            },
            {
                "name": "Max Depth",
                "id": "template-max-depth",
                "type": "number",
                "required": False,
                "value": None,
            },
            {
                "name": "Min Samples Split",
                "id": "template-min-samples-split",
                "type": "number",
                "required": False,
                "value": 2,
            },
            {
                "name": "Max Features",
                "id": "template-max-features",
                "type": "text",
                "required": False,
                "value": "sqrt",
                "placeholder": "sqrt, log2, or number",
            },
        ],
        "decision_tree": [
            {
                "name": "Max Depth",
                "id": "template-max-depth",
                "type": "number",
                "required": True,
            },
            {
                "name": "Min Samples Split",
                "id": "template-min-samples-split",
                "type": "number",
                "required": False,
                "value": 2,
            },
            {
                "name": "Criterion",
                "id": "template-criterion",
                "type": "text",
                "required": False,
                "value": "gini",
                "placeholder": "gini or entropy",
            },
        ],
        "gradient_boosting": [
            {
                "name": "Number of Estimators",
                "id": "template-n-estimators",
                "type": "number",
                "required": True,
                "value": 100,
            },
            {
                "name": "Learning Rate",
                "id": "template-learning-rate",
                "type": "number",
                "required": True,
                "value": 0.1,
                "step": "0.01",
            },
            {
                "name": "Max Depth",
                "id": "template-max-depth",
                "type": "number",
                "required": True,
                "value": 3,
            },
        ],
        "svm": [
            {
                "name": "Kernel",
                "id": "template-kernel",
                "type": "text",
                "required": True,
                "value": "rbf",
                "placeholder": "rbf, linear, poly, sigmoid",
            },
            {
                "name": "C (Regularization)",
                "id": "template-c",
                "type": "number",
                "required": True,
                "value": 1.0,
                "step": "0.1",
            },
            {
                "name": "Gamma",
                "id": "template-gamma",
                "type": "text",
                "required": False,
                "value": "scale",
                "placeholder": "scale or float",
            },
        ],
        "neural_network": [
            {
                "name": "Hidden Layers (comma-separated)",
                "id": "template-hidden-layers",
                "type": "text",
                "required": True,
                "placeholder": "e.g., 128,64,32",
            },
            {
                "name": "Activation",
                "id": "template-activation",
                "type": "text",
                "required": False,
                "value": "relu",
                "placeholder": "relu, sigmoid, tanh",
            },
            {
                "name": "Learning Rate",
                "id": "template-learning-rate",
                "type": "number",
                "required": False,
                "value": 0.001,
                "step": "0.0001",
            },
            {
                "name": "Batch Size",
                "id": "template-batch-size",
                "type": "number",
                "required": False,
                "value": 32,
            },
        ],
        "rnn": [
            {
                "name": "Hidden Units",
                "id": "template-hidden-units",
                "type": "number",
                "required": True,
                "value": 64,
            },
            {
                "name": "Number of Layers",
                "id": "template-num-layers",
                "type": "number",
                "required": True,
                "value": 1,
            },
            {
                "name": "Activation",
                "id": "template-activation",
                "type": "text",
                "required": False,
                "value": "relu",
                "placeholder": "relu, tanh",
            },
            {
                "name": "Dropout Rate",
                "id": "template-dropout",
                "type": "number",
                "required": False,
                "value": 0.0,
                "min": 0,
                "max": 1,
                "step": 0.1,
            },
        ],
        "cubist": [
            {
                "name": "Committees",
                "id": "template-committees",
                "type": "number",
                "required": True,
                "value": 1,
            },
            {
                "name": "Instance-based Corrections",
                "id": "template-instance-corrections",
                "type": "number",
                "required": True,
                "value": 3,
            },
            {
                "name": "Min Instances per Leaf",
                "id": "template-min-instances",
                "type": "number",
                "required": True,
                "value": 12000,
            },
            {
                "name": "Pruned",
                "id": "template-pruned",
                "type": "checkbox",
                "required": False,
                "value": True,
            },
        ],
        "m5": [
            {
                "name": "Min Instances per Leaf",
                "id": "template-min-instances",
                "type": "number",
                "required": True,
                "value": 12000,
            },
            {
                "name": "Pruned",
                "id": "template-pruned",
                "type": "checkbox",
                "required": False,
                "value": True,
            },
            {
                "name": "Smoothed",
                "id": "template-smoothed",
                "type": "checkbox",
                "required": False,
                "value": True,
            },
        ],
        "linear_regression": [
            {
                "name": "Fit Intercept",
                "id": "template-fit-intercept",
                "type": "checkbox",
                "required": False,
                "value": True,
            },
            {
                "name": "Positive Coefficients",
                "id": "template-positive",
                "type": "checkbox",
                "required": False,
                "value": False,
            },
        ],
        "logistic_regression": [
            {
                "name": "C (Regularization)",
                "id": "template-c",
                "type": "number",
                "required": False,
                "value": 1.0,
                "step": 0.1,
            },
            {
                "name": "Penalty",
                "id": "template-penalty",
                "type": "text",
                "required": False,
                "value": "l2",
                "placeholder": "l1, l2, elasticnet, none",
            },
            {
                "name": "Solver",
                "id": "template-solver",
                "type": "text",
                "required": False,
                "value": "lbfgs",
                "placeholder": "lbfgs, liblinear, newton-cg, saga",
            },
        ],
        "pls": [
            {
                "name": "Number of Components",
                "id": "template-n-components",
                "type": "number",
                "required": True,
                "value": 2,
            },
            {
                "name": "Scale",
                "id": "template-scale",
                "type": "checkbox",
                "required": False,
                "value": True,
            },
        ],
        "pca": [
            {
                "name": "Number of Components",
                "id": "template-n-components",
                "type": "text",
                "required": False,
                "value": "auto",
                "placeholder": "auto, mle, or integer",
            },
            {
                "name": "Whiten",
                "id": "template-whiten",
                "type": "checkbox",
                "required": False,
                "value": False,
            },
        ],
        "kmeans": [
            {
                "name": "Number of Clusters",
                "id": "template-n-clusters",
                "type": "number",
                "required": True,
                "value": 3,
            },
            {
                "name": "Init Method",
                "id": "template-init",
                "type": "text",
                "required": False,
                "value": "k-means++",
                "placeholder": "k-means++ or random",
            },
            {
                "name": "Max Iterations",
                "id": "template-max-iter",
                "type": "number",
                "required": False,
                "value": 300,
            },
        ],
        "gaussian_process": [
            {
                "name": "Kernel",
                "id": "template-kernel",
                "type": "text",
                "required": False,
                "value": "rbf",
                "placeholder": "rbf, matern, rational_quadratic",
            },
            {
                "name": "Alpha (Noise)",
                "id": "template-alpha",
                "type": "number",
                "required": False,
                "value": 1e-6,
                "step": "0.00001",
            },
        ],
        "ensemble": [
            {
                "name": "Ensemble Method",
                "id": "template-ensemble-method",
                "type": "text",
                "required": False,
                "value": "voting",
                "placeholder": "voting, stacking, blending, averaging",
            },
            {
                "name": "Number of Base Estimators",
                "id": "template-num-estimators",
                "type": "number",
                "required": False,
                "value": 3,
            },
        ],
        "cnn": [
            {
                "name": "Number of Filters",
                "id": "template-num-filters",
                "type": "number",
                "required": False,
                "value": 32,
            },
            {
                "name": "Kernel Size",
                "id": "template-kernel-size",
                "type": "number",
                "required": False,
                "value": 3,
            },
            {
                "name": "Pool Size",
                "id": "template-pool-size",
                "type": "number",
                "required": False,
                "value": 2,
            },
        ],
        "transformer": [
            {
                "name": "Model Dimension (d_model)",
                "id": "template-d-model",
                "type": "number",
                "required": True,
                "value": 512,
            },
            {
                "name": "Number of Heads",
                "id": "template-num-heads",
                "type": "number",
                "required": True,
                "value": 8,
            },
            {
                "name": "Number of Layers",
                "id": "template-num-layers",
                "type": "number",
                "required": True,
                "value": 6,
            },
        ],
        "custom": [
            {
                "name": "Custom Configuration (JSON)",
                "id": "template-custom-config",
                "type": "textarea",
                "required": False,
                "value": "{}",
            },
        ],
    }
    return fields_map.get(algorithm, [])
