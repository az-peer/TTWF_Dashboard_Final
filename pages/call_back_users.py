from dash import callback, Output, Input, ctx, ALL, no_update, callback_context

@callback(
    Output("url", "pathname"),
    Output("url", "search"),
    Input({'type': 'school-nav-btn', 'index': ALL}, "n_clicks"),
    prevent_initial_call=True
)
def redirect_to_school(n_clicks):
    triggered = callback_context.triggered
    if not triggered:
        return no_update, no_update

    button_id = eval(triggered[0]["prop_id"].split('.')[0])
    school_id = button_id['index']
    return "/school", f"?school_id={school_id}"