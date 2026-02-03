from dash import Input, Output, State


def register_toolbar_callbacks(app):
    @app.callback(
        Output("settings-modal", "is_open"),
        Input("btn-settings", "n_clicks"),
        Input("close-settings", "n_clicks"),
        State("settings-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_modal(open_click, close_click, is_open):
        if open_click is None and close_click is None:
            return is_open
        if open_click and open_click > close_click if close_click else True:
            return True
        return False
