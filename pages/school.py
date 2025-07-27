from dash import html, dcc, Input, Output, State, callback, ctx, html, dash_table
import dash
import pandas as pd 
from urllib.parse import parse_qs
import os
import plotly.express as px


# this will be the static dashboard that we load in for the final component 
# this is what we will attempt to use for this 

# we set the layout for the schools for now to be nothing 

layout = html.Div([
    # dcc.Location(id='url', refresh=False),  # Make sure this is available here
    html.Div(id="school-detail-content")
])

# now we read in the active students info across all the schools to display a table 
active_students_data = pd.read_csv(os.path.join(
    os.path.dirname(__file__), '..', 'final_aggregated_data', 'student_data_total.csv'
    ))


# grab the selected columns 
columns_to_display_activity = ['userId', 'userRegdate', 
                      'activity_completion_rate', 
                      'activity_eng_course_final',
                      'activity_eng_level_final',
                      'activity_eng_unit_final',
                      'activity_eng_lesson_final',
                      'activity_mat_course_final',
                      'activity_mat_level_final',
                      'activity_mat_unit_final',
                      'activity_mat_lesson_final',
                      'activity_last_session_gap',
                      'activity_eng_perf_bin',
                      'activity_mat_perf_bin',
                      'activity_is_mature',
                      'activity_consistency_score',
                      'missing_activity_log_index',
                      'activity_learning_index_category',
                      'activity_completion_rate_category',
                      'activity_avg_session_gap_category',
                      'activity_max_session_gap_category',
                      'activity_last_session_gap_category',
                      'activity_num_gaps_gt_3_category',
                      'activity_num_gaps_gt_7_category',
                      'activity_lessons_attempted_per_day_category',
                      'activity_lessons_completed_per_day_category',
                      'activity_consistency_score_category',
                      'activity_completion_rate_color',
                      'activity_avg_session_gap_color',
                      'activity_max_session_gap_color',
                      'activity_last_session_gap_color',
                      'activity_num_gaps_gt_3_color',
                      'activity_num_gaps_gt_7_color',
                      'activity_lessons_attempted_per_day_color',
                      'activity_lessons_completed_per_day_color',
                      'activity_consistency_score_color',
                      'activity_learning_index_color'







                      ]

columns_to_display_curr = [
    'userId',
    'curr_placement_index',
    'curr_placement_score_eng',
    'curr_placement_score_mat',
    'curr_placement_level_eng',
    'curr_placement_level_mat',
    'curr_learning_index_overall',
    'curr_learning_index_eng',
    'curr_learning_index_mat',
    'curr_raw_learning_rate_eng',
    'curr_raw_learning_rate_mat',
    'curr_engagement_index',
    'curr_num_sessions',
    'curr_num_problems_attempted',
    'curr_active_days',
    'curr_days_between',
    'curr_raw_engagement_score',
    'curr_weight_sum',
    'curr_final_index',
    'curr_student_group',
    'missing_curr_final_index',
    'curr_final_index_category',
    'curr_placement_index_category',
    'curr_placement_score_eng_category',
    'curr_placement_score_mat_category',
    'curr_placement_level_eng_category',
    'curr_placement_level_mat_category',
    'curr_num_placement_tests_category',
    'curr_learning_index_eng_category',
    'curr_learning_index_mat_category',
    'curr_raw_learning_rate_eng_category',
    'curr_raw_learning_rate_mat_category',
    'curr_engagement_index_category',
    'curr_num_sessions_category',
    'curr_raw_engagement_score_category',
    'curr_placement_index_color',
    'curr_placement_score_eng_color',
    'curr_placement_score_mat_color',
    'curr_placement_level_eng_color',
    'curr_placement_level_mat_color',
    'curr_num_placement_tests_color',
    'curr_learning_index_eng_color',
    'curr_learning_index_mat_color',
    'curr_raw_learning_rate_eng_color',
    'curr_raw_learning_rate_mat_color',
    'curr_engagement_index_color',
    'curr_num_sessions_color',
    'curr_raw_engagement_score_color']

columns_to_display_dig = ['userId', 'dig_total_attempted', 'dig_total_correct','dig_DLI','missing_dig_DLI','dig_DLI_category']

columns_to_diplay_final = ['userId', 'final_combined_index', 'final_combined_index_category']

# we create a function that will render the layout based off of what function was created
# we also add a callback to this 
@callback(
    Output('school-detail-content', 'children'),
    Input('url', 'search')  # listen to the global Location component
)
def render_school_page(query_string):
    # read in the data 


    # then we grab a 

    school_id = parse_qs(query_string.lstrip("?")).get("school_id", [None])[0]


    
    # we first read in the aggregated data from the school 
    active_students_per_school = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'school_aggregated_data', 'active_students_per_school.csv'))

    # then we filter by the school_id 
    num_students = active_students_per_school.loc[active_students_per_school['schoolName'] == school_id, 'userId'].iloc[0]

    # then we read in the data for the pie charts 
    pie_chart_data = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'school_aggregated_data', 'distribution_pct.csv'))

    # then we filter by school id and then grab the info we want
    # we also track the columns we want to plot 
    activity_log_columns = ['average_activity', 'gifted_activity', 'needs attention_activity'] 
    curriculum_log_columns = ['average_curriculum', 'gifted_curriculum', 'poor_curriculum']
    dig_log_columns = ['average_dig', 'gifted_dig', 'poor_dig']
    fin_index_columns = ['average_fin', 'gifted_fin', 'poor_fin']
    school_row_activity = pie_chart_data.loc[pie_chart_data['schoolName'] == school_id, activity_log_columns].squeeze()
    school_row_curr = pie_chart_data.loc[pie_chart_data['schoolName'] == school_id, curriculum_log_columns].squeeze()
    school_row_dig = pie_chart_data.loc[pie_chart_data['schoolName'] == school_id, dig_log_columns].squeeze()
    school_row_fin = pie_chart_data.loc[pie_chart_data['schoolName'] == school_id, fin_index_columns].squeeze()

    
    



    if school_id is None:
        return html.Div("No school selected.")
    return html.Div([
        # create the top nav bar first 
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
        html.H2(f"School {school_id}"), 
        html.Div(className = 'school_kpis', children = [
            html.Div(className = "school-kpi-card", children = [
                    html.H3(str(num_students), className = 'school-info'),
                    html.P("Active Students In ENUMA")
            ]),
            html.Div(className = 'school-info-grid',  style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '50px', 'justifyContent': 'center'}, children = [
                html.Div(className = "school-kpi-card", style={'width': '300px'},children = [
                    html.P("Final Composite Index Distribution" ,className = 'pie-chart'),
                    dcc.Graph(id = 'graph-final', style = {'height':'250px'}),
                    html.P("Names:"),
                    dcc.Dropdown(
                        id='names-final', 
                        options=[{'label': col.replace('_fin', '').title(), 'value': col} for col in fin_index_columns], 
                        value=fin_index_columns[0], clearable=False
                        )
                ]),
                html.Div(className = "school-kpi-card", style={'width': '300px'} ,children = [
                    html.P("Activity Log Index Distribution", className = 'pie-chart'),
                    dcc.Graph(id = 'graph-act', style = {'height':'250px'}),
                    html.P("Names:"),
                    dcc.Dropdown(
                        id='names-act', 
                        options=[{'label': col.replace('_activity', '').title(), 'value': col} for col in activity_log_columns], 
                        value=activity_log_columns[0], clearable=False
                        )
                ]),
                html.Div(className = 'school-kpi-card', style={'width': '300px'},children = [
                    html.P("Curriculum Index Distribution", className = 'pie-chart'),
                    dcc.Graph(id = 'graph-curr', style = {'height':'250px'}),
                    html.P("Names:"),
                    dcc.Dropdown(
                        id='names-curr', 
                        options=[{'label': col.replace('_curriculum', '').title(), 'value': col} for col in curriculum_log_columns], 
                        value=curriculum_log_columns[0], clearable=False
                    )
                    
                ]),
                html.Div(className = 'school-kpi-card', style={'width': '300px'},children = [
                    html.P("Digital Index Distribution", className = 'pie-chart'),
                    dcc.Graph(id = 'graph-dig', style = {'height':'250px'}),
                    html.P("Names:"),
                    dcc.Dropdown(
                        id='names-dig', 
                        options=[{'label': col.replace('_dig', '').title(), 'value': col} for col in dig_log_columns], 
                        value=dig_log_columns[0], clearable=False
                    )
                    
                ])
            ])
        ]),
        html.Div(className = 'student-info-data', children = [
            html.H3("Student Data Table", className = 'student-data'),
            html.Label("Select Index Type:"),
            dcc.Dropdown(
                id = 'table-options-menu',
                options = [
                    {'label': 'Activity', 'value': 'activity'},
                    {'label': 'Curriculum', 'value': 'curr'},
                    {'label': 'Digital', 'value': 'dig'},
                    {'label': 'Final', 'value': 'final'}
                ], value = 'activity',
                clearable = False
            )
        ]), 
        dash_table.DataTable(
            id = 'student-table-data',
            sort_action='native',
            page_size = 15,
            style_table = {'overflowX': 'auto'},
            style_cell = {'textAlign': 'left', 'minWidth': '120px', 'whiteSpace': 'normal'}
        )
    ])


@callback(
    Output('graph-final', 'figure'),
    Input('names-final', 'value'),
    Input('url', 'search')
)
def update_final_pie(selected_value, query_string):
    school_id = parse_qs(query_string.lstrip("?")).get("school_id", [None])[0]
    
    pie_chart_data = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'school_aggregated_data', 'distribution_pct.csv'))

    fin_index_columns = ['average_fin', 'gifted_fin', 'poor_fin']
    school_row = pie_chart_data.loc[pie_chart_data['schoolName'] == school_id, fin_index_columns].squeeze()

    if school_id is None or school_row.empty:
        return px.pie(title="No data available")

    # Create full pie chart
    fig = px.pie(
        names=[col.replace('_fin', '') for col in school_row.index],
        values=school_row.values,
        title="",
        color=school_row.index.str.replace('_fin', ''),
        color_discrete_map={'average': 'orange', 'gifted': 'green', 'poor': 'red', 'needs attention': 'red'}
    )
    

    # Highlight selected slice
    selected_index = fin_index_columns.index(selected_value)
    pull_values = [0.1 if i == selected_index else 0 for i in range(len(fin_index_columns))]
    fig.update_traces(pull=pull_values)

    fig.update_layout(showlegend=False)


    return fig


@callback(
    Output('graph-act', 'figure'),
    Input('names-act', 'value'),
    Input('url', 'search')
)
def update_act_pie(selected_value, query_string):
    school_id = parse_qs(query_string.lstrip("?")).get("school_id", [None])[0]
    pie_chart_data = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'school_aggregated_data', 'distribution_pct.csv'))

    activity_log_columns = ['average_activity', 'gifted_activity', 'needs attention_activity'] 
    school_row = pie_chart_data.loc[pie_chart_data['schoolName'] == school_id, activity_log_columns].squeeze()

    if school_id is None or school_row.empty:
        return px.pie(title="No data available")

    # Create full pie chart
    fig = px.pie(
        names=[col.replace('_activity', '') for col in school_row.index],
        values=school_row.values,
        title="",
        color=school_row.index.str.replace('_activity', ''),
        color_discrete_map={'average': 'orange', 'gifted': 'green', 'poor': 'red', 'needs attention': 'red'}
    )

    # Highlight selected slice
    selected_index = activity_log_columns.index(selected_value)
    pull_values = [0.1 if i == selected_index else 0 for i in range(len(activity_log_columns))]
    fig.update_traces(pull=pull_values)
    fig.update_layout(showlegend=False)



    return fig



@callback(
    Output('graph-curr', 'figure'),
    Input('names-curr', 'value'),
    Input('url', 'search')
)
def update_curr_pie(selected_value, query_string):
    school_id = parse_qs(query_string.lstrip("?")).get("school_id", [None])[0]
    pie_chart_data = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'school_aggregated_data', 'distribution_pct.csv'))

    curriculum_log_columns = ['average_curriculum', 'gifted_curriculum', 'poor_curriculum']
    school_row = pie_chart_data.loc[pie_chart_data['schoolName'] == school_id, curriculum_log_columns].squeeze()

    if school_id is None or school_row.empty:
        return px.pie(title="No data available")

    # Create full pie chart
    fig = px.pie(
        names=[col.replace('_curriculum', '') for col in school_row.index],
        values=school_row.values,
        title="",
        color=school_row.index.str.replace('_curriculum', ''),
        color_discrete_map={'average': 'orange', 'gifted': 'green', 'poor': 'red', 'needs attention': 'red'}
    )

    # Highlight selected slice
    selected_index = curriculum_log_columns.index(selected_value)
    pull_values = [0.1 if i == selected_index else 0 for i in range(len(curriculum_log_columns))]
    fig.update_traces(pull=pull_values)
    fig.update_layout(showlegend=False)


    return fig



@callback(
    Output('graph-dig', 'figure'),
    Input('names-dig', 'value'),
    Input('url', 'search')
)
def update_dig_pie(selected_value, query_string):
    school_id = parse_qs(query_string.lstrip("?")).get("school_id", [None])[0]
    pie_chart_data = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'school_aggregated_data', 'distribution_pct.csv'))

    dig_log_columns = ['average_dig', 'gifted_dig', 'poor_dig']
    school_row = pie_chart_data.loc[pie_chart_data['schoolName'] == school_id, dig_log_columns].squeeze()

    if school_id is None or school_row.empty:
        return px.pie(title="No data available")

    # Create full pie chart
    fig = px.pie(
        names=[col.replace('_dig', '') for col in school_row.index],
        values=school_row.values,
        title="",
        color=school_row.index.str.replace('_dig', ''),
        color_discrete_map={'average': 'orange', 'gifted': 'green', 'poor': 'red', 'needs attention': 'red'}
    )

    # Highlight selected slice
    selected_index = dig_log_columns.index(selected_value)
    pull_values = [0.1 if i == selected_index else 0 for i in range(len(dig_log_columns))]
    fig.update_traces(pull=pull_values)
    fig.update_layout(showlegend=False)
 

    return fig


# then we have the callback for the actual table 

@callback(
    Output('student-table-data', 'data'),
    Output('student-table-data', 'columns'),
    Output('student-table-data', 'style_data_conditional'),
    Input('table-options-menu', 'value'),
    Input('url', 'search')
)
def update_student_table(category, query_string):
    from urllib.parse import parse_qs
    school_id = parse_qs(query_string.lstrip("?")).get("school_id", [None])[0]

    df = active_students_data.copy()
    df = df.loc[df['schoolName'] == school_id, :]

    columns_map = {
        'activity': columns_to_display_activity,
        'curr': columns_to_display_curr,
        'dig': columns_to_display_dig,
        'final': columns_to_diplay_final
    }

    selected_columns = columns_map.get(category, [])
    df = df[selected_columns]

    # Define table columns
    table_columns = [{"name": col, "id": col} for col in df.columns]

    # Build conditional styling from *_color columns
    style_conditional = []
    for col in df.columns:
        if col.endswith('_color'):
            color_base = col.replace('_color', '')
            if color_base in df.columns:
                for i, color in enumerate(df[col]):
                    style_conditional.append({
                        'if': {'filter_query': f'{{userId}} = "{df["userId"].iloc[i]}"', 'column_id': color_base},
                        'backgroundColor': color
                    })

    return df.to_dict('records'), table_columns, style_conditional



