import dash
from dash import html, Output, Input, callback, dcc, callback_context, no_update, ALL
import os
import json
from pages.division_map_generator import generate_division_map
import pandas as pd
from pages.call_back_users import redirect_to_school



# set the assests paths
current_directory = os.path.join(os.path.dirname(__file__), '..')

# we load in the data sets that are needed 
final_dashboard_data = pd.read_csv(os.path.join(current_directory, 'final_aggregated_data', 'final_aggregated_data.csv'))
active_students_dashboard_data = pd.read_csv(os.path.join(current_directory, 
                                                          'final_aggregated_data', 'active_final_aggregated_data.csv'))
# we extract the information for the KPI cards
total_students_and_schools = final_dashboard_data.groupby(by = ['Division']).agg({'schoolName': 'nunique', 'userId':'nunique'}).reset_index()
active_students_and_schools = active_students_dashboard_data.groupby(by = ['Division']).agg({'schoolName':'nunique', 'userId':'nunique'}).reset_index()
division_info_schools_and_students = active_students_and_schools.merge(total_students_and_schools, on = 'Division', how = 'inner')
division_info_schools_and_students['dropoout_students'] = division_info_schools_and_students['userId_y'] - division_info_schools_and_students['userId_x']
division_info_schools_and_students['dropout_rate'] = round(division_info_schools_and_students['dropoout_students'] / division_info_schools_and_students['userId_y'] * 100)
division_info_schools_and_students.drop(columns=['schoolName_y', 'dropoout_students'], inplace = True)
division_info_schools_and_students.columns = ['Division', 'activeSchools', 'activeStudents', 'total_students', 'dropoutRate'] 

division_name = 'Hyderabad'

# get the totoal active schools 
num_operational_schools = division_info_schools_and_students.loc[division_info_schools_and_students['Division'] == division_name, 'activeSchools']

# active students 
num_active_students = division_info_schools_and_students.loc[division_info_schools_and_students['Division'] == division_name, 'activeStudents']

# get the dropout rate 
dropout_rate = division_info_schools_and_students.loc[division_info_schools_and_students['Division'] == division_name, 'dropoutRate']

# read in the map 
map, initial_center, initial_zoom = generate_division_map(division_name, active_students_dashboard_data)

layout = html.Div([
    dcc.Location(id="school-redirect", refresh=True),
    html.H1("Hyderabad Dashboard", className="dashboard-title"),
    html.Div(className="kpi-grid", children=[
        html.Div(className="kpi-card", children=[
            html.H3(num_operational_schools, className="kpi-value"),
            html.P("Operational Schools", className="kpi-label"),
            html.Span("+12 this month", className="kpi-note")
        ]),
        html.Div(className="kpi-card", children=[
            html.H3(num_active_students, className="kpi-value"),
            html.P("Students Enrolled", className="kpi-label"),
            html.Span("+5.2% vs last year", className="kpi-note")
        ]),
        html.Div(className="kpi-card red", children=[
            html.H3(dropout_rate, className="kpi-value"),
            html.P("Dropout Rate", className="kpi-label"),
            html.Span("Critical - requires action", className="kpi-critical")
        ]),
    ]), 
    html.Div(className="division-map-section", children = [map])
])

# then we have the callback for the map itself 
# this is a call back to just update and store the center data
@callback(
    Output("hyderabad-map-reset", "data"),
    Input("reset-hyderabad-map-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_map_config(n_clicks):
    return {"center": initial_center, "zoom": initial_zoom}

# Callback to update the stored reset data

@callback(
    Output("hyderabad-map", "center"),
    Output("hyderabad-map", "zoom"),
    Input("hyderabad-map-reset", "data"),
    prevent_initial_call=True
)
def update_map_center(data):
    return data["center"], data["zoom"]



