#%%
# Final Project
# create a new geodatabase to hold project data

# try running the GDB_Import first because I believe that will also create a new
# geodatabase from my chosen import files

### depending on how I combine scripts may ormay not need next block

import arcpy
from arcpy import env

# set my workspace
arcpy.env.workspace = "G:/Share/GEOG6293_Programming/Alles/Final"

# set local variables
out_folder_path = "G:/Share/GEOG6293_Programming/Alles/Final"
out_name = "spotted_owl.gdb"

# Execute CreateFileGeodatabase
arcpy.CreateFileGDB_management(out_folder_path, out_name)

########

#%%

