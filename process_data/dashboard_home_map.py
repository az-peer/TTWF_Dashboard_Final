import dash_leaflet as dl
from dash import html, Output, Input, dcc, callback, callback_context
import json
import os
from process_data.capture_indexes_for_main_map import grab_indexes
import dash
# run to grab the selected indexes
grab_indexes()



# Load assets
assets_path = os.path.join(os.path.dirname(__file__), "assets")

with open(os.path.join(assets_path, "district_coords.json")) as f:
    district_data = json.load(f)
with open(os.path.join(assets_path, "division_info_map_main.json")) as f:
    division_info = json.load(f)

# grab the indexes
with open(os.path.join(assets_path, "user_digital_indexes_by_division.json")) as f:
    digital_indexes_for_map = json.load(f)

with open(os.path.join(assets_path, "curr_final_index_by_division.json")) as f:
    curr_indexes_for_map = json.load(f)

# Map center and zoom
initial_center = [27.5, 69.3451]
initial_zoom = 6

status_color_map = {
    "Good": "green",
    "Average": "orange",
    "Needs Attention": "red"
}

# Index division for the coloring of the dots 
dig_status_map = {d["Division"]: d["status"] for d in digital_indexes_for_map}
dig_score_map = {d["Division"]: d["DLI"] for d in digital_indexes_for_map}

curr_status_map = {d["Division"]: d["status"] for d in curr_indexes_for_map}
curr_score_map = {d["Division"]: d["median_final_index"] for d in curr_indexes_for_map}

# write a function to determine the color 
def determine_color(dig_status, curr_status):
    if "Needs Attention" in (dig_status, curr_status):
        return "red"
    elif "Good" in (dig_status, curr_status):
        return "green"
    else:
        return "orange"


# Create markers
markers = []
for d in district_data:
    division = d["name"]
    lat, lon = float(d["lat"]), float(d["long"])

    dig_status = dig_status_map.get(division)
    curr_status = curr_status_map.get(division)
    dig_score = dig_score_map.get(division)
    curr_score = curr_score_map.get(division)

    if dig_status is None or curr_status is None:
        continue  # skip if missing data

    color = determine_color(dig_status, curr_status)

    markers.append(
        dl.CircleMarker(
            center=[lat, lon],
            radius=10,
            color=color,
            fillColor=color,
            fillOpacity=0.7,
            children=[
                # dl.Tooltip(division, direction="bottom", permanent=False, offset=[0, 10], sticky=False),
                dl.Popup(html.Div([
                    html.H4(division),
                    html.Div([
                        html.B(division),
                        html.Div(f"Total Schools: {division_info[division]['total_schools']}"),
                        html.Div(f"Active Students: {division_info[division]['active_student_count']}"),
                        html.Hr(),
                        html.Button("📊 View Details", id={"type": "nav-btn", "index": division.lower()}, n_clicks=0)
                    ]),
                    html.Hr(),
                    html.Div("📊 Index Summary:"),
                    html.Table([
                        html.Tr([
                            html.Td("Curriculum Index:"),
                            html.Td(f"{curr_score:.1f}"),
                            html.Td(curr_status, style={"color": status_color_map[curr_status]})
                        ]),
                        html.Tr([
                            html.Td("Digital Index:"),
                            html.Td(f"{dig_score:.1f}"),
                            html.Td(dig_status, style={"color": status_color_map[dig_status]})
                        ])
                    ]),
                    html.Hr(),
                    html.Div("Status Counts:"),
                    html.Ul([html.Li(f"{k}: {v}") for k, v in division_info[division]["status_counts"].items()]),
                    html.Div("Type Counts:"),
                    html.Ul([html.Li(f"{k}: {v}") for k, v in division_info[division]["type_counts"].items()]),
                    

                # play around to make the popout experience better 
                ]), keepInView=False, autoPan=True)
            ]
        )
    )


# Full map layout with floating home button
pakistan_map = html.Div([
    dcc.Location(id="redirect", refresh=True),
    dcc.Store(id="map-config", data={"center": initial_center, "zoom": initial_zoom}),
    html.H2("Geographic Distribution", className="section-title"),
    
    html.Div([
        dl.Map(
            id="pakistan-map",
            center=initial_center,
            zoom=initial_zoom,
            children=[dl.TileLayer(), *markers],
            style={"width": "100%", "height": "500px", "position": "relative"}
        ),
        html.Button("🏠", id="reset-map-btn", title="Reset map", style={
            "position": "absolute",
            "top": "10px",
            "right": "10px",
            "zIndex": "1000",
            "fontSize": "18px",
            "backgroundColor": "white",
            "border": "1px solid lightgray",
            "borderRadius": "5px",
            "cursor": "pointer",
            "padding": "4px 8px"
        })
    ], style={"position": "relative"})  # parent container must be relative
])

# Register callback (inside dashboard_home_map.py if needed)
@callback(
    Output("map-config", "data"),
    Input("reset-map-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_map_config(n_clicks):
    return {"center": initial_center, "zoom": initial_zoom}

@callback(
    Output("pakistan-map", "center"),
    Output("pakistan-map", "zoom"),
    Input("map-config", "data"),
    prevent_initial_call=True
)
def update_map_center(data):
    return data["center"], data["zoom"]


# Callback to navigate
@callback(
    Output("redirect", "pathname"),
    Input({"type": "nav-btn", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True
)
def navigate_to_page(n_clicks_list):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    division = eval(button_id)["index"].lower()
    print("Triggered ID:", button_id)
    print("Redirecting to:", f"/{division}")
    print("➡️ NAVIGATION CALLBACK TRIGGERED")
    print("Triggered ID:", ctx.triggered[0]["prop_id"])
    print("Redirecting to:", f"/{division}")

    return f"/{division}"
