import pandas as pd 
import numpy as np
import json
import os

# This file is to gather the data for the ENUMA metrics for the main part of the dashboard 
current_dir = os.path.dirname(__file__)

def grab_user_info():
    data_path = os.path.join(current_dir, '..', 'ENUMA_DATA', 'enuma_users_df.csv')
    data_path2 = os.path.join(current_dir, '..', 'ENUMA_DATA', 'inactive_schools_df_activity_log.csv')
    data_path3 = os.path.join(current_dir, '..', 'ENUMA_DATA', 'schools_not_in_activity_log.csv')
    data_path4 = os.path.join(current_dir, '..', 'ENUMA_DATA_CURR', 'combined_missing_schools_curr.csv')

    # total number of users tracked 
    enuma_users = pd.read_csv(data_path)

    # grab the inactive schools 
    inactive_schools = pd.read_csv(data_path2)
    inactive_schools = [school[0] for school in inactive_schools.values.tolist()]
    total_users = enuma_users['userId'].nunique()

    # schools not in activity log 
    schools_not_in_al = pd.read_csv(data_path3)
    schools_not_in_al = [school[0] for school in schools_not_in_al.values.tolist()]

    # schools not in curriculum log 
    schools_not_in_curr = pd.read_csv(data_path4)
    schools_not_in_curr = [school[0] for school in schools_not_in_curr.values.tolist()]

    # active users
    user_counts = enuma_users['activeStatus'].value_counts()

    # total number of active schools 
    active_schools = enuma_users.loc[enuma_users['activeStatus'] == True, ['schoolName']].nunique()
    
    # now we parse this to a json format 
    enuma_summary_metrics = {
        'num_inactive_schools':int(len(inactive_schools)),
        'inactive_schools' : inactive_schools,
        'total_users':int(total_users),
        'num_schools_not_in_al':int(len(schools_not_in_al)),
        'schools_not_in_all':schools_not_in_al,
        'num_schools_not_in_curr':int(len(schools_not_in_curr)),
        'schools_not_in_curr':schools_not_in_curr,
        'active_users':int(user_counts.get(True, 0)),
        'num_active_schools':int(active_schools.iloc[0]),
        'active_schools':int(active_schools.values[0]),
    }
    
    with open(os.path.join(current_dir, "..","assets", "enuma_summary_metrics.json"), "w+") as f:
        json.dump(enuma_summary_metrics, f, indent=2)



grab_user_info()