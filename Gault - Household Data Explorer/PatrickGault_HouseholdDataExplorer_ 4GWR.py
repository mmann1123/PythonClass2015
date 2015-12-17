# ------------------------------------------------------------------ #
# Name: Household Data Explorer | Part 4 of 4: Geographically Weighted Regression (GWR)
# Purpose: The purpose of this script is to: 1) Conduct GWR are on previously specified model(s); 2) Isolate the areas in the output coefficient surfaces that are significant.
# Author: Patrick Gault
# Created: 2015/11
# License: MIT License
# Requirements: ArcGIS Desktop 10.x, Geostatistical Analyst
# ------------------------------------------------------------------ #

print "Starting Part 4 of 4: Geographically Weighted Regression..."

# ---- STEP 1: IMPORT ARCPY, SET ENVIRONMENTS, WORKSPACE---- #
# Import ArcPy, os, and shutil site packages
import arcpy
import os
import shutil

# Set prefix for filenames 
filePrefix = "BGD_" # This should be the 3 letter ISO 3116 code.  For reference, see: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3

# Checkout Geostatistical and Spatial Analyst Extensions
arcpy.CheckOutExtension("GeoStats")
arcpy.CheckOutExtension("Spatial")

# Create new folder as the workspace to store output report documents and overwrite it if it already exists
path = r'G:\\Share\\GEOG6293_Programming\\Data\\Gault\\FinalProject\\Data' # Add the path to the folder where you're storing the GDB.
folderName = filePrefix + "GWR"

if os.path.exists(path + "\\" + folderName):
    shutil.rmtree(path + "\\" + folderName)
os.makedirs(path + "\\" + folderName)

# Set workspace to new folder and add overwrite permissions
arcpy.env.workspace = path + "\\" + folderName
arcpy.env.overwriteOutput = True

# Set the GDB path in order to call data from the GDB
fileGDB = r'G:\\Share\\GEOG6293_Programming\\Data\\Gault\\FinalProject\\Data\\BGD_LAM.gdb' #  Add the filepath of the workspace File GDB

# *** Set Spatial Reference using WKID (http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Projected_coordinate_systems/02r3000000vt000000/)
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3106)

# Set Raster Mask
arcpy.env.mask = fileGDB + "\\" + filePrefix + "Adm0"


# ---- STEP 2: GWR ANALYSIS FOR SEVERAL DEPENDENT VARIABLES ---- #
# *** Requires User Input

# Set Global Variables
in_features = fileGDB + "\\" + filePrefix + "hhPoints" # This is the household points dataset
distance = ""
number_of_neighbors = ""
weight_field = ""
cell_size = ""
in_prediction_locations = ""
prediction_explanatory_field = ""
out_prediction_featureclass = ""

# MODEL 1: Set Local Variables for 
dependent_field = "dietDiv" # This is the field name for the dependent variable
explanatory_field = ["agshkR", "FCS"] # These are the field names for the independent variables
kernel_type = "ADAPTIVE"
bandwidth_method = "AICc"

print "\t Starting GWR..."
# MODEL 1: Create a new folder to store the GWR Output and overwrite it if it already exists
gwrPath = path + "\\" + folderName  # Add the path to the folder where you're storing the GDB.
gwrFolderName = filePrefix + "GWR_" + dependent_field  # This is a new folder name that will be named with the dependent varibale field name
print "\n\t\t 1 of 10: Creating a new folder for the %s GWR output..." % dependent_field
if os.path.exists(gwrPath + "\\" + gwrFolderName):
    shutil.rmtree(gwrPath + "\\" + gwrFolderName)
os.makedirs(gwrPath + "\\" + gwrFolderName) # This creates the output folder
print "\t\t\t Complete: Finished creating the folder for the %s GWR output..." % dependent_field

# MODEL 1: Set the output location and name based on the new folder that was created above.
out_featureclass = gwrPath + "\\" + gwrFolderName + "\\" + filePrefix + "GWR_" + dependent_field # This is the name of the output point feature class from the GWR 
coefficient_raster_workspace = gwrPath + "\\" + gwrFolderName # This is the location for the GWR output raster surfaces, there will be 1 for each independent variable and they will take the independent variable name.

# MODEL 1: Execute GWR
print "\n\t\t 2 of 10: Executing GWR for %s..." % dependent_field
arcpy.GeographicallyWeightedRegression_stats(in_features, dependent_field, explanatory_field, out_featureclass,
                                             kernel_type, bandwidth_method, distance, number_of_neighbors, weight_field,
                                             coefficient_raster_workspace, cell_size, in_prediction_locations,
                                             prediction_explanatory_field, out_prediction_featureclass)
print "\t\t\t Complete: Finished GWR for %s..." % dependent_field


# MODEL 1 - Coef 1: Add new field for t-stat, calculat t-stat, make feature layer where t-stat is above 90% confidence level, buffer significant points, clip GWR output coefficient surface to significant area
# I'm using 90% CL for this subset of data that is testing the script and the test model specifications because its hard to pick up significant hh points otherwise. We'll use 95% CL when its game time.

# I tried to be more sophisticated but couldn't enter these into my SQL expressions below.  I want to figure out if there's a way to loop over the below, it would really reduce the lines of code.
# coef1 = [f.name for f in arcpy.ListFields(out_featureclass + ".shp","C1_*",'')]
# coef1_2 = coef1[0]
# coef1SE = [f.name for f in arcpy.ListFields(out_featureclass + ".shp","StdErrC1_*",'')]
# coef1SE_2 = coef1SE[0]

# Add new field for the t-stat for the first coefficient and calculate the t-stat
print "\n\t\t 3 of 10: Adding new fields for t-stats for the %s coefficient..." % (explanatory_field[0])
arcpy.AddField_management(out_featureclass + ".shp", "C1_tStat", "FLOAT")

print "\t\t\t Calculating the t-stats for the %s coefficient..." % explanatory_field[0]
arcpy.CalculateField_management(out_featureclass + ".shp", "C1_tStat","""!C1_agshkR! / !StdErrC1_a!""", "PYTHON_9.3")
print "\t\t\t\t Complete: Finished calculating the t-stats for the %s coefficient..." % (explanatory_field[0])

# Isolate household points that are significant at the 90% level for the first independent variable
print "\n\t\t 4 of 10: Isolating the houshehold points where t-stats are significant for the %s coefficient..." % (explanatory_field[0])
arcpy.MakeFeatureLayer_management(out_featureclass + ".shp", "coefPoints")
arcpy.SelectLayerByAttribute_management("coefPoints", "NEW_SELECTION", """"C1_tStat" >= 1.645 OR "C1_tStat" <= -1.645""")
print "\t\t\t Complete: Finished isolating houshehold points where t-stats are significant for the %s coefficient..." % (explanatory_field[0])


# Buffer the Household Points that are significant at the 90% level for the first independent variable using the same buffer distance as before
print "\n\t\t 5 of 10: Buffering the hh points for the %s coefficient surface..." % (explanatory_field[0])
# Set local buffer variables and execute buffer
bufferInput = "coefPoints" #  This is the subsetted part of the feature layer created above representing coefficients that are significant at the 90% confidence level
bufferDistance = "25 Kilometers" # This parameter should be selected based on testing different buffer distances and determining which distance creates the most contiguous surface without leaving isolated households.
bufferOutput = "in_memory\coefPoints_Buffer"
dissolveType = "All"

arcpy.Buffer_analysis(bufferInput, bufferOutput, bufferDistance, "", "", dissolveType, "")
print "\t\t\t Complete: The hh points for the %s coefficient surface have been buffered!" % (explanatory_field[0])

# Clip the output raster for coef 1 to the buffer
print "\n\t\t 6 of 10: Clipping the hh points for the %s coefficient surface..." % (explanatory_field[0])
# Set local clip variables and execute clip
in_raster = gwrPath + "\\" + gwrFolderName + "\\" + explanatory_field[0]
out_raster = fileGDB + "\\" + filePrefix + "GWR_" + explanatory_field[0] + "_90"
in_template_dataset = "in_memory\coefPoints_Buffer"
clipping_geometry = "ClippingGeometry"

arcpy.Clip_management(in_raster, "", out_raster, in_template_dataset, "", clipping_geometry)
print "\t\t\t Complete: The hh points have been clipped!"


# MODEL 1 - Coef 2: Add new field for t-stat, calculat t-stat, make feature layer where t-stat is above 90% confidence level, buffer significant points, clip GWR output coefficient surface to significant area
# Add new field for the t-stat for the first coefficient and calculate the t-stat
print "\n\t\t 7 of 10: Adding new fields for t-stats for the %s coefficient..." % (explanatory_field[1])
arcpy.AddField_management(out_featureclass + ".shp", "C2_tStat", "FLOAT")

print "\t\t\t Calculating the t-stats for the %s coefficient..." % (explanatory_field[1])
arcpy.CalculateField_management(out_featureclass + ".shp", "C2_tStat","""!C2_fcs! / !StdErrC2_f!""", "PYTHON_9.3")
print "\t\t\t\t Complete: Finished calculating the t-stats for the %s coefficient..." % (explanatory_field[1])

# Isolate household points that are significant at the 90% level for the first independent variable
print "\n\t\t 8 of 10: Isolating the houshehold points where t-stats are significant for the %s coefficient..." % (explanatory_field[1])
arcpy.MakeFeatureLayer_management(out_featureclass + ".shp", "coefPoints")
arcpy.SelectLayerByAttribute_management("coefPoints", "NEW_SELECTION", """"C1_tStat" >= 1.645 OR "C1_tStat" <= -1.645""")
print "\t\t\t Complete: Finished isolating houshehold points where t-stats are significant for the %s coefficient..." % (explanatory_field[1])

# Buffer the Household Points that are significant at the 90% level for the first independent variable using the same buffer distance as before
print "\n\t\t 9 of 10: Buffering the hh points for the %s coefficient surface..." % (explanatory_field[1])
# Set local buffer variables and execute buffer
bufferInput = "coefPoints" #  This is the subsetted part of the feature layer created above representing coefficients that are significant at the 90% confidence level
bufferDistance = "25 Kilometers" # This parameter should be selected based on testing different buffer distances and determining which distance creates the most contiguous surface without leaving isolated households.
bufferOutput = "in_memory\coefPoints_Buffer"
dissolveType = "All"

arcpy.Buffer_analysis(bufferInput, bufferOutput, bufferDistance, "", "", dissolveType, "")
print "\t\t\t Complete: The hh points for the %s coefficient surface have been buffered!" % (explanatory_field[1])

# Clip the output raster for coef 2 to the buffer
print "\n\t\t 10 of 10: Clipping the hh points for the %s coefficient surface..." % (explanatory_field[1])
# Set local clip variables and execute clip
in_raster = gwrPath + "\\" + gwrFolderName + "\\" + (explanatory_field[1])
out_raster = fileGDB + "\\" + filePrefix + "GWR_" + explanatory_field[1] + "_90"
in_template_dataset = "in_memory\coefPoints_Buffer"
clipping_geometry = "ClippingGeometry"

arcpy.Clip_management(in_raster, "", out_raster, in_template_dataset, "", clipping_geometry)
print "\t\t Complete: The hh points have been clipped!"

print "Part 4 of 4: Geographically Weighted Regression is complete!"