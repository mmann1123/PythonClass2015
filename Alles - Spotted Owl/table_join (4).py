#%%
# Final Project Join Table
#
# After converting raster land cover file to polygon, the table join will associate the
# GRIDCODE given to the corresponding land cover type so that forest types can be selected


# original file name:nlcd_or_20111
# 17 landcover types
# each landcover type had a corresponding 'value' in raster attribute table
#

# import system modules-- conversion is within arcpy
import arcpy
from arcpy import env
import os

# set my workspace
arcpy.env.workspace = "G:/Share/GEOG6293_Programming/Alles/Final/spotted_owl.gdb"

arcpy.JoinField_management("cover", "GRIDCODE", "VALUE")

