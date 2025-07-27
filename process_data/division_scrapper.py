import pandas as pd
import numpy as np
import json
import os

current_dir = os.path.dirname(__file__)

########################################### OBJECTIVE ##########################################################
'''
This file is dedicated to extracting the main singleton values on the main dashboard
'''
################################################################################################################
# first set the base directory 
current_dir = os.path.dirname(__file__)


def grab_school_info_by_division():
    '''
        Extracts summary metrics per Division and saves as a JSON for subpage views.
    '''
    # Load the master school list
    data_path = os.path.join(current_dir, "..", "cleaned_TTWF_DATA", "cleaned_master_school_list.csv")
    master_school_list = pd.read_csv(data_path)

    # Group by Division and build a dictionary for each
    division_info = {}

    for division, df_div in master_school_list.groupby("Division"):
        # Handle NaN division names
        if pd.isna(division):
            continue

        status_counts = df_div['Status'].value_counts()

        info = {
            "num_operational_schools": int(status_counts.get("Active", 0)),
            "num_closed_schools": int(status_counts.get("Closed", 0)),
            "num_missing_status_schools": int(status_counts.get("missing", 0)),
            "num_total_historical_school": len(df_div),
            "closed_schools": df_div.loc[df_div['Status'] == "Closed", ['School_Id', 'School_Name']].to_dict(orient="records"),
            "missing_schools": df_div.loc[df_div['Status'] == "missing", ['School_Id', 'School_Name']].to_dict(orient="records"),
            "districts_covered": sorted(df_div['District'].dropna().unique().tolist()),
            "num_districts": int(df_div['District'].nunique())
        }

        division_info[division] = info

    # Save the full dictionary
    with open(os.path.join(current_dir, "..", "assets", "sub_page_main_info.json"), "w+") as f:
        json.dump(division_info, f, indent=2)

def grab_students_enrolled_by_division():
    '''
        Computes student enrollment stats (total, active, dropout rate) per division and saves to JSON.
    '''
    master_school_path = os.path.join(current_dir, '..', 'cleaned_TTWF_DATA', 'cleaned_master_school_list.csv')
    users_df_path = os.path.join(current_dir,  '..', 'ENUMA_DATA', 'enuma_users_df.csv')


    master_school_list = pd.read_csv(master_school_path)
    users_df = pd.read_csv(users_df_path)

    # we need to merge the master school list with the other data sets 
    master_school_list['School_Code_3'] = master_school_list['School_Id'].apply(lambda x:x[:3]).astype(int)

    # merge the full users with the master_school_list and only keep the division column 
    columns_to_keep = users_df.columns.tolist()
    columns_to_keep.append('Division')
    columns_to_keep
    users_df = users_df.merge(master_school_list, left_on = 'schoolUID', right_on='School_Code_3', how = 'left').loc[:, columns_to_keep]

    # Prepare dictionary
    division_student_info = {}

    for division, df_div in users_df.groupby("Division"):
        if pd.isna(division):
            continue

        status_counts = df_div['activeStatus'].value_counts()

        
        dropout_students = status_counts.get(False, 0)
        active_students = status_counts.get(True, 0)
        total_students  = active_students + dropout_students
        dropout_rate = dropout_students / total_students if total_students > 0 else 0

        division_student_info[division] = {
            "total_students": int(total_students),
            "active_students": int(active_students),
            "dropout_rate": round(dropout_rate * 100, 2)  # percentage, rounded
        }


    # Save to JSON
    with open(os.path.join(current_dir, "..", "assets", "sub_page_main_student_info.json"), "w+") as f:
        json.dump(division_student_info, f, indent=2)


grab_school_info_by_division()
grab_students_enrolled_by_division()