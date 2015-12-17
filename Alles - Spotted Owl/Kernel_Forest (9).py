#%%
# Final Project 
# Kernel All Forest
# looking at kernel density within forest polygons containing spotted owl sightings
# 
#

# import system modules-- conversion is within arcpy
import arcpy
from arcpy import env
# Spatial Analyst needs to be cited to import Kernel tool
from arcpy.sa import *

# Add Spatial Analyst Extension

if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.AddMessage("Checking out Spatial")
    arcpy.CheckOutExtension("Spatial")
else:
    arcpy.AddError("Unable to get spatial analyst extension")
    arcpy.AddMessage(arcpy.GetMessages(0))
    sys.exit(0)

arcpy.CheckInExtension("Spatial")   
 
# set my workspace
arcpy.env.workspace = "G:/Share/GEOG6293_Programming/Alles/Final/spotted_owl.gdb"

# set extent to previously created intersect layer from old growth
# will only output within forest instead of a default size
arcpy.env.extent = "forest"

# run Kernel between general forest and locations
outKDens = KernelDensity("owl_point.shp", "NONE")
outKDens.save("G:/Share/GEOG6293_Programming/Alles/Final/spotted_owl.gdb/for_kdens")



###############
#%%