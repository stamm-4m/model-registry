import dash_bootstrap_components as dbc
from dash import dcc, html
from model_registry.backend.components.footer import build_footer


def login_form():
    return html.Div(
        [
            dcc.Location(id="url-login", refresh=True),
            html.Div(
                [
                    dbc.Container(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            # Logo
                                            html.Div(
                                                html.Img(
                                                    src="/assets/logo.png",
                                                    style={
                                                        "maxWidth": "160px",
                                                        "marginBottom": "25px",
                                                    },
                                                ),
                                                className="text-center",
                                            ),

                                            # Card Login
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        html.H4(
                                                            "Sign In",
                                                            className="text-center",
                                                        )
                                                    ),
                                                    dbc.CardBody(
                                                        [
                                                            # Username
                                                            html.Div(
                                                                [
                                                                    dbc.Label("Username"),
                                                                    dbc.InputGroup(
                                                                        [
                                                                            dbc.InputGroupText(
                                                                                html.I(
                                                                                    className="bi bi-person-fill"
                                                                                )
                                                                            ),
                                                                            dbc.Input(
                                                                                id="login-username",
                                                                                placeholder="Enter your username",
                                                                                type="text",
                                                                            ),
                                                                        ]
                                                                    ),
                                                                ],
                                                                className="mb-3",
                                                            ),

                                                            # Password
                                                            html.Div(
                                                                [
                                                                    dbc.Label("Password"),
                                                                    dbc.InputGroup(
                                                                        [
                                                                            dbc.InputGroupText(
                                                                                html.I(
                                                                                    className="bi bi-lock-fill"
                                                                                )
                                                                            ),
                                                                            dbc.Input(
                                                                                id="login-password",
                                                                                placeholder="Enter your password",
                                                                                type="password",
                                                                            ),
                                                                            dbc.Button(
                                                                                html.I(
                                                                                    className="bi bi-eye-fill"
                                                                                ),
                                                                                id="toggle-password",
                                                                                color="light",
                                                                                n_clicks=0,
                                                                                className="border",
                                                                            ),
                                                                        ]
                                                                    ),
                                                                ],
                                                                className="mb-3",
                                                            ),

                                                            # Remember + Register
                                                            html.Div(
                                                                [
                                                                    dbc.Checkbox(
                                                                        id="remember-me",
                                                                        className="me-2",
                                                                    ),
                                                                    dbc.Label(
                                                                        "Remember me",
                                                                        className="me-auto",
                                                                    ),
                                                                    html.A(
                                                                        "Register",
                                                                        href="/register",
                                                                        className="ms-auto text-primary",
                                                                    ),
                                                                ],
                                                                className="d-flex justify-content-between align-items-center mb-3",
                                                            ),

                                                            # Button
                                                            dbc.Button(
                                                                "Sign In",
                                                                id="login-button",
                                                                color="primary",
                                                                className="w-100",
                                                            ),

                                                            # Message
                                                            html.Div(
                                                                id="login-message",
                                                                className="text-danger mt-3",
                                                                style={
                                                                    "minHeight": "2em"
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                                className="shadow p-4",
                                                style={"borderRadius": "1rem"},
                                            ),
                                        ],
                                        width=12,
                                        md=6,
                                        lg=4,
                                    )
                                ],
                                justify="center",
                                align="center",
                                className="flex-grow-1",
                            )
                        ],
                        fluid=True,
                    ),

                    # footer
                    build_footer(
                        logos=[
                            {"src": "/assets/inrae.webp", "href": "https://inrae.com", "height": "80px"},
                            {"src": "/assets/bioind4-dark.png", "href": "https://www.bioindustry4.eu/", "height": "100px"},
                            {"src": "/assets/tbi.png", "href": "https://www.toulouse-biotechnology-institute.fr/", "height": "100px"},
                            {"src": "/assets/logo_transparent_background_dark.png", "href": "https://stamm.inrae.fr/", "height": "100px"},
                            {"src": "/assets/ibisba.png", "href": "https://ibisba.eu/", "height": "80px"},
                        ],
                        text="© 2026 MR - Model Registry. All rights reserved.",
                    ),
                ],
                style={
                    "minHeight": "100vh",
                    "display": "flex",
                    "flexDirection": "column",
                },
            ),
        ]
    )