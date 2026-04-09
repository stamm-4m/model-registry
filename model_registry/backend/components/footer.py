import dash_bootstrap_components as dbc
from dash import html


def build_footer(logos=None, text="© 2026 My App. All rights reserved."):
    """
    Create a footer component.

    :param logos: List of dicts -> [{"src": "...", "href": "..."}]
    :param text: Footer copyright text
    :param height: Height of the logos
    :return: dbc.Container
    """

    logos = logos or []

    logo_elements = []
    for logo in logos:
        img = html.Img(
            src=logo.get("src"),
            style={"height":logo.get("height"), "margin": "0 10px"},
        )

        # Si tiene link
        if logo.get("href"):
            img = html.A(img, href=logo["href"], target="_blank")

        logo_elements.append(img)

    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.Div(
                        logo_elements,
                        style={
                            "display": "flex",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "flexWrap": "wrap",
                        },
                    )
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.Small(
                        "Mathematics cell",
                        style={"color": "#6c757d"},
                    ),
                    className="text-center mt-2",
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.Small(
                        text,
                        style={"color": "#6c757d"},
                    ),
                    className="text-center mt-2",
                )
            ),
        ],
        fluid=True,
        className="mt-4 pt-3 border-top",
        style={"backgroundColor": "#1e1e2f"},
    )