#!/usr/bin/env python
import sys
import json
import os
import pandas as pd


user = os.environ.get('USER')
base_dir = "/home/{}/test_new-flamespray/".format(user) #replace with sys.argv
base_dir = sys.argv[1]
output_dir = os.path.join(base_dir, "Output")
particle_area_file = os.path.join(output_dir, "FSP-Lurederra_alumina-particle_area_flux.srp")
area_file_data = pd.read_csv(particle_area_file, skiprows=5, delim_whitespace=True)

particle_volume_file = os.path.join(output_dir, "FSP-Lurederra_alumina-particle_volume_flux.srp")  
volume_file_data = pd.read_csv(particle_volume_file, skiprows=5, delim_whitespace=True)

volume_flux = float(volume_file_data.columns[1])
area_flux = float(area_file_data.columns[1])
particle_size = 6.0 * 1e9 * volume_flux / area_flux

results = {
  "volume_flux": volume_flux,
  "area_flux": area_flux,
  "particle_size": particle_size
}

output_file = os.path.join(base_dir, 'results.json')
with open(output_file, 'w') as fh:
    json.dump(results, fh)
    fh.write("\n") # Need a newline at end of file

