import yaml
import json
import os
import pandas as pd 
################################################ Goal ################################################
# This file will be dedicated to scrapping data to feed into the map on the home page

current_dir = os.path.dirname(__file__)

data_path = os.path.join(current_dir, "..", "assets", "district_coords.yml")

def parse_coords_to_json():
# Load the YAML
    with open(data_path, "r") as f:
        data = yaml.safe_load(f)

# Save as JSON
    with open("assets/district_coords.json", "w") as f:
        json.dump(data["district"], f, indent=2)

parse_coords_to_json()


def grab_division_information():
    data_path =  os.path.join(current_dir, "..", "cleaned_TTWF_DATA", "cleaned_master_school_list.csv")
    master_school_list = pd.read_csv(data_path)

    # we first need all the unique names for the district 
    divsion_names = master_school_list['Division'].unique()

    # grabs the total school counts
    total_school_counts = master_school_list.groupby(by = 'Division').count()['School_Id'].reset_index()

    # get the actual school distributions
    school_distribution = master_school_list.groupby(by = ['Division', 'Status']).count()['School_Id'].reset_index()

    # we need to also get the number of microschools vers in
    school_type_count = master_school_list.groupby(by = ['Division', 'Type']).count()['School_Id'].reset_index()

    # we need the total number of active students as well
    data_path =  os.path.join(current_dir, "..", "cleaned_TTWF_DATA", "cleaned_learner_profile.csv")
    learner_profile = pd.read_csv(data_path)
    # and we need the avaergae monthly attendance as well
    # grab only the active kids
    active_students = learner_profile.loc[learner_profile['Status_cleaned'] != 'Active', :]
  
    # we need to cllean some columns 
    active_students['School_Code'] = active_students['School_Code'].replace(to_replace='missing', value = '0').astype(float)
    master_school_list['School_Code_3'] = master_school_list['School_Id'].apply(lambda x:x[:3]).astype(float)

    # now we can merge on this data
    temp = active_students.merge(master_school_list, how = 'left', left_on='School_Code', right_on='School_Code_3')
    
    student_counts_by_division =  temp.groupby(by=['Division']).count()['Name']

    division_info = {}

    # Safely get all unique divisions
    all_divisions = master_school_list['Division'].dropna().unique()

    for division in all_divisions:
        division_info[division] = {
            "total_schools": int(total_school_counts.loc[total_school_counts['Division'] == division, 'School_Id'].values[0])
                             if not total_school_counts.loc[total_school_counts['Division'] == division].empty else 0,

            "status_counts": {
                row['Status']: int(row['School_Id'])
                for _, row in school_distribution[school_distribution['Division'] == division].iterrows()
            },

            "type_counts": {
                row['Type']: int(row['School_Id'])
                for _, row in school_type_count[school_type_count['Division'] == division].iterrows()
            },

            "active_student_count": int(student_counts_by_division.get(division, 0))
        }

    # Write to JSON file
    json_output_path = os.path.join(current_dir, "..", "assets", "division_info_map_main.json")
    with open(json_output_path, "w") as f:
        json.dump(division_info, f, indent=2)

    print(f"Division info written to {json_output_path}")


    # attendance
    # GRAB MONTHLY ATTENDANCE FOR TOMORROW 

    # print(student_counts_by_division)

grab_division_information()

''''
Model village
Type: MicroSchool

District: Mirpurkhas

Status: Active

Enrollment: 36 students

Attendance: 79%

Teachers: 3

Launch Date: Unknown
'''