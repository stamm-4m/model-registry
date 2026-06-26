import dash_bootstrap_components as dbc
from dash import dcc, html


def login_form():
    """
    Two-pane sign-in screen styled after FermOps Admin.

    IMPORTANT: All component IDs are preserved so the existing
    callbacks in ``callbacks/callback_auth.py`` keep working without
    modification:

      * ``url-login``        – dcc.Location used after login
      * ``login-username``   – username input
      * ``login-password``   – password input
      * ``toggle-password``  – show/hide password toggle
      * ``remember-me``      – remember-me checkbox
      * ``login-button``     – submit button
      * ``login-message``    – error feedback container
    """

    return html.Div(
        [
            dcc.Location(id="url-login", refresh=True),
            html.Div(
                [
                    # ── Brand pane (left) ────────────────────────────────
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Img(
                                        src="/assets/ml_repo_logo.png",
                                        className="login-logo-img",
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Span(
                                                        "Model ",
                                                        className="brand-ferm",
                                                    ),
                                                    html.Span(
                                                        "Registry",
                                                        className="brand-ops",
                                                    ),
                                                ],
                                                className="login-product",
                                            ),
                                            html.Div(
                                                "ML model lifecycle · a STAMM module",
                                                className="login-tag",
                                            ),
                                        ],
                                        className="login-brand-text",
                                    ),
                                ],
                                className="login-brand-top",
                            ),
                            html.Div(
                                [
                                    html.Br(),
                                    html.H2(
                                        [
                                            "Register, version and deploy ",
                                            html.Em("bioprocess ML models"),
                                        ]
                                    ),
                                    html.P(
                                        "Centralised registry for soft, dynamic "
                                        "and hybrid models — track metadata, "
                                        "lineage and deployments across your labs."
                                    ),
                                    html.Ul(
                                        [
                                            html.Li(
                                                "Project · experiment · model hierarchy"
                                            ),
                                            html.Li(
                                                "Versioned model artifacts with FAIR metadata"
                                            ),
                                            html.Li(
                                                "Python & R model serving out of the box"
                                            ),
                                            html.Li(
                                                "Role-based access for labs and partners"
                                            ),
                                        ],
                                        className="login-feature-list",
                                    ),
                                ],
                                className="login-pitch",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("Created by the "),
                                            html.Strong("Mathematics Cell"),
                                            html.Span(" at"),
                                        ],
                                        style={
                                            "fontSize": "11px",
                                            "opacity": 0.85,
                                            "marginBottom": "8px",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.A(
                                                html.Img(
                                                    src="/assets/inrae.webp",
                                                    className="login-credit-logo login-credit-inrae",
                                                ),
                                                href="https://www.inrae.fr/",
                                                target="_blank",
                                                title="INRAE",
                                            ),
                                            html.A(
                                                html.Img(
                                                    src="/assets/tbi.png",
                                                    className="login-credit-logo login-credit-tbi",
                                                ),
                                                href="https://www.toulouse-biotechnology-institute.fr/",
                                                target="_blank",
                                                title="Toulouse Biotechnology Institute",
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "gap": "12px",
                                            "alignItems": "center",
                                            "marginBottom": "12px",
                                            "flexWrap": "wrap",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.Span("STAMM Framework · open source"),
                                            html.Br(),
                                            html.Span("Model Registry · MR"),
                                        ]
                                    ),
                                ],
                                className="login-credits",
                            ),
                        ],
                        className="login-brand-pane",
                    ),
                    # ── Form pane (right) ────────────────────────────────
                    html.Div(
                        [
                            html.H1("Sign in"),
                            html.Div(
                                "Welcome back. Enter your credentials to continue.",
                                className="login-sub",
                            ),
                            # Username
                            html.Div(
                                [
                                    html.Label("Username"),
                                    dcc.Input(
                                        id="login-username",
                                        type="text",
                                        value="",
                                        placeholder="your.username",
                                        className="login-input",
                                    ),
                                ],
                                className="login-field",
                            ),
                            # Password (with show/hide toggle)
                            html.Div(
                                [
                                    html.Label("Password"),
                                    html.Div(
                                        [
                                            dcc.Input(
                                                id="login-password",
                                                type="password",
                                                value="",
                                                placeholder="••••••••",
                                                className="login-input",
                                            ),
                                            html.Button(
                                                html.I(className="bi bi-eye-fill"),
                                                id="toggle-password",
                                                n_clicks=0,
                                                type="button",
                                                className="login-eye-btn",
                                            ),
                                        ],
                                        className="login-input-wrap",
                                    ),
                                ],
                                className="login-field",
                            ),
                            # Remember me + register link
                            html.Div(
                                [
                                    html.Label(
                                        [
                                            dbc.Checkbox(
                                                id="remember-me",
                                                className="login-checkbox",
                                            ),
                                            html.Span(
                                                "Keep me signed in",
                                                className="login-keep-text",
                                            ),
                                        ],
                                        className="login-keep-label",
                                    ),
                                    html.A(
                                        "Register",
                                        href="/register",
                                        className="login-link",
                                    ),
                                ],
                                className="login-row",
                            ),
                            # Submit
                            html.Button(
                                "Sign in →",
                                id="login-button",
                                n_clicks=0,
                                className="login-submit",
                            ),
                            # Error / status message
                            html.Div(
                                id="login-message",
                                className="login-error",
                                style={"minHeight": "16px"},
                            ),
                            html.Div(
                                [
                                    html.Span("Need access? "),
                                    html.Span(
                                        "Contact your lab admin →",
                                        className="login-request",
                                    ),
                                    html.Div(
                                        [
                                            "By signing in, you agree to your "
                                            "institution's data-use policy and "
                                            "STAMM's open-source terms.",
                                            html.Br(),
                                            "Model artifacts and metadata remain "
                                            "on your facility's infrastructure.",
                                        ],
                                        className="login-legal",
                                    ),
                                    html.Div(
                                        "© 2026 MR - Model Registry. All rights reserved.",
                                        className="login-copyright",
                                    ),
                                ],
                                className="login-footer",
                            ),
                        ],
                        className="login-form-pane",
                    ),
                ],
                className="login-stage",
            ),
        ],
        className="login-page",
    )
