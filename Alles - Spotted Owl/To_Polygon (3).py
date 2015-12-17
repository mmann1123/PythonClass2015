#%%
# Final Project Create Polygon
#
# State Land Cover data is in raster format so the following code converts to 
# polygon so that it can be worked with all the other data

# Need to check the correct input field
# original file name:nlcd_or_20111
# 17 landcover types
#
#

# import system modules-- conversion is within arcpy
import arcpy
from arcpy import env
import os

# set my workspace
arcpy.env.workspace = "G:/Share/GEOG6293_Programming/Alles/Final/OR_NLCD_2011"

# I am choosing not to simplify to have the data be the exact cover as the original raster file--just seems like the more
# accurate way to convert in this case


# Identifying the 'Value' field as identifier for future table join--tomaintain land cover labels

inRaster = "nlcd_or_20111"
outPolygons = "G:/Share/GEOG6293_Programming/Alles/Final/spotted_owl.gdb/cover.shp"
field = VALUE

arcpy.RasterToPolygon_conversion("nlcd_or_20111", "G:/Share/GEOG6293_Programming/Alles/Final/spotted_owl.gdb/cover.shp", "NO_SIMPLIFY", "VALUE")

