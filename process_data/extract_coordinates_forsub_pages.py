import python as pd 
import numpy as np
import os
import json
current_dir = os.path.dirname(__file__)

def grab_coords():
    # we first need to grab the master school list in order to merge with the division
    master_school_path = os.path.join(current_dir, '..', 'cleaned_TTWF_DATA', 'cleaned_master_school_list.csv')
    users_df_path = os.path.join(current_dir,  '..', 'ENUMA_DATA', 'enuma_users_df.csv')

    master_school_list = pd.read_csv(master_school_path)
    master_school_list['School_Code_3'] = master_school_list['School_Id'].apply(lambda x:x[:3]).astype(int)

    df_clean = master_school_list.replace(to_replace='missing', value=None).dropna(subset=["Division", "Loc_X_clean", "Loc_Y_clean"])
    # Group and build the structure
    division_coords = {}

    for division, group in df_clean.groupby("Division"):
        schools = []
        for _, row in group.iterrows():
            schools.append({
                "name": row["School_Name"],
                "school_id": row["School_Id"],
                "lat": float(row["Loc_Y_clean"]),
                "long": float(row["Loc_X_clean"])
            })
        division_coords[division] = schools

    # Save to assets
    output_path = os.path.join(current_dir, '..', 'assets', 'school_coords_by_division_for_subpage.json')
    with open(output_path, "w") as f:
        json.dump(division_coords, f, indent=2)

grab_coords()

def get_metrics_for_schools():
    pass