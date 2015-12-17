#%%
# Final Project 
# Kernel Old Growth Forest
# looking at kernel density within old growth polygons containing spotted owl sightings
# 
#

# import system modules-- conversion is within arcpy
import arcpy
from arcpy import env
# Spatial Analyst needs to be cited to import Kernel tool
from arcpy.sa import *

# set my workspace
arcpy.env.workspace = "G:/Share/GEOG6293_Programming/Alles/Final/spotted_owl.gdb"

# Add Spatial Analyst Extension

if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.AddMessage("Checking out Spatial")
    arcpy.CheckOutExtension("Spatial")
else:
    arcpy.AddError("Unable to get spatial analyst extension")
    arcpy.AddMessage(arcpy.GetMessages(0))
    sys.exit(0)

arcpy.CheckInExtension("Spatial")   

# set extent to previously created intersect layer from old growth
# will only output within old growth instead of a default size
arcpy.env.extent = "og_intersect"

# run Kernel between old growth and locations
outKDens = KernelDensity("owl_point.shp", "NONE")
outKDens.save("G:/Share/GEOG6293_Programming/Alles/Final/spotted_owl.gdb/og_kdens")

###############
#%%