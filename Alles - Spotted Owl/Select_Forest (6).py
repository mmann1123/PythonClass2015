#%%
# Final Project Select by Attribute
#
# Want to isolate any forest landcover types (there are 4) from the larger landcover shapefile


# original file name:nlcd_or_20111
# 17 landcover types, 4 of which are forest types
#

# import system modules-- conversion is within arcpy
import arcpy
from arcpy import env
import os

# set my workspace
arcpy.env.workspace = "G:/Share/GEOG6293_Programming/Alles/Final/spotted_owl.gdb"

arcpy.MakeFeatureLayer_management("G:/Share/GEOG6293_Programming/Alles/Final/spotted_owl.gdb/cover.shp", "coverlyr")
arcpy.SelectLayerByAttribute_management("coverlyr", "NEW_SELECTION", " [nlcd_or_20111.vat:LAND_COVER] = 'Deciduous Forest' OR [nlcd_or_20111.vat:LAND_COVER] = 'Evergreen Forest' OR [nlcd_or_20111.vat:LAND_COVER] = 'Mixed Forest' OR [nlcd_or_20111.vat:LAND_COVER] = 'Woody Wetlands' ")

#
# Next, create new layer from selection

arcpy.MakeFeatureLayer_management("forest.shp", "forest")


