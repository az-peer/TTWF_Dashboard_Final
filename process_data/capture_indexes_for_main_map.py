import pandas as pd 
import numpy as np
import json
import os

# This file is to gather the data for all the collective indexes to be stored here and played around with 
current_dir = os.path.dirname(__file__)

def grab_indexes():
    # we first need to grab the master school list in order to merge with the division
    master_school_path = os.path.join(current_dir, '..', 'cleaned_TTWF_DATA', 'cleaned_master_school_list.csv')
    # we first need to grab the master school list in order to merge with the division
    master_school_path = os.path.join(current_dir, '..', 'cleaned_TTWF_DATA', 'cleaned_master_school_list.csv')
    full_student_index_activity_log_path = os.path.join(current_dir, '..', 'ENUMA_DATA', 'full_student_index_activity_log.csv')
    users_df_path = os.path.join(current_dir,  '..', 'ENUMA_DATA', 'enuma_users_df.csv')
    curriculum_indexes_path = os.path.join(current_dir,  '..', 'ENUMA_DATA_CURR', 'curr_indexes.csv')
    school_digital_indexes_path = os.path.join(current_dir,  '..', 'ENUMA_DATA_DIG', 'school_digital_learning_index.csv')
    user_digital_indexes_path = os.path.join(current_dir,  '..', 'ENUMA_DATA_DIG', 'user_digital_learning_index.csv')

    master_school_list = pd.read_csv(master_school_path)
    full_student_index_activity_log = pd.read_csv(full_student_index_activity_log_path)
    users_df = pd.read_csv(users_df_path)
    curriculum_indexes = pd.read_csv(curriculum_indexes_path)
    school_digital_indexes = pd.read_csv(school_digital_indexes_path)
    user_digital_indexes = pd.read_csv(user_digital_indexes_path)

    # we need to merge the master school list with the other data sets 
    master_school_list['School_Code_3'] = master_school_list['School_Id'].apply(lambda x:x[:3]).astype(int)

    # merge the full users with the master_school_list and only keep the division column 
    columns_to_keep = users_df.columns.tolist()
    columns_to_keep.append('Division')
    columns_to_keep
    users_df = users_df.merge(master_school_list, left_on = 'schoolUID', right_on='School_Code_3', how = 'left').loc[:, columns_to_keep]

    # merge the full student activity log with the users df to get the division
    full_student_index_activity_log_with_div = full_student_index_activity_log.merge(users_df, on = 'userId', how = 'left')

    # merge with the curriculum index
    # we will look at the num lessons attempted
    columns_to_keep = curriculum_indexes.columns.tolist()
    columns_to_keep.append('Division')
    curr_with_division = curriculum_indexes.merge(users_df, on = 'userId', how = 'left')
    columns_to_drop = [col for col in curr_with_division.columns if col.endswith('_y')]
    curr_with_division.drop(columns=columns_to_drop, inplace = True)
    p10_curr = curr_with_division['final_index'].quantile(0.25) * 100
    p90_curr = curr_with_division['final_index'].quantile(0.50) * 100

    # grab the curriculum final indexes
    curr_final_index_by_division = curr_with_division.groupby(by = 'Division').agg({'final_index':['median']}).reset_index()
    curr_final_index_by_division.columns = ['Division', 'median_final_index']
    curr_final_index_by_division['median_final_index'] = curr_final_index_by_division['median_final_index'] * 100
    curr_final_index_by_division['median_final_index'] = curr_final_index_by_division['median_final_index'].astype(int)

    # for the digital_user
    user_digital_indexes_with_div = user_digital_indexes.merge(users_df, on = ['userId', 'schoolName'], how = 'left')
    p10_dig = user_digital_indexes_with_div['DLI'].quantile(0.25) * 100
    p90_dig = user_digital_indexes_with_div['DLI'].quantile(0.50) * 100
    user_digital_indexes_with_div_by_division = user_digital_indexes_with_div.groupby(by = 'Division').agg({'DLI':'median'}).reset_index()
    user_digital_indexes_with_div_by_division.columns = ['Division','DLI']
    user_digital_indexes_with_div_by_division['DLI'] = user_digital_indexes_with_div_by_division['DLI'] * 100
    user_digital_indexes_with_div_by_division['DLI'] = user_digital_indexes_with_div_by_division['DLI'].astype(int)


    # pass the indexes to a dictionary
    curr_final_index_by_division_json = []
    for d, m in zip(curr_final_index_by_division["Division"], curr_final_index_by_division["median_final_index"]):
        if m > p90_curr:
            status = "Good"
        elif m < p10_curr:
            status = "Needs Attention"
        else:
            status = "Average"
        curr_final_index_by_division_json.append({
            "Division": d,
            "median_final_index": m,
            "status": status
        })

    # Add status to digital learning index JSON
    user_digital_indexes_with_div_by_div_json = []
    for d, dli in zip(user_digital_indexes_with_div_by_division["Division"], user_digital_indexes_with_div_by_division["DLI"]):
        if dli > p90_dig:
            status = "Good"
        elif dli < p10_dig:
            status = "Needs Attention"
        else:
            status = "Average"
        user_digital_indexes_with_div_by_div_json.append({
            "Division": d,
            "DLI": dli,
            "status": status
        })

    # now we parse these with json values 
    with open(os.path.join(current_dir, "..", "assets", "curr_final_index_by_division.json"), "w") as f:
        json.dump(curr_final_index_by_division_json, f, indent=2)

    with open(os.path.join(current_dir, "..", "assets", "user_digital_indexes_by_division.json"), "w") as f:
        json.dump(user_digital_indexes_with_div_by_div_json, f, indent=2)

    



grab_indexes()