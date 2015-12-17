# Final project "WORK IN PROGRESS" (this script doesn't all work yet)
# Average Nearest Neighbor, Getis-Ord, Multi_Distance and regression of an iconic species in NSW

import arcpy
from arcpy import env
import os
# Remove: env.workspace = "G:\\Share\\GEOG6293_Programming\\DelgadoReveles\\Project\\FinalProject.gdb"

arcpy.env.overwriteOutput = True

# Obtain script parameters: Workspace, MakeXY Layer, 
env.workspace = arcpy.GetParameterAsText(0)



# STEP 1: Create a new layer using XY coordinates

# Set local variables to Make XY event Layer
# Sintax: MakeXYEventLayer_management(table, in_x_field, in_y_field, out_layer, {spatial_reference}, {in_z_field})
in_Table = arcpy.GetParameterAsText(1)
x_field = arcpy.GetPatameterAsText(2)
y_field = arcpy.GetParameterAsText(3)
z_field = arcpy.GetParameterAsText(4)
EventLayerName = arcpy.GetParameterAsText(5)

# Set the spatial reference "NSW AGD_1966_Lambert_Conformal_Conic" (102004)
sr = arcpy.SpatialReference(102004)

# Make the XY event layer
arcpy.MakeXYEventLayer_management(in_Table, x_field, y_field, EventLayer, sr, z_field)

# Set local variables to Copy Features of the XY event layer
# CopyFeatures_management(in_features, out_features_class, {config_keyword}, {spatial_grid_1}, {spatial_grid_2}, {spatial_grid_3})
output_feaName = arcpy.GetParameterAsText(6)

# Copy features
arcpy.CopyFeatures_management(EventLayer, output_feaName, "", "0", "0", "0")

# Print total rows
featCount = arcpy.GetCount_management(output_feaName)
print "Possums file has %s rows" % featCount

print "XY points uploaded and a temporaly layer was created"
    



# STEP 2: Perform Select by Attribute in the new layer

# Set local variable
output_final = arcpy.GetParametersAsText(7)

# Make a Feature Layer to be used in the Selection by Attribute as this function only uses feature layers
arcpy.MakeFeatureLayer_management(output_feaName, "AllTempLyr")

# Set SQL Expression
whereClause = arcpy.GetParameterAsText(7)

# Use Select by Attributes to subse the data
arcpy.SelectLayerByAttribute_management("AllTempLyr", "NEW_SELECTION", whereClause)

# Copy new feature class layer
arcpy.CopyFeatures_management("AllTempLyr", output_final, "", "0", "0", "0")

# Print total rows
featCount_2 = arcpy.GetCount_management(output_final)
print "Possums Final has %s rows" % featCount_2

# Delete Feature Layer creater
arcpy.Delete_management("AllTempLyr")

print "Select by Attribute completed"



# STEP 3: Analysis of the distribution using Average Nearest Neighbor stat method

# Process ANN
nn_output = arcpy.AverageNearestNeighbor_stats(output_final, "EUCLIDEAN_DISTANCE", "NO_REPORT", "#")

# Create a list of the ANN output values
print("The nearest neighbor index is: " + nn_output[0])
print("The z-score of the nearest neighbor index is: " + nn_output[1])
print("The p-value of the nearest neighbor index is: " + nn_output[2])
print("The expected mean distance is: " + nn_output[3])
print("The observed mean distance is: " + nn_output[4])

print "Average Nearest Neighbor completed"



# STEP 4: Perform Getis_ord method

# Sintax: HotSpots_stats(Input_Feature_Class, Input_Field, Output_Feature_Class,
# Conceptualization_of_Spatial_Relationships, Distance_Method, Standardization. {Distance_Band_or_Threshold_Distance},
# {Self_Potential_Field}, {Weight_Matrix_File}, {Apply_False_Discovery_Rate_FDR_Correction})

# Set the variables (from user)
NumIn_Field = arcpy.GetParameterAsText(8)
output_G = arcpy.GetParameterAsText(9)

# Process Getis -Ord
arcpy.HotSpots_stats(output_final, NumIn_Field, output_G, "INVERSE_DISTANCE", "EUCLIDEAN_DISTANCE", "NONE", "#", "#", "", "NO_FDR")

# Get the results
result_G = arcpy.HotSpots_starts()
print result_G.summary()

print "Getis-Ord method completed"



# STEP 5: Multi_Distance Spatial Cluster

# Sintax: MultiDistanceSpatialClustering_stats (Input_Feature_Class, Output_Table, Number_of_Distance_Bands,
# {Compute_Confidence_Envelope}, {Display_Results_Graphically}, {Weight_Field}, {Beginning_Distance},
# {Distance_Increment}, {Boundary_Correction_Method}, {Study_Area_Method}, {Study_Area_Feature_Class})

# Set variables (from user)
output_MD = arcpy.GetParameterAsText(9)
Number_DistBand = arcpy.GetParameterAsText(10)
Beg_Dist = arcpy.GetParameterAsText(11)
Dist_Incr = arcpy.GetParameterAsText(12)

# Perform Multi-Distance method
arcpy.MultiDistanceSpatialClustering_stats(output_final, output_MD, Number_DistBand, "0_PERMUTATIONS_-_NO_CONFIDENCE_ENVELOPE", "NO_REPORT", "#", Beg_Dist, Dist_Incr, "NONE", "", "")

# Get Results
result_MD = arcpy.MultiDistanceSpatialClustering_stats()
print result_MD.summary
                                          
print "Multi-Distance Spatial Cluster method completed"



# STEP 6: Regression (I do not have the Dependent and Independent variables

# Sintax: ExploratoryRegression_stats (Input_Features, Dependent_Variable, Candidate_Explanatory_Variables,
# {Weights_Matrix_File}, {Output_Report_File}, {Output_Results_Table}, {Maximum_Number_of_Explanatory_Variables},
# {Minimum_Number_of_Explanatory_Variables}, {Minimum_Acceptable_Adj_R_Squared}, {Maximum_Coefficient_p_value_Cutoff},
# {Maximum_VIF_Value_Cutoff}, {Minimum_Acceptable_Jarque_Bera_p_value}, {Minimum_Acceptable_Spatial_Autocorrelation_p_value})

# Set variables (from user)

# Perform Regression

# Get results

print "Script completed"
