import dash_leaflet as dl
from dash import html, dcc, callback_context, no_update, ALL, callback, Output, Input
import json
import os
import pandas as pd
from functools import lru_cache


# this is a function is what will generate the maps for all the ditricts 
from functools import lru_cache

def generate_division_map(division_name, coords_df, dig_score=None, curr_score=None):
    # we will now read in the data to color the dots 

    # Load coordinates for this division
    # this is what we need to fix 
    # we will be getting the centers for the actual dataframe now 
    # lets read the division center from the original json 
    assets_path = os.path.join(os.path.dirname(__file__), '..', "assets")

    with open(os.path.join(assets_path, "district_coords.json")) as f:
        district_data_list = json.load(f)

    # read in the info with the students information
    student_information = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 
                                                   'school_popup_card_info','division_info_schools_and_students.csv'))

    student_information = student_information.loc[student_information['Division'] == division_name, :]

    # school popup card information
    pop_up_card_information = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 
                                                   'school_popup_card_info','school_popup_card_info.csv'))
    
    
    
    pop_up_card_information = pop_up_card_information[pop_up_card_information['Division'] == division_name]

    
    district_data_list = {
        entry["name"]: {
        "lat": float(entry["lat"]),
        "lon": float(entry["long"])}
        for entry in district_data_list
    }
    
    d = district_data_list[division_name]
    


    # then we grab the coordinates 
    coordinates = coords_df.loc[coords_df['Division'] == division_name, 
                                      ['schoolName','final_jittered_Loc_X', 'final_jittered_Loc_Y']]
    # define the center for each of the different division that we have 
    # we got this online we may have to switch to just the coordinates.yaml
    
    
    # Define center and zoom specific to the division (optional)
    # these are also flipped as well
    initial_center = (d['lat'], 
                      d['lon'])
    initial_zoom = 8

    markers = []
    # we iterate through the actual data points
    # for now we are only including the actual points
    # d should be one of the values
    for school in coordinates.schoolName:
        
        # exttract all the school info from this data 
        name = school
        lat = float(coordinates.loc[coordinates['schoolName'] == school, ['final_jittered_Loc_X']].values[0])
        lon = float(coordinates.loc[coordinates['schoolName'] == school, ['final_jittered_Loc_Y']].values[0])
        # grab the color to fill in the points
        # # needs to be updated 
        # now we fetch the color from the 
        color = pop_up_card_information.loc[pop_up_card_information['schoolName'] == school, 'final_combined_index_color'].iloc[0]
        
        # we read in the popcard information 
        num_active_students = int(student_information.loc[student_information['schoolName'] == school, 'num_active_students'].iloc[0])
        num_total_students = int(student_information.loc[student_information['schoolName'] == school, 'num_total_students'].iloc[0])
        dropout_rate = int(student_information.loc[student_information['schoolName'] == school, 'dropout_rate'].iloc[0])

        # and then we fetch all of the index information 
        final_combined_index = float(pop_up_card_information.loc[pop_up_card_information['schoolName'] == school, 'final_combined_index'].iloc[0])
        active_log_index = float(pop_up_card_information.loc[pop_up_card_information['schoolName'] == school, 'activity_learning_index'].iloc[0])
        curr_log_index = float(pop_up_card_information.loc[pop_up_card_information['schoolName'] == school, 'curr_final_index'].iloc[0])
        dig_log_index = float(pop_up_card_information.loc[pop_up_card_information['schoolName'] == school, 'dig_DLI'].iloc[0])
        
        active_log_index_color = pop_up_card_information.loc[pop_up_card_information['schoolName'] == school, 
                                                        'activity_learning_index_category_color'].iloc[0]
        
        curr_log_index_color = pop_up_card_information.loc[pop_up_card_information['schoolName'] == school, 
                                                        'curr_final_index_color'].iloc[0]
        
        dig_log_index_color = pop_up_card_information.loc[pop_up_card_information['schoolName'] == school, 
                                                        'dig_DLI_category_color'].iloc[0]
        
        # append the coordinates to the markers list 
        markers.append(
            dl.CircleMarker(
                # looks like I accidently mixed up the long and lat fix in code review for later
                center=[lat, lon],
                radius=5,
                color=color,
                fillColor=color,
                fillOpacity=0.7,
                children=[
                    # now we need to decide how to get the exact students
                    # this is the popup information that will appear for each of the school 
                    dl.Popup(html.Div([
                        html.H4(name),
                        html.Div([
                            html.Div(f"Total Students: {num_total_students}"),
                            html.Div(f"Active Students: {num_active_students}"),
                            html.Div(f"Dropout Rate: {dropout_rate}%"),
                            # adding button to get to the school page for more info
                            html.Button("📊 View Details", id = {"type": "school-nav-btn", "index": school}, n_clicks=0)
                        ]),
                        html.Hr(),
                        html.Div("📊 Index Summary:"),
                        html.Table([
                            html.Tr([
                                html.Td("Final Combined Index"),
                                html.Td(f"{final_combined_index}", style = {'color':color})
                            ]),
                            html.Tr([
                                html.Td("Activity Log Index"),
                                html.Td(f"{active_log_index:}", style = {'color':active_log_index_color})
                            ]),
                            html.Tr([
                                html.Td("Curriculum Index"),
                                html.Td(f"{curr_log_index}", style = {'color':curr_log_index_color})
                            ]),
                            html.Tr([
                                html.Td("Digital Learning Index"),
                                html.Td(f"{dig_log_index}", style={'color':dig_log_index_color})
                            ])
                        ])
                        ]), keepInView=False, autoPan=True)
                    ]
            )
        )

    return (html.Div([
        # create the reset link but use dcc.Store so we dont have to reload the page
        dcc.Store(id = f'{division_name.lower()}-map-reset', data = {"center":initial_center, "zoom":initial_zoom}),
        # add heading 
        html.H2(f"School Distribution of {division_name}"),
        # create the actual map for the division 
        dl.Map(
            id=f"{division_name.lower()}-map",
            center=initial_center,
            zoom=initial_zoom,
            children=[
                dl.TileLayer(),
                *markers
            ],
            style={"width": "100%", "height": "500px", "marginTop": "20px"}
        ),
        # add the recentering of the map 
        html.Button("🏠", id=f"reset-{division_name.lower()}-map-btn", title="Reset map", style = {
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
    ], style = {"position":"relative"}), initial_center, initial_zoom)


'''
# add a call back for all the buttons
@callback(
    Output("redirect", "pathname"),
    Output("redirect", "search"),
    Input({'type':'school-nav-btn', 'index':ALL}, "n_clicks"),
    prevent_initial_call = True
)
def navigate_to_school(n_clicks_list):
    triggered = callback_context.triggered
    if not triggered:
        return no_update, no_update
    
    button_id = eval(triggered[0]['prop_id'].split('.')[0])
    school_id = button_id['index']
    return "/school", f"?school_id={school_id}"
'''