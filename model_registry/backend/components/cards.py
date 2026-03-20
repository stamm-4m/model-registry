from dash import html


def info_card(title, body):
    return html.Div([
        html.H4(title),
        html.P(body)
    ], style={'border':'1px solid #ddd','padding':'8px','border-radius':'4px'})
