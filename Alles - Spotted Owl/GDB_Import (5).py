#%%
# Final Project
# import base data files to project geodatabase

### depending on how I combine scripts may or may not need next block

import arcpy
from arcpy import env

# set my workspace
arcpy.env.workspace = "G:/Share/GEOG6293_Programming/Alles/Final\\spotted_owl.gdb"

# designate layers to import to geodatabase
# base layers are: old growth forests, owl point locations, landcover layer, and Oregon polygon layer
arcpy.FeatureClassToGeodatabase_conversion(['old_growth.shp', 'owl_point.shp', 'Oregon.shp', 'cover.shp'], 'G:/Share/GEOG6293_Programming/Alles/Final\\spotted_owl.gdb')

###############
#%%
