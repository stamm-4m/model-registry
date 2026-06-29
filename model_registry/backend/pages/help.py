import dash
from dash import html
import dash_bootstrap_components as dbc

_XAI_IMG_STYLE = {
    "width": "100%", "maxWidth": "320px", "border": "1px solid #e9ecef",
    "borderRadius": "6px", "background": "#ffffff", "padding": "4px",
    "marginBottom": "10px", "display": "block",
}

def help_layout():

    sidebar = dbc.Card(
        [
            dbc.CardHeader(html.H5("Documentation")),
            dbc.CardBody(
                dbc.Nav(
                    [
                        dbc.NavLink("Overview", href="#overview", external_link=True),
                        dbc.NavLink("Architecture", href="#architecture", external_link=True),
                        dbc.NavLink("Upload Workflow", href="#upload", external_link=True),
                        dbc.NavLink("Prediction Workflow", href="#prediction", external_link=True),
                        dbc.NavLink("Explainability (XAI)", href="#xai", external_link=True),
                        dbc.NavLink("API Endpoints", href="#api", external_link=True),
                        dbc.NavLink("Configuration Files", href="#config", external_link=True),
                        dbc.NavLink("Error Handling", href="#errors", external_link=True),
                        dbc.NavLink("FAQ", href="#faq", external_link=True),
                    ],
                    vertical=True,
                    pills=True,
                )
            ),
        ],
        className="h-100",
    )

    content = html.Div(
        [
            html.H2("Help & Documentation", className="mb-4"),

            # Overview
            html.H4("Overview", id="overview"),
            html.P(
                """
                This backend application provides model registration,
                validation, and prediction services. It supports YAML
                configuration files, EDF processing, and REST-based
                communication between components.
                """
            ),

            html.Hr(),

            # Architecture
            html.H4("Architecture", id="architecture"),
            html.P("Main components of the system:"),
            html.Ul(
                [
                    html.Li("Models: Model validation and prediction logic."),
                    html.Li("Views: Dash UI components and callbacks."),
                    html.Li("Data: Uploaded datasets and processed files."),
                    html.Li("InfluxDb: Database integration layer."),
                    html.Li("R Integration: External R scripts execution."),
                ]
            ),
            html.P(
                "Workflow: Upload → Validate → Store → Predict → Save Results."
            ),

            html.Hr(),

            # Upload Workflow
            html.H4("Upload Workflow", id="upload"),
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P("1. Upload a valid file (.edf, .yaml, etc.)."),
                            html.P("2. Fill required metadata fields."),
                            html.P("3. Backend validates structure and variables."),
                            html.P("4. File is stored in the server directory."),
                        ],
                        title="How to Upload Files",
                    ),
                ],
                start_collapsed=True,
            ),

            html.Hr(),

            # Prediction Workflow
            html.H4("Prediction Workflow", id="prediction"),
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P("1. Select a registered model."),
                            html.P("2. Provide required input variables."),
                            html.P("3. Backend executes prediction logic."),
                            html.P("4. Results are displayed and stored."),
                        ],
                        title="How Prediction Works",
                    ),
                ],
                start_collapsed=True,
            ),

            html.Hr(),

            # Explainability (XAI)
            html.H4("Explainability (XAI)", id="xai"),
            html.P(
                "Open this view from the magnifying-glass icon in the XAI column "
                "of the models list. It gives a per-model, explanation-first view "
                "of one model: a model-agnostic core (importance, SHAP, partial "
                "dependence, local explanation) plus a family-specific section "
                "that changes with the model's algorithm."
            ),
            dbc.Alert(
                [
                    html.Strong("Live vs. illustrative. "),
                    "Panels with a green ", html.Em("live"), " badge are computed "
                    "from the real model artifact. Panels with a grey ",
                    html.Em("placeholder"), " badge are illustrative (the artifact "
                    "could not be explained, or the capability needs data that "
                    "isn't available). Importance, rules, tree structure and "
                    "coefficients come straight from the trained model. Partial "
                    "dependence and SHAP run the real model over a background "
                    "sampled from each feature's declared operating range "
                    "(expected_range in the model YAML) — unless you upload your "
                    "own data. Permutation importance needs labels and is only "
                    "computed when you upload data that includes the target column.",
                ],
                color="info",
            ),

            html.H6("How to read each chart"),
            html.P("Each panel below shows what the chart looks like and a worked "
                   "example from the IndPenSim penicillin models.",
                   className="text-muted small"),
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.Img(src="/assets/xai/importance_bars.svg", style=_XAI_IMG_STYLE),
                            html.P("Ranks inputs by how much the model's accuracy drops when that input is randomly shuffled — a longer bar means the model relies on it more. Needs labelled data: upload a CSV that includes the target column to compute it."),
                            html.P([html.Strong("Example: "), 'For the penicillin Random Forest, sugar_feed_rate and dissolved oxygen top the list — shuffling them hurts predictions the most — while agitation barely moves the score.']),
                        ],
                        title='Global feature importance (permutation)',
                    ),
                    dbc.AccordionItem(
                        [
                            html.Img(src="/assets/xai/shap_beeswarm.svg", style=_XAI_IMG_STYLE),
                            html.P("Each dot is one sample. Left/right shows whether that feature pushed the prediction down/up; colour shows whether the feature's value was low (blue) or high (red). Features are ordered top-to-bottom by overall impact."),
                            html.P([html.Strong("Example: "), 'sugar_feed_rate spreads widest: red dots (high feed) sit on the right and push predicted penicillin up, blue dots (low feed) sit on the left and pull it down.']),
                        ],
                        title='SHAP summary',
                    ),
                    dbc.AccordionItem(
                        [
                            html.Img(src="/assets/xai/pdp_curve.svg", style=_XAI_IMG_STYLE),
                            html.P('Shows how the predicted output changes as ONE feature varies, averaging over the others. An upward slope means higher feature values give higher predictions. Choose the feature in the dropdown.'),
                            html.P([html.Strong("Example: "), 'Sweeping temperature from 298 K to 308 K, predicted penicillin climbs then flattens — the model expects more product as it warms, up to a point.']),
                        ],
                        title='Partial dependence (PDP)',
                    ),
                    dbc.AccordionItem(
                        [
                            html.Img(src="/assets/xai/waterfall.svg", style=_XAI_IMG_STYLE),
                            html.P('Explains ONE prediction: each bar is how much a feature pushed it above (blue) or below (red) the average. The bars add up from the baseline E[f(x)] to the final prediction. Choose the instance in the dropdown.'),
                            html.P([html.Strong("Example: "), 'For one batch sample, starting from the average ≈0.50 g/L, high sugar_feed_rate adds +0.18 and low DO subtracts −0.06, landing the prediction at ≈0.70 g/L.']),
                        ],
                        title='Local explanation (SHAP waterfall)',
                    ),
                    dbc.AccordionItem(
                        [
                            html.Img(src="/assets/xai/tree.svg", style=_XAI_IMG_STYLE),
                            html.P("Impurity importance: how much each feature reduced error across the tree's splits, read straight from the model — fast and exact, but can over-credit features with many distinct values, so cross-check against SHAP. The decision structure and rules show a representative path / IF-THEN rules; for a forest this is ONE example tree, not the whole ensemble's combined logic."),
                            html.P([html.Strong("Example: "), "The first tree splits on pH ≤ 6.8, then on dissolved oxygen; one leaf reads 'predicted penicillin = 0.55'. The rules panel writes the same path as IF pH ≤ 6.8 AND DO > 2.1 THEN 0.34."]),
                        ],
                        title='Trees — importance, structure & rules',
                    ),
                    dbc.AccordionItem(
                        [
                            html.Img(src="/assets/xai/coefficients.svg", style=_XAI_IMG_STYLE),
                            html.P('Each bar is the weight the linear model gives a feature: positive (blue) raises the prediction, negative (red) lowers it; larger magnitude = stronger effect. Most comparable when the inputs are on similar scales.'),
                            html.P([html.Strong("Example: "), 'A linear fit might give sugar_feed_rate +0.5 (more feed → more penicillin) and temperature −0.3 (hotter → less), so feed pushes the prediction up and temperature pulls it down.']),
                        ],
                        title='Linear — coefficients',
                    ),
                    dbc.AccordionItem(
                        [
                            html.Img(src="/assets/xai/uncertainty.svg", style=_XAI_IMG_STYLE),
                            html.P("ARD relevance: inverse length-scales — higher means the model treats that feature as more relevant. The uncertainty band shows the model's confidence (wider = less certain)."),
                            html.P([html.Strong("Example: "), 'A Gaussian process flags pH and DO as most relevant and widens its uncertainty band in operating regions it saw little of during training.']),
                        ],
                        title='Kernel / Gaussian process',
                    ),
                    dbc.AccordionItem(
                        [
                            html.Img(src="/assets/xai/saliency_heatmap.svg", style=_XAI_IMG_STYLE),
                            html.P('Temporal saliency: how sensitive the prediction is to each feature at each time step (brighter = more influential). Integrated gradients attribute the prediction to each feature relative to a baseline; transformers also show an attention map — which time steps the model focused on.'),
                            html.P([html.Strong("Example: "), 'An LSTM forecasting penicillin lights up dissolved oxygen in the last few time steps before the prediction — the model leans on the most recent readings.']),
                        ],
                        title='Sequence & attention models',
                    ),
                    dbc.AccordionItem(
                        [
                            html.Img(src="/assets/xai/loadings_heatmap.svg", style=_XAI_IMG_STYLE),
                            html.P("Component loadings show how much each original feature contributes to each component / cluster; explained variance shows how much of the data's variation each component captures. Target-based attributions (SHAP, PDP) don't apply to unsupervised models."),
                            html.P([html.Strong("Example: "), "PCA over the bioreactor sensors might load temperature and agitation heavily on PC1 — a 'heat & mixing' axis — with PC1 alone capturing about 45% of the variance."]),
                        ],
                        title='Unsupervised (PCA / K-means)',
                    ),
                ],
                start_collapsed=True,
            ),

            html.H6("What each model family shows", className="mt-3"),
            dbc.Table(
                [
                    html.Thead(html.Tr([html.Th("Model family"),
                                        html.Th("What you'll see")])),
                    html.Tbody(
                        [
                            html.Tr([html.Td("Tree (Random Forest, Gradient Boosting, "
                                             "HistGB, CART, M5, Cubist)"),
                                     html.Td("Impurity importance, decision rules, tree "
                                             "structure, SHAP, partial dependence")]),
                            html.Tr([html.Td("Linear / Logistic / PLS"),
                                     html.Td("Signed coefficients, SHAP, partial dependence")]),
                            html.Tr([html.Td("SVM / Gaussian process"),
                                     html.Td("ARD relevance, predictive uncertainty, "
                                             "partial dependence")]),
                            html.Tr([html.Td("Neural / RNN / CNN"),
                                     html.Td("Temporal saliency, integrated gradients")]),
                            html.Tr([html.Td("Transformer"),
                                     html.Td("Attention map, step attribution")]),
                            html.Tr([html.Td("PCA / K-means"),
                                     html.Td("Component loadings, explained variance")]),
                        ]
                    ),
                ],
                bordered=True, striped=True, hover=True, responsive=True, size="sm",
            ),

            html.H6("Testing with your own data", className="mt-3"),
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.P("1. In the 'Test with your own data' card, upload "
                                   "a CSV."),
                            html.P("2. The column names must match the model's stored "
                                   "input feature names exactly (the view lists them)."),
                            html.P("3. Include a column matching the model's output "
                                   "(target) name to also compute permutation "
                                   "importance."),
                            html.P("4. SHAP and partial dependence are recomputed on "
                                   "your rows (the first 2000) instead of the sampled "
                                   "background; a status line confirms what was "
                                   "recomputed."),
                        ],
                        title="How to upload data",
                    ),
                ],
                start_collapsed=True,
            ),

            html.H6("How it works (and privacy)", className="mt-3"),
            html.P(
                "The view never reads model files itself. It calls a protected API "
                "endpoint (POST /{project_id}/explain/{model_id}, requiring "
                "models:read on Models), which uses the model the registry already "
                "loaded from the database — the artifact's location is never exposed "
                "to the browser. Each explanation is computed independently, so if "
                "one fails the rest still render."
            ),

            html.Hr(),

            # API Endpoints
            html.H4("API Endpoints", id="api"),
            dbc.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Method"),
                                html.Th("Endpoint"),
                                html.Th("Description"),
                            ]
                        )
                    ),
                    html.Tbody(
                        [
                            html.Tr(
                                [
                                    html.Td("POST"),
                                    html.Td("/predict"),
                                    html.Td("Run model prediction"),
                                ]
                            ),
                            html.Tr(
                                [
                                    html.Td("GET"),
                                    html.Td("/models"),
                                    html.Td("List registered models"),
                                ]
                            ),
                            html.Tr(
                                [
                                    html.Td("POST"),
                                    html.Td("/{project_id}/explain/{model_id}"),
                                    html.Td("Return XAI explanations for a model "
                                            "(protected: models:read on Models)"),
                                ]
                            ),
                        ]
                    ),
                ],
                bordered=True,
                striped=True,
                hover=True,
                responsive=True,
            ),

            html.Hr(),

            # Configuration Files
            html.H4("Configuration Files", id="config"),
            html.P("YAML configuration must include:"),
            html.Ul(
                [
                    html.Li("model_name"),
                    html.Li("model_version"),
                    html.Li("input_variables"),
                    html.Li("output_variables"),
                ]
            ),
            html.P("Ensure variable names match dataset columns."),

            html.Hr(),

            # Error Handling
            html.H4("Error Handling", id="errors"),
            html.Ul(
                [
                    html.Li("Validation Error: Missing required variables."),
                    html.Li("Format Error: Invalid file type."),
                    html.Li("Server Error (500): Internal processing failure."),
                ]
            ),

            html.Hr(),

            # FAQ
            html.H4("FAQ", id="faq"),
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        "Verify that all required variables exist in the dataset.",
                        title="Why does my model fail validation?",
                    ),
                    dbc.AccordionItem(
                        "Check backend logs for detailed error information.",
                        title="Where can I see server errors?",
                    ),
                ],
                start_collapsed=True,
            ),
        ],
        className="p-4",
    )
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(sidebar, width=3),
                    dbc.Col(content, width=9),
                ],
                className="mt-4",
            )
        ],
        fluid=True,
    )
