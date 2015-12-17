# The purpose of this code is to 1) add city points 2) manipulate precipitation, population
# temperature, heating degree days and cooling degree days data and assign valeus in order to
# get a overall harshness index (Nordicity Value) 3) import data and display data in arcmap
# in a way that displays the gradual change in harshness across space in Alaska

# *****NOTE: ONCE THE CODE HAS RUN THE FINAL MAP AND DATA LAYERS ARE IN 
# "G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file\\Nordicity2.mxd"

import pandas as pd
import arcpy

# setting overwrite power to save a lot of time, energy and confusion
arcpy.env.overwriteOutput = 1

# Read in Population.csv and call in Alaska.pop
pop = pd.read_csv('G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file\\Population.csv')
# sort Alaska_pop by ascending order
Alaska_pop = pop.sort('Population', ascending = False)
# create a list of values to populate a new column. These will be added for each Nordicity parameter to create a Nordicity value for each location
Nord_value = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42','43','44','45','46','47','48','49','50','51','52','53','54','55','56','57']
Alaska_pop['pop_Nord_value'] = Nord_value
# creating a new csv file out of the new data with the new column
Alaska_pop.to_csv("Alaska_pop.csv")
arcpy.CopyRows_management ("G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file\\Alaska_pop.csv", "G:\\Share\\GEOG6293_Programming\\Melvin\\Nord.gdb\\Alaska_pop")

# importing annual precipitation and sorting in ascending order. And creating a new column to input Nordicity values
precip = pd.read_csv('G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file\\Annual_precip.csv')
# sorted ascending because higher annual precipt i.e snowfall means harsher conditions
Alaska_precip = precip.sort('Precipitation', ascending = True)
Alaska_precip['precip_Nord_value'] = Nord_value
# creating a new csv file out of the new data with the new column
Alaska_precip.to_csv("Alaska_precip.csv")
arcpy.CopyRows_management ("G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file\\Alaska_precip.csv", "G:\\Share\\GEOG6293_Programming\\Melvin\\Nord.gdb\\Alaska_precip")

# importing annual temperature and sorting and creating a new column to input Nordicity values
temp = pd.read_csv('G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file\\Annual_temp.csv')
#sorted descending because lower annual temp needs a higher more intense Nordicity value
Alaska_temp = temp.sort('Temperature', ascending = False)
Alaska_temp['temp_Nord_value'] = Nord_value
# creating a new csv file out of the new data with the new column
Alaska_temp.to_csv("Alaska_temp.csv")
arcpy.CopyRows_management ("G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file\\Alaska_temp.csv", "G:\\Share\\GEOG6293_Programming\\Melvin\\Nord.gdb\\Alaska_temp")

# importing the cooling degree days and creating a new column to input the Nordicity values
cooling = pd.read_csv('S:\\GEOG 6293.10 Special Topics 201503\\Melvin, Forrest - FMelvin\\Proj_file\\CoolingDegreeDays.csv')
# sorting the cooling degree days in ascending order because the greater number of cooling days the harsher the conditions
Alaska_coolDD = cooling.sort('CoolingDD', ascending = True)
Alaska_coolDD['cool_Nord_value'] = Nord_value
# creating a new csv file out of the new data with the new column
Alaska_coolDD.to_csv("Alaska_coolDD.csv")
arcpy.CopyRows_management ("G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file\\Alaska_coolDD.csv", "G:\\Share\\GEOG6293_Programming\\Melvin\\Nord.gdb\\Alaska_coolDD")

#importing number of days above 5.6 deg C and creating a new column which to ranks values and assign a Noricity value
heating = pd.read_csv('S:\\GEOG 6293.10 Special Topics 201503\\Melvin, Forrest - FMelvin\\Proj_file\\HeatingDD.csv')
# sorting the heating descending because the more the lower number of warm days the higher the harshness
# put the NA values at the begining as to not skew the values as much
Alaska_heatDD = heating.sort('HeatingDD', ascending = False, na_position='first')
Alaska_heatDD['heat_Nord_value'] = Nord_value 
# creating a new csv file out of the new data with the new column
Alaska_heatDD.to_csv("Alaska_heatDD.csv")
arcpy.CopyRows_management ("G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file\\Alaska_heatDD.csv", "G:\\Share\\GEOG6293_Programming\\Melvin\\Nord.gdb\\Alaska_heatDD")

####################################################################################
# setting arcpy work environment for this section
arcpy.env.workspace = "G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file"

# pulling up the mxd which will be manipulated
mxd = arcpy.mapping.MapDocument("Nordicity.mxd")
# deciding which data frame to work in
df = arcpy.mapping.ListDataFrames(mxd, "Alaska_Data_Frame")[0]
# adding the base map layer into the mxd
addLayer = arcpy.mapping.Layer("Alaska.shp")
# ssigning a place for the layer
arcpy.mapping.AddLayer(df, addLayer, "BOTTOM")
# saving the mxd base as a new mxd file
mxd.saveACopy("Nordicity1.mxd")
del mxd, addLayer

#################################################################################
arcpy.env.workspace = "G:\\Share\\GEOG6293_Programming\\Melvin\\Nord.gdb"
# This section imports XY coordinates to create the point shapefile 
# assigning which table to use and which fields in the table that will be used for the XY values that will be used for the coordinates
in_table = "G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file\\Lat_long.csv"
x_coords = "Lat"
y_coords = "Long"
saved_layer = "City_Featureclass"
out_Layer = "Alaska_Cities"
spRef = "Coordinate Systems\\Geographic Coordinate Systems\\World\\WGS 1984"

# making a layer of the 
arcpy.MakeXYEventLayer_management(in_table, x_coords, y_coords, out_Layer, spRef)
print arcpy.GetCount_management(out_Layer)
#Saving file named Alaska_Coords
arcpy.SaveToLayerFile_management(out_Layer, saved_layer, "", "CURRENT")

#########################################################################################
arcpy.env.workspace = "G:\\Share\\GEOG6293_Programming\\Melvin\\Nord.gdb"
#This section joins all other data to the the base data table Cities
# making a feature layer out of Alaska Cities in order to join tables to
arcpy.MakeFeatureLayer_management ("G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file\\City_Featureclass.shp", "City_out_Layer")
# assigning features and field on which to join the tables
inFeatures = "City_out_Layer"
inField = "Field2"
joinTable = "Alaska_pop"
joinField = "City"
fieldList = ["City", "pop_Nord_value"]
arcpy.AddJoin_management(inFeatures, inField, joinTable, joinField)

# joining tables to the layer to create a master table with all the important info
arcpy.AddJoin_management("City_out_Layer", "Field2", "Alaska_precip", "City")
arcpy.AddJoin_management("City_out_Layer", "Field2", "Alaska_temp", "City")
arcpy.AddJoin_management("City_out_Layer", "Field2", "Alaska_coolDD", "City")
arcpy.AddJoin_management("City_out_Layer", "Field2", "Alaska_heatDD", "City")
# creating a feature out of the City_out_Layer 
arcpy.CopyFeatures_management("City_out_Layer", "NordTable")

##########################################################################################
arcpy.env.workspace = "G:\\Share\\GEOG6293_Programming\\Melvin\\Nord.gdb"
#This section creates a final table which includes the final Nordicity values 
#Making a feature layer from previous step- joins must be done with feature layers not just classes
arcpy.MakeFeatureLayer_management("NordTable", "NordTable_Layer", "", "")
# assigning values to that will be used in the join
NordTable = "NordTable_Layer"
Nordicity = "G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file\\Nordicity_Final.csv"

# Joining final Nordicity values to the main NordTable with all the other values
arcpy.AddJoin_management(NordTable, "City_featureclass_Field2", Nordicity, "Cities", "KEEP_ALL")
arcpy.CopyFeatures_management("NordTable_Layer", "Final_Nordicity")

##################################################################################
arcpy.env.workspace = "G:\\Share\\GEOG6293_Programming\\Melvin\\Nord.gdb"
#This section interpolates the city points by the Nordicity Values and builds a raster that displays gradation of values across space
# since I will be using the 3D analyst extension I have to check that it is available and functioning
arcpy.CheckOutExtension("3D")
#Assigning shapefile and the out raster name 
FinalTable_shp = "G:\\Share\\GEOG6293_Programming\\Melvin\\Nord.gdb\\Final_Nordicity.shp"
Interpol = "G:\\Share\\GEOG6293_Programming\\Melvin\\Nord.gdb\\Interpol"

# interpolating points with a cell size of 0.08 to get an output raster of "Interpol"
arcpy.NaturalNeighbor_3d(FinalTable_shp, "Nordicity_Final_csv_Nordicity_Value", Interpol, "0.08")

##################################################################################
# This section takes this interpolated raster and fits it the the shapefile of Alaksa- this is 
#...necessary because the raster is spread across the whole of the points which covers part of the ocean(It just makes it look better)
arcpy.env.overwriteOutput = 1
arcpy.env.workspace = "G:\\Share\\GEOG6293_Programming\\Melvin\\Nord.gdb"
# I will be using the spatial analyst extension so I need to make sure it is accessible
arcpy.CheckOutExtension("spatial")
#Assigning variables "Interpol" is the raster that will be masked by the shapefile Alaska.shp
Interpol = "Interpol"
Alaska = "G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file\\Alaska.shp"
# naming the mask and assigning its path
Mask_extract_Alaska = "G:\\Share\\GEOG6293_Programming\\Melvin\\Nord.gdb\\Mask_Alaska"

# extracting Interpol raster by Alaska.shp and creating a raster that fits the shapefile
arcpy.gp.ExtractByMask_sa(Interpol, Alaska, Mask_extract_Alaska)

##################################################################################
arcpy.env.workspace = "G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file"

# pulling up the mxd which will be manipulated
mxd = arcpy.mapping.MapDocument("Nordicity1.mxd")
# deciding which data frame to work in
df = arcpy.mapping.ListDataFrames(mxd, "Alaska_Data_Frame")[0]
# adding the base map layer into the mxd
addLayer1 = arcpy.mapping.Layer("G:\\Share\\GEOG6293_Programming\\Melvin\\Nord.gdb\\Mask_Alaska")
addLayer2 = arcpy.mapping.Layer("G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file\\City_featureclass.shp")
# assigning a place for the layer
arcpy.mapping.AddLayer(df, addLayer1, "AUTO_ARRANGE")
arcpy.mapping.AddLayer(df, addLayer2, "TOP")

# saving the mxd base as a new mxd file
mxd.saveACopy("Nordicity2.mxd")
del mxd, addLayer1, addLayer2

# NOTE: OPEN G:\\Share\\GEOG6293_Programming\\Melvin\\Proj_file\\"Nordicity2.mxd" to see final product
# Sorry the colors are not as nice as in the presentation! 
# Thanks for a great semester!!- eventhough it was a struggle at times I will definitely be taking a lot away
#
#%%




