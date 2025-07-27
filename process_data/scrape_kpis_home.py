import pandas as pd 
import numpy as np
import json
import os

########################################### OBJECTIVE ##########################################################
'''
This file is dedicated to extracting the main singleton values on the main dashboard
'''
################################################################################################################
# first set the base directory 
current_dir = os.path.dirname(__file__)


def grab_school_info():
    '''
        This will read in the master school list to get information about inactive schools, active schools
    '''

    # first read in the data
    # grab the directory first 
    data_path = os.path.join(current_dir, "..", "cleaned_TTWF_DATA", "cleaned_master_school_list.csv")
 
    master_school_list = pd.read_csv(data_path)

    # grab the value counts for status 
    school_counts = master_school_list['Status'].value_counts()

    # grab the counts and the school names and schoolId for the missing and closed schools 
    num_operational_schools =  school_counts.get('Active', 0)
    num_closed_schools = school_counts.get('Closed', 0)
    num_missing_status_schools = school_counts.get('missing', 0)
    num_total_historical_school = len(master_school_list)
    # we put these results in a json
    school_counts_data = {
        'num_operational_schools': int(num_operational_schools),
        'num_closed_schools': int(num_closed_schools),
        'num_missing_status_schools': int(num_missing_status_schools),
        'num_total_historical_school': int(num_total_historical_school)
    }

    # we store this as a json 
    with open(os.path.join(current_dir, "..","assets", "school_counts_data.json"), "w+") as f:
        json.dump(school_counts_data, f)

    # now actually grab the schools with missing status and the ones that were closed 
    closed_schools = master_school_list.loc[master_school_list['Status'] == 'Closed', ['School_Id', 'School_Name']]
    missing_schools = master_school_list.loc[master_school_list['Status'] == 'missing', ['School_Id', 'School_Name']]

    # convert into json 
    closed_json = closed_schools.to_dict(orient="records")
    missing_json = missing_schools.to_dict(orient="records")

    # Save closed schools
    with open(os.path.join(current_dir, ".." ,"assets", "closed_schools.json"), "w+") as f:
        json.dump(closed_json, f, indent=2)

    # Save missing schools
    with open(os.path.join(current_dir, "..","assets", "missing_schools.json"), "w+") as f:
        json.dump(missing_json, f, indent=2)

    # now grab the districts covered and the divisions 
    # Create dictionary
    coverage_summary = {
        "districts_covered": sorted(master_school_list['District'].dropna().unique().tolist()),
        "num_districts": int(master_school_list['District'].nunique()),
        "divisions_covered": sorted(master_school_list['Division'].dropna().unique().tolist()),
        "num_divisions": int(master_school_list['Division'].nunique())
    }

    # Save to JSON
    with open(os.path.join(current_dir, "..","assets", "school_coverage.json"), "w+") as f:
        json.dump(coverage_summary, f, indent=2)


def grab_students_enrolled():
    # this function is used to grab the total number of students enrolled and the total dropout rate from the learner profole
    data_path = os.path.join(current_dir, "..", "cleaned_TTWF_DATA", "cleaned_learner_profile.csv")

    learner_profile = pd.read_csv(data_path, low_memory=False)

    status_counts = learner_profile['Status_cleaned'].value_counts()

    total_students = len(learner_profile)
    dropout_students = status_counts.get('Dropout', 0)
    active_students = total_students - dropout_students
    dropout_rate = dropout_students / total_students

    student_info = {'total_students':int(total_students), 'active_students':int(active_students), 'dropout_rate':int(dropout_rate * 100)}

    with open(os.path.join(current_dir, "..","assets", "student_main_ttwf_dist.json"), "w+") as f:
        json.dump(student_info, f, indent=2)

def grab_attendace_metrics():
    # this will be used to grab the average attendance we will use the historical, monthly, and past week
    data_path = os.path.join(current_dir, "..", "cleaned_TTWF_DATA", "cleaned_attendance.csv")

    attendance = pd.read_csv(data_path)
    attendance_all = int(
        attendance['Attendance_Percent_all'].replace(to_replace='No data', value = None).astype(float).dropna().mean()
    )
    attendance_month = int(
        attendance['Attendance_Percent_month'].replace(to_replace='No data', value = None).astype(float).dropna().mean()
    )
    attendance_week = int(
        attendance['Attendance_Percent_week'].replace(to_replace='No data', value = None).astype(float).dropna().mean()
    )
    
    attendance_data = {'historical':attendance_all, 'past_month':attendance_month, 'past_week':attendance_week}

    with open(os.path.join(current_dir, "..","assets", "attendance_main.json"), "w+") as f:
        json.dump(attendance_data, f, indent=2)


grab_school_info()
grab_students_enrolled()

grab_attendace_metrics()

