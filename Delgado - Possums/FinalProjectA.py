# Final project FINISHED AND WORKS
# Distribution of the Brush-tailed Possum in New South Wales, Australia

import arcpy
from arcpy import env
env.workspace = "G:\\Share\\GEOG6293_Programming\\DelgadoReveles\\Project\\FinalProject.gdb"


# STEP 1: Create a new layer using XY coordinates

# Set the spatial reference "NSW AGD_1966_Lambert_Conformal_Conic" (102004)
sr = arcpy.SpatialReference(102004)

# Make the XY event layer
arcpy.MakeXYEventLayer_management("AtlasXY_txt", "Longitude_GDA94", "Latitude_GDA94", "Possums_Event", sr, "")

# Copy features
arcpy.CopyFeatures_management("Possums_Event", "Possums_All", "", "0", "0", "0")

# Print total rows
featCount = arcpy.GetCount_management("Possums_All")
print "Possums file has %s rows" % featCount

print "XY points uploaded and a temporaly layer was created"


# STEP 2: Perform Select by Attribute in the new layer
# Set variables first
# whereClause = "DatasetName" + " = " + "'Dan Lunney's Community Wildlife Survey' and " + "NumberIndividuals" + " >= 1"
# whereClause = """DatasetName" = "Dan Lunney's Community Wildlife Survey" AND "NumberIndividuals" >= 1"""

# Make a Feature Layer to be used in the Selection by Attribute as this function only uses feature layers
arcpy.MakeFeatureLayer_management("Possums_All", "PossumsAllLyr")

# Use Select by Attributes to subse the data
arcpy.SelectLayerByAttribute_management("PossumsAllLyr", "NEW_SELECTION", "DatasetName" + " = " + "'Dan Lunney''s Community Wildlife Survey' and " + "NumberIndividuals" + " >= 1")

# Copy new feature class layer
arcpy.CopyFeatures_management("PossumsAllLyr", "Possums_Final", "", "0", "0", "0")

# Print total rows
featCount_2 = arcpy.GetCount_management("Possums_Final")
print "Possums Final has %s rows" % featCount_2

# Delete Feature Layer creater
arcpy.Delete_management("PossumsAllLyr")

print "Select by Attribute completed"


# STEP 3: Analysis of the distribution using Average Nearest Neighbor stat method

# Process ANN
nn_output = arcpy.AverageNearestNeighbor_stats("Possums_Final", "EUCLIDEAN_DISTANCE", "NO_REPORT", "#")

# Create a list of the ANN output values
print("The nearest neighbor index is: " + nn_output[0])
print("The z-score of the nearest neighbor index is: " + nn_output[1])
print("The p-value of the nearest neighbor index is: " + nn_output[2])
print("The expected mean distance is: " + nn_output[3])
print("The observed mean distance is: " + nn_output[4])


print "Script completed"
