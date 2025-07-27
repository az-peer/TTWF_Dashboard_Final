import dash_leaflet as dl
from dash import html, Output, Input, dcc, callback, callback_context, no_update, ALL
import json
import os
import dash
import pandas as pd
import numpy as np
# run to grab the selected indexes
# attempting to change with the final index table  the old copy is in process data 
# we will attempt to also try to do this in pandas so that the assets stay clear otherwise debugging will be a pain


# Load assets
assets_path = os.path.join(os.path.dirname(__file__), "assets")

# also load in the data for the home page 
# for the maps we only need the active schools 
active_students_dashboard_data = pd.read_csv(os.path.join(assets_path, '..', 'final_aggregated_data','active_final_aggregated_data.csv'))

# Count users by Division and final_combined_index_category
# so this is the division and the count of the number of each kid in the category 
# the category is defined by average, gifted, poor
counts_for_category_final_index = active_students_dashboard_data.groupby(['Division', 'final_combined_index_category'])['userId'].count()
# Count total users per Division
# counts the total number of users per divions 
# Division and then the number of the counts 
totals_for_division = active_students_dashboard_data.groupby('Division')['userId'].count()
# Calculate actual percentages 
# now we turn the counts of each of the categories and then we turn this into a percentage
percentages = counts_for_category_final_index.div(totals_for_division, level=0) * 100
# now we round these values 
# this is like a pd data frame with division, final_combined_index_category, percentage
percentages = percentages.round(2).reset_index(name='percentage')

# Pivot to wide format
# ow we have final_combined_index_category as the columns 
# average, gifted, poor, and division as the index 
pivot_df = percentages.pivot(index='Division', columns='final_combined_index_category', values='percentage').fillna(0)
# we will weight gifted and poor as 2 times more likely then the others 

def compute_score(row):
    return 2 * row.get('gifted', 0) + 1 * row.get('average', 0) - 2 * row.get('poor', 0)

# a function to assign colors for the index 
# these numbers are just a proof of concept 
def assign_color(score):
    if score >= 70:
        return 'green'
    elif score >= 50:
        return 'orange'
    else:
        return 'red'
# we get the composite score
pivot_df['composite_score'] = pivot_df.apply(compute_score, axis=1)

# and then we also get th color we should assign each of the indexes 
pivot_df['color'] = pivot_df['composite_score'].apply(assign_color)
# we need the medians of each of the indexes
# this is what will be displayed in each of the pop up cards 
# we also need a way to add color meanings to all of the indexes 
# should also be green, orange, and,red 
main_map_popup_cards = active_students_dashboard_data.groupby(by = 'Division').agg({'schoolName':'nunique',
                                                             'userId':'count',
                                                             'final_combined_index':'median', 
                                                             'activity_learning_index':'median',
                                                             'curr_final_index':'median',
                                                             'dig_DLI':'median',
                                                             })

main_map_popup_cards.columns = ['num_schools', 'num_users', 'final_index', 'activity_index', 'curriculum_index', 'dig']

# then we will re-apply a function to actually categorize the columns 
# Your categorization function
def create_index_category(df, colname):
    p10 = df[colname].quantile(0.10)
    p90 = df[colname].quantile(0.90)
    
    def categorize(x):
        if pd.isna(x):
            return np.nan
        elif x < p10:
            return 'poor'
        elif x > p90:
            return 'gifted'
        else:
            return 'average'
    
    return df[colname].apply(categorize)

# write a function to extract what color should be displayed
def extract_popup_card_index_color(category):
    if category == 'gifted':
        return 'green'
    elif category == 'average':
        return 'orange'
    else:
        return 'red'

# then apply the function to the main popup cards 
# List of index columns to categorize
index_cols = ['final_index', 'activity_index', 'curriculum_index', 'dig']

# Apply the categorization to each index column
for col in index_cols:
    category_col = col + '_category'
    main_map_popup_cards[category_col] = create_index_category(main_map_popup_cards, col)


# these will be the main coordinates for the divisions read in from the assests 
with open(os.path.join(assets_path, "district_coords.json")) as f:
    district_data = json.load(f)


# Map center and zoom for the intial point
initial_center = [27.5, 69.3451]
initial_zoom = 6


# Create markers
markers = []
for d in district_data:
    # grab the name of the division 
    # and then we read in the latitude and the longitude for the plot 
    division = d["name"]
    lat, lon = float(d["lat"]), float(d["long"])

    # we gather all the indexes here for the division
    # lets first gather the main things from the pivot df 
    # lets first get the color for the actual division
    division_color = pivot_df.loc[division, 'color']
    # then lets grab the composite score
    division_composite_score = pivot_df.loc[division, 'composite_score']
    # then we can grab the percentages of gifted, average and poor
    division_composite_percentage_gifted = pivot_df.loc[division, 'gifted']
    division_composite_percentage_average = pivot_df.loc[division, 'average']
    division_composite_percentage_poor = pivot_df.loc[division, 'poor']

    # now we grab information from the main popup card  
    # first grab the final index 
    final_index = main_map_popup_cards.loc[division, 'final_index']
    # get the totoal number of schools 
    num_schools = main_map_popup_cards.loc[division, 'num_schools']
    # get the totoal number of users 
    num_students = main_map_popup_cards.loc[division, 'num_users']
    # then get the separate indexes 
    activity_index = main_map_popup_cards.loc[division, 'activity_index']
    # curr index 
    curriculum_index = main_map_popup_cards.loc[division, 'curriculum_index']
    # dig index 
    dig_index = main_map_popup_cards.loc[division, 'dig']

    # we need to extract the color of the point here for each of the indexes on the popup card 
    # we pass this into the function above 
    activity_index_color = extract_popup_card_index_color(
        main_map_popup_cards.loc[division, 'activity_index_category']
        )
    curriculum_index_color = extract_popup_card_index_color(
        main_map_popup_cards.loc[division, 'curriculum_index_category']
    )
    dig_index_color = extract_popup_card_index_color(
        main_map_popup_cards.loc[division, 'dig_category']
    )
    
    # now we create our markers 
    markers.append(
        dl.CircleMarker(
            center=[lat, lon],
            radius=10,
            # we set the colors for the points 
            color=division_color,
            fillColor=division_color,
            fillOpacity=0.7,
            children=[
                # dl.Tooltip(division, direction="bottom", permanent=False, offset=[0, 10], sticky=False),
                # this is the popup card when our mouse hovers over everything
                dl.Popup(html.Div([
                    html.H4(division),
                    html.Div([
                        html.B(division),
                        html.Div(f"Total Schools: {num_schools}"),
                        html.Div(f"Active Students: {num_students}"),
                        html.Hr(),
                        # then the button to go to the next page
                        html.Button("📊 View Details", id={"type": "nav-btn", "index": division.lower()}, n_clicks=0)
                    ]),
                    html.Hr(),
                    # then this will have the index summary for everything 
                    html.Div("📊 Index Summary:"),
                    html.Table([
                        html.Tr([
                            # we will start with the final index 
                            html.Td("Final Composite Index"),
                            html.Td(f"{final_index:.2f}", style={"color":division_color})
                        ]),
                        # the curriculum index
                        html.Tr([
                            html.Td("Curriculum Log Index"),
                            html.Td(f"{curriculum_index:.2f}", style={"color":curriculum_index_color})
                        ]),
                        # digital index
                        html.Tr([
                            html.Td("Digital Log Index"),
                            html.Td(f"{dig_index:.2f}", style={'color':dig_index_color})
                        ]),
                        html.Tr([
                            html.Td("Activity Log Index"),
                            html.Td(f"{activity_index:.2f}", style={'color':activity_index_color})
                        ])
                    ]),
                    
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
# this is the config for the map rest button
@callback(
    Output("map-config", "data"),
    Input("reset-map-btn", "n_clicks"),
    prevent_initial_call=True
)
# resets the map to the inital center and zoom
def reset_map_config(n_clicks):
    return {"center": initial_center, "zoom": initial_zoom}
# this is for the reload of the entire map page
# passes the above info to actually reset the information 
@callback(
    Output("pakistan-map", "center"),
    Output("pakistan-map", "zoom"),
    Input("map-config", "data"),
    prevent_initial_call=True
)
def update_map_center(data):
    return data["center"], data["zoom"]


# Callback to navigate through the pages for the subdivisions
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

    return f"/{division}"
