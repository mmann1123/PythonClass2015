# Code: B_3_FedLndLandCvrReclass.py
# Coder: Max Grossman
# Description: Reclassifies specified Landcover Classes to 1, 0 

# Contents
#   A. Set Environment
#   B. LandCover Parameters
#   C. LandCover Reclassification 
#   D. FedLands Parameters
#   E. FedLands Reclassification
#%% Set Parameters

import arcpy
arcpy.env.workspace = r"G:\Share\GEOG6293_Programming\Grossman\Florida_FinalProject.gdb"
aoi = 'WestPalm'
arcpy.env.mask = aoi
# the spatial extension needs to be checked out
arcpy.CheckoutExtension("Spatial")
arcpy.env.overwriteOutput = True

#%% LandCover Parameters

# Before reclassifying Landcover, the parameters to do so must be set
# I made two classes, 1 for all land suitable for solar (flat land), and 
# 0, those that are not flat/or land

# first I set the in raster
in_raster = "Clipped_WP_FloridaLandcover_ALbers"
# next I set the parameters to reclassify. To do so I need to use the
# spatial analyst's RemapValue fucntion. The synax for this is an list of 
# arrays. Each array has either 2 or 3 values depending on weather the 
# reclassfied group reclassifies a single value from original raster or a 
# range. If just one value,  the arrays in that list only have 2 values, first
# the value from the original raster and the second the value that original
# value will be reclassified to. If it is a range to be reclassified, the first
# two values delim the original raster's range, and the third the value values
# will be reclassified to.

# Here, pixels between 2 and 8, flat land, are set to 1, 9 to 19 to 0, 20 to 1
# and 21 to 23 to 0
remap = arcpy.sa.RemapValue([[2,8,1],[9,19,0],[20,1], [21,23,0]])
# This sets the field from which I reclassify
reclass_field = "Value"
# This defines how I deal with missing pixels. I leave them to 'no data'
missing_values = "NODATA"

#%% LandCover Reclassification

# Next I store the reclassify function in the Florida_LandCover variable 
# I pass through the in_raster, reclass_field, remap, and missing_values
Florida_LandCover = arcpy.sa.Reclassify(in_raster, reclass_field, remap, missing_values)
# Next, I save the reclassified raster by calling .save on Florida_LandCover
# and I name it.
Florida_LandCover.save("norm_LandCoverSolarLands_reclass")
# Note, the norm_ prefix is so to avoid adding it to a list to normalize values later

#%% FedLands Parameters

# Next I set the parameters to reclassify FedLands

# I set the in_raster
in_raster = "Clipped_WP_fedland_Albers_Straightraster"
# Set my Remap. The values 0, 1 and 127 come from the PolygonToRaster
# 0 signifies a distance of 0 meters to a federal land, others are distance
# my only criteria here is to not be on a federal land. So if not 0, its a 1
remap = arcpy.sa.RemapValue([[0,1],[1,127,0]])
# Similarly, my re_class field is Value
reclass_field = "Value"

#%% FedLands Reclassification

# I set the reclassification to Florida_fedlands
Florida_fedlands = arcpy.sa.Reclassify(in_raster, reclass_field, remap, missing_values)
# I save reclassification with .save
Florida_fedlands.save("norm_FedLands_reclass")
# Note, the norm_ prefix is so to avoid adding it to a list to normalize values later