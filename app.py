import dash
from dash import html, dcc, Input, Output, callback, State
import dash_bootstrap_components as dbc
from process_data.scrape_kpis_home import grab_school_info, grab_students_enrolled, grab_attendace_metrics
from process_data.enuma_summary_metrics import grab_user_info
import json
import os
from routes import get_layout
from pages.home import layout
from pages.call_back_users import redirect_to_school
# register this as the home pagep


# run data scrapping before the app starts
# we run python scripts to grab this 
# grab_school_info()
# grab_students_enrolled()
# grab_attendace_metrics()
# grab_user_info()


# set the assests paths
assets_path = os.path.join(os.path.dirname(__file__), "assets")

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


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# add the access link for multiple pages 
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="main-content")
])

app.title = "TTWF Pakistan Dashboard"


def wrap_with_main_layout(content, pathname):
    show_sidebar = pathname in ['/', 'home']
    return html.Div([
        # this line causes constant call backs 
        # dcc.Location(id="url"),
        # TOP NAVBAR
        html.Div(className="top-navbar", children=[
            html.Div(className="navbar-left", children=[
                html.Img(src="/assets/TTWF_logo2.png", className="logo-img"),
                html.H2([
                    html.Span("TTWF", className="brand-english"),
                    html.Span(" پاکستان", className="brand-urdu")
                ], className="brand-title")
            ]),
            html.Div(className="navbar-center", children=[
                dcc.Input(
                    placeholder="Search schools, districts, students...",
                    type="text",
                    className="search-input"
                )
            ]),
            html.Div(className="navbar-right", children=[
                html.Button("🌙", className="nav-icon-btn", id="dark-mode-btn"),
                html.Button("🔔", className="nav-icon-btn", id="reminder-btn"),
                html.Button("👤", className="nav-icon-btn", id="profile-btn")
            ])
        ]),

        # WRAPS SIDEBAR AND MAIN CONTENT
        html.Div(className="dashboard-wrapper", children=[

            # SIDEBAR
            html.Div(className="sidebar-content", children=[
                html.Div(className="sidebar-overview-box", children=[
                    html.H3("📊 Data Overview For TTWF", className="sidebar-section-title"),
                    html.Div(className="sidebar-kpi", children=[
                        html.Div("Total Historical Schools", className="sidebar-kpi-title"),
                        html.Div(str(school_counts["num_total_historical_school"]), className="sidebar-kpi-value highlight-purple")
                    ]),
                    html.Div(className="sidebar-kpi", children=[
                        html.Div("Closed Schools", className="sidebar-kpi-title"),
                        html.Div(str(school_counts["num_closed_schools"]), className="sidebar-kpi-value highlight-purple"),
                        html.Button(html.Img(src="/assets/mag_glass.png", style={"height": "20px", "width": "20px", 'padding-left':'5px'}
                                            , id="toggle-closed-btn", className="sidebar-toggle-btn")),
                        dbc.Collapse(id="collapse-closed", is_open=False, children=[
                            html.Ul([html.Li(name) for name in closed_schools_names], className="school-list")
                        ])
                    ]),
                    html.Div(className="sidebar-kpi", children=[
                        html.Div("Schools With Missing Status", className="sidebar-kpi-title"),
                        html.Div(str(school_counts["num_missing_status_schools"]), className="sidebar-kpi-value highlight-purple"),
                        html.Button(html.Img(src="/assets/mag_glass.png", style={"height": "20px", "width": "20px", 'padding-left':'5px'}), id='toggle-missing-btn', className="sidebar-toggle-btn"),
                        dbc.Collapse(id="collapse-missing", is_open=False, children=[
                            html.Ul([html.Li(name) for name in missing_schools_names], className="school-list")
                        ])
                    ]),
                    html.Div(className='sidebar-kpi', children=[
                        html.Div("Districts Covered", className="sidebar-kpi-title"),
                        html.Div(str(school_coverage["num_districts"]), className="sidebar-kpi-value highlight-purple"),
                        html.Button(html.Img(src="/assets/mag_glass.png", style={"height": "20px", "width": "20px", 'padding-left':'5px'}), id='toggle-districts-btn', className="sidebar-toggle-btn"),
                        dbc.Collapse(id="collapse-districts", is_open=False, children=[
                            html.Ul([html.Li(name) for name in school_coverage["districts_covered"]], className="school-list")
                        ])
                    ]),
                    html.Div(className='sidebar-kpi', children=[
                        html.Div("Divisions", className="sidebar-kpi-title"),
                        html.Div(str(school_coverage["num_divisions"]), className="sidebar-kpi-value highlight-purple"),
                        html.Button(html.Img(src="/assets/mag_glass.png", style={"height": "20px", "width": "20px", 'padding-left':'5px'}), id='toggle-divisions-btn', className="sidebar-toggle-btn"),
                        dbc.Collapse(id="collapse-divions", is_open=False, children=[
                            html.Ul([html.Li(name) for name in school_coverage["divisions_covered"]], className="school-list")
                        ])
                    ])
                ]),
                html.Div(className="sidebar-overview-box", children=[
                    html.H3("📊 Data Overview For ENUMA Analtyics", className="sidebar-section-title"),
                    html.Div(className="sidebar-kpi", children=[
                        html.Div("Total Users Tracked", className="sidebar-kpi-title"),
                        html.Div(str(enuma_main['total_users']), className="sidebar-kpi-value highlight-purple")
                    ]),
                    html.Div(className="sidebar-kpi", children=[
                        html.Div("Active Users Tracked", className="sidebar-kpi-title"),
                        html.Div(str(enuma_main["active_users"]), className="sidebar-kpi-value highlight-purple")
                    ]),
                    html.Div(className="sidebar-kpi", children=[
                        html.Div("Total Schools Present", className="sidebar-kpi-title"),
                        html.Div(str(enuma_main["active_schools"]), className="sidebar-kpi-value highlight-purple")
                    ]),
                    html.Div(className="sidebar-kpi", children=[
                        html.Div("Inactive Schools", className="sidebar-kpi-title"),
                        html.Div(str(enuma_main["num_inactive_schools"]), className="sidebar-kpi-value highlight-purple"),
                        html.Button(html.Img(src="/assets/mag_glass.png", style={"height": "20px", "width": "20px", 'padding-left':'5px'}
                                            , id="toggle-enuma-inactive-btn", className="sidebar-toggle-btn")),
                        dbc.Collapse(id="collapse-enuma-inactive", is_open=False, children=[
                            html.Ul([html.Li(name) for name in enuma_main['inactive_schools']], className="school-list")
                        ])
                    ]),
                    html.Div(className="sidebar-kpi", children=[
                        html.Div("Schools Not In Activity Log", className="sidebar-kpi-title"),
                        html.Div(str(enuma_main["num_schools_not_in_al"]), className="sidebar-kpi-value highlight-purple"),
                        html.Button(html.Img(src="/assets/mag_glass.png", style={"height": "20px", "width": "20px", 'padding-left':'5px'}
                                            , id="toggle-enuma-act-miss-school-btn", className="sidebar-toggle-btn")),
                        dbc.Collapse(id="collapse-enuma-act-miss-school", is_open=False, children=[
                            html.Ul([html.Li(name) for name in enuma_main['schools_not_in_all']], className="school-list")
                        ])
                    ]),
                    html.Div(className="sidebar-kpi", children=[
                        html.Div("Schools Not In Curriculum Tests Log", className="sidebar-kpi-title"),
                        html.Div(str(enuma_main["num_schools_not_in_curr"]), className="sidebar-kpi-value highlight-purple"),
                        html.Button(html.Img(src="/assets/mag_glass.png", style={"height": "20px", "width": "20px", 'padding-left':'5px'}
                                            , id="toggle-enuma-curr-miss-school-btn", className="sidebar-toggle-btn")),
                        dbc.Collapse(id="collapse-enuma-curr-miss-school", is_open=False, children=[
                            html.Ul([html.Li(name) for name in enuma_main['schools_not_in_curr']], className="school-list")
                        ])
                    ])
                ])
            ]),

            # DYNAMIC PAGE CONTENT GOES HERE
            html.Div(className="main-container", children=content)
        ]) if show_sidebar else html.Div(className="main-container", children=content),
    ])




# this is called a callback function
# it basically takes in path name and then fills it in with whatever the main content is for the output
# the problem is right herre 

@app.callback(
    Output("main-content", "children"),
    Input("url", "pathname")
)
def render_page(pathname): # what dash calls when pathname changes 
    content = get_layout(pathname)# this is my routing function refer above
    if content: 
        return wrap_with_main_layout(content, pathname) # fill out the display above 
    return wrap_with_main_layout(html.Div([
        html.H1("404 - Page not found"),
        html.P(f"No page exists at '{pathname}'")
    ]), pathname) # pathname allows for boolean custom control




if __name__ == "__main__":
    app.run(debug=True)
