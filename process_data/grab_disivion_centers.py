import os 
import json
import numpy as np
# this will grab all the centers for the divisions for the map in the subpages 


with open(os.path.join("assets", "school_coords_by_division_for_subpage.json"), 'r') as f:
    data = json.load(f)

# this will be the dict we populate 
division_centers = {}

for d in data:
    # now we have a list of all the schools
    lats = []
    longs = [] 
    for school in data[d]:
        # append them to the lists 
        lats.append(school['lat'])
        longs.append(school['long'])
    
    # now we can find the mean 
    mean_lats = np.mean(lats)
    mean_long = np.mean(longs)

    division_centers[d] = (float(mean_lats), float(mean_long))


# now we can write this to json 
with open(os.path.join("assets", "division_centers_for_subpages.json"), "w+") as f:
    json.dump(division_centers, f)


