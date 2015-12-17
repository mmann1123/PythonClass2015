#%%
# Final Project Gi* Analysis
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
arcpy.env.workspace = "G:/Share/GEOG6293_Programming/Alles/Final/spotted_owl.gdb"

# Determine hotspots based on number of owls located at each point location
arcpy.HotSpots_stats("owl_point.shp", "Total", "OwlHotSpots.shp", "INVERSE_DISTANCE", "EUCLIDEAN_DISTANCE", "NONE","#", "#", "#","#")

#%%
