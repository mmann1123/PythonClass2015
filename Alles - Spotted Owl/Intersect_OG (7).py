#%%
# Final Project Intersect Old Growth
#
# Intersect between Old Growth Forest Land Cover types and spotted owl point locations
# then we create a new layer from the selected polygons
# 
#

# import system modules-- conversion is within arcpy
import arcpy
from arcpy import env
import os

# set my workspace
arcpy.env.workspace = "G:/Share/GEOG6293_Programming/Alles/Final"


# Will be selecting old growth forest polygons that contain Spotted Owl locations

arcpy.SelectLayerByLocation_management("land_cover", "INTERSECT", "G:/Share/GEOG6293_Programming/Alles/Final/spotted_owl.gdb/owl_point", "0", "NEW_SELECTION")

# Next, create new layer from selection

arcpy.MakeFeatureLayer_management("old_growth.shp", "og_intersect")

###########

#%%

