from dash import html
from process_data.scrape_kpis_home import grab_school_info, grab_students_enrolled, grab_attendace_metrics
from process_data.enuma_summary_metrics import grab_user_info
import os 
import json
from dashboard_home_map import pakistan_map
from dash import Input, Output, State, callback



# This will be the hompage for whenever we want to have a route




# set the assests paths
assets_path = os.path.join(os.path.dirname(__file__), "..", "assets")

# load the info that I need 
with open(os.path.join(assets_path, "school_counts_data.json")) as f:
    school_counts = json.load(f)

with open(os.path.join(assets_path, "school_coverage.json")) as f:
    school_coverage = json.load(f)

with open(os.path.join(assets_path, "closed_schools.json")) as f:
    closed_schools = json.load(f)

with open(os.path.join(assets_path, "missing_schools.json")) as f:
    missing_schools = json.load(f)

with open(os.path.join(assets_path, "student_main_ttwf_dist.json")) as f:
    student_dist = json.load(f)

with open(os.path.join(assets_path, "attendance_main.json")) as f:
    attendance_main = json.load(f)

with open(os.path.join(assets_path, "enuma_summary_metrics.json")) as f:
    enuma_main = json.load(f)

# grab the ids and names separatedly 
closed_schools_names = [val["School_Name"] for val in closed_schools]
missing_schools_names = [val["School_Name"] for val in missing_schools]



layout = html.Div(className='main-container', children=[
    html.H1("TTWF Pakistan Education Dashboard", className="dashboard-title"),
    html.Div(className="kpi-grid", children=[
        html.Div(className="kpi-card", children=[
            html.H3(str(school_counts["num_operational_schools"]), className="kpi-value"),
            html.P("Operational Schools", className="kpi-label"),
            html.Span("+12 this month", className="kpi-note")
        ]),
        html.Div(className="kpi-card", children=[
            html.H3(str(student_dist['active_students']), className="kpi-value"),
            html.P("Students Enrolled", className="kpi-label"),
            html.Span("+5.2% vs last year", className="kpi-note")
        ]),
        html.Div(className="kpi-card", children=[
            html.P("📉 Average Attendance", className="kpi-label kpi-subheader"),
            html.Div(className="attendance-kpi-row", children=[
                html.Div(className="attendance-kpi-box", children=[
                    html.Div(f"{attendance_main['historical']}%", className="kpi-attendance-value highlight-purple"),
                    html.Div("Historical", className="kpi-metric-label")
                ]),
                html.Div(className="attendance-kpi-box", children=[
                    html.Div(f"{attendance_main['past_month']}%", className="kpi-attendance-value highlight-purple"),
                            html.Div("Past Month", className="kpi-metric-label")
                ]),
                html.Div(className="attendance-kpi-box", children=[
                    html.Div(f"{attendance_main['past_week']}%", className="kpi-attendance-value highlight-purple"),
                    html.Div("Past Week", className="kpi-metric-label")
                ])
            ]),
            html.Span("Needs Attention", className="kpi-warning")
        ]),

        html.Div(className="kpi-card red", children=[
            html.H3(str(student_dist['dropout_rate']) + '%', className="kpi-value"),
            html.P("Dropout Rate", className="kpi-label"),
            html.Span("Critical - requires action", className="kpi-critical")
        ]),
        html.Div(className="kpi-card blue", children=[
            html.H3("27%", className="kpi-value"),
            html.P("Academic Performance", className="kpi-label"),
            html.Span("Requires intervention", className="kpi-warning")
        ])
    ]),
    
    html.Div(className="map-section", children=[pakistan_map])
         
])


# callbacks for the home page
@callback(
    Output("collapse-closed", "is_open"),
    Input("toggle-closed-btn", "n_clicks"),
    State("collapse-closed", "is_open"),
    prevent_initial_call=True
)
def toggle_closed_list(n, is_open):
    return not is_open if n else is_open

@callback(
    Output("collapse-missing", "is_open"),
    Input("toggle-missing-btn", "n_clicks"),
    State("collapse-missing", "is_open"),
    prevent_initial_call=True
)
def toggle_missing_list(n, is_open):
    return not is_open if n else is_open

@callback(
    Output("collapse-districts", "is_open"),
    Input("toggle-districts-btn", "n_clicks"),
    State("collapse-districts", "is_open"),
    prevent_initial_call=True
)
def toggle_districts(n, is_open):
    return not is_open if n else is_open

@callback(
    Output("collapse-divions", "is_open"),
    Input("toggle-divisions-btn", "n_clicks"),
    State("collapse-divions", "is_open"),
    prevent_initial_call=True
)
def toggle_divisions(n, is_open):
    return not is_open if n else is_open

@callback(
    Output("collapse-enuma-inactive", "is_open"),
    Input("toggle-enuma-inactive-btn", "n_clicks"),
    State("collapse-enuma-inactive", "is_open"),
    prevent_initial_call=True
)
def toggle_enuma_inactive(n, is_open):
    return not is_open if n else is_open

@callback(
    Output("collapse-enuma-act-miss-school", "is_open"),
    Input("toggle-enuma-act-miss-school-btn", "n_clicks"),
    State("collapse-enuma-act-miss-school", "is_open"),
    prevent_initial_call=True
)
def toggle_enuma_activity_missing(n, is_open):
    return not is_open if n else is_open

@callback(
    Output("collapse-enuma-curr-miss-school", "is_open"),
    Input("toggle-enuma-curr-miss-school-btn", "n_clicks"),
    State("collapse-enuma-curr-miss-school", "is_open"),
    prevent_initial_call=True
)
def toggle_enuma_curriculum_missing(n, is_open):
    return not is_open if n else is_open


if __name__ == "__main__":
    grab_school_info()
    grab_students_enrolled()
    grab_attendace_metrics()
    grab_user_info()