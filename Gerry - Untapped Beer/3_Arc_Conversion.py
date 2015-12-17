# -*- coding: utf-8 -*-

## Kady Gerry
## Geog 6392
## Project: Step 3
## Create shapefiles


#### This script will convert the combined csv data (from step two) into to shapefiles:
#### 1: UnTappd beer ratings by brewery location
#### 2: UnTappd beer ratings by venue location
#### 3: A projected polygon shapefile aggregating the number of checkins per country

import arcpy

## Create file geodatabase. It's already created, so it's commented out
out_folder_path = r'G:\Share\GEOG6293_Programming\Gerry\Project'
out_name = "geoDB.gdb"
#arcpy.CreateFileGDB_management(out_folder_path, out_name)
print "Geodatabase created"

## Set ArcPy environment variables
arcpy.env.workspace = r'G:\Share\GEOG6293_Programming\Gerry\Project\geoDB.gdb'
arcpy.env.overwriteOutput = True

## Create a table in the gdb from the combined checkin csv file created in the previous script
dataFile = r'G:\Share\GEOG6293_Programming\Gerry\Project\Data\CombinedData.csv'
arcpy.TableToTable_conversion(dataFile, arcpy.env.workspace, "data2")
print "Data import complete"

## Create a temp layer using Brewery lat/lon as the X/Y fields from the data in the table
## I didn't use the spatial reference parameter because it was reading degrees as meters
## That didn't work at all. The data is handled properly if the spatial reference is not defined.
table = arcpy.env.workspace + '\data2'
in_x_field = "BrewLon"
in_y_field = "BrewLat"
out_layer = "tempLyr"
spatial_reference = r'Coordinate Systems\Projected Coordinate Systems\World\WGS 1984 World Mercator.prj' 
arcpy.MakeXYEventLayer_management(table, in_x_field, in_y_field, out_layer) #, spatial_reference)


## Create a permanent shapefile for the brewery locations in the checkins
out_feature_class = arcpy.env.workspace + r'\Brewery'
arcpy.CopyFeatures_management(out_layer, out_feature_class)
print "Brewery shapefile created"

## Create a temp layer using Venue lat/lon as the X/Y fields from the data in the table
in_x_field = "VenueLon"
in_y_field = "VenueLat"
out_layer = "tempLyr"
arcpy.MakeXYEventLayer_management(table, in_x_field, in_y_field, out_layer) #, spatial_reference)


## Create a permanent layer for the venue locations in the checkins
out_feature_class = arcpy.env.workspace + r'\Venue'
arcpy.CopyFeatures_management(out_layer, out_feature_class)
print "Venue shapefile created"


## Create a layer with by country aggregated counts using spatial join
## Parameters for the spatialjoin function:
target_features = r'G:\Share\GEOG6293_Programming\Gerry\Project\SHP\countries_shp\countries.shp'
join_features = arcpy.env.workspace + r'\Brewery'
out_feature_class = "Country_count"
join_operation = "JOIN_ONE_TO_ONE"
join_type = "KEEP_ALL"
match_option = "CONTAINS"

## Run spatialjoin function
arcpy.SpatialJoin_analysis(target_features,
                           join_features,
                           out_feature_class,
                           join_operation,
                           join_type)#,
                           #match_option = match_option)

## Project the country layer, parameters:
in_dataset = "Country_Count"
out_dataset = "Country_ct_proj"
out_coor_system = arcpy.Describe("DC_poly_proj").spatialReference

## Run the project function
arcpy.Project_management(in_dataset, out_dataset, out_coor_system)

print "Ratings aggregated by country"
print "Script 3 is now complete"
