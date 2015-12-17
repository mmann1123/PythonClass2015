# Code: A_3_WestPalm_Clipper.py
# Coder : Max Grossman
# Description : Clips all shapefiles with WestPalm.shp

# Contents
#   A. Set Environment
#   B. Set clip inputs
#   C. Clip each feature class
#	D. Clip the Landcover Raster

#%% Set Environment

import arcpy
arcpy.env.workspace = r'G:\Share\GEOG6293_Programming\Grossman\Florida_FinalProject.gdb'
arcpy.env.overwriteOutput = True

#%% Set clip inputs

# Feature used for these clip, 'WestPalm'
clip_features = 'WestPalm'

# Lists all Feature Classes in the workspace envelope
# At this point in the project, the only features within my gdb were
# The non clipped feature classes. Thus, nothing is passed through
# the ListFeatureClasses function. If this were not the case, wildcards and 
# a regular list could be used.
fcs = arcpy.ListFeatureClasses()

# A for loop that clips each of the Feature Classes with "WestPalm"
for fc in fcs:
    out_feature_class = 'WP_clipped' + fc # The output of the clip, a new fc
    # run the clip geoprocess
    arcpy.Clip_analysis(fc,clip_features, out_feature_class)
    
#%% Clip the Landcover Raster

# To clip a raster, we use the Clip_managememnt tool. It is a bit different
# than the other clip. function. It needs the following inputs:

# 1) An input raster dataset  
# 2) An extent rectangle with a min&max X and min&max Y coordinate. 
#		For our purposes, we'll set this to the WestPalm extents.
#		this can be found either by using the arcpy.Describe().extent
#		method, or looking in ArcCatalog
# 3) The output raster. If output is to gdb, do not specify extension. 
#		if to a folder, .tif, .png, .gif ect. needs to be specified 
# 4) An optional template dataset, or shapefile to use as the extent.
#		in otherwords, a fc to clip the raster much like the Clip_analysis tool
# 5) Means to rectify nodata_values, inputs are either #, for leaving it, or a 
#		value user specifies
# 6) clipping geometry. this is optionaly, but if you are using a shapefile
#		to clip the raster, you need to input a string "ClippingGeometry
# 7) maintain clipping extent. If we want to match pixels to exactly
#		match the clip extent, type "MAINTAIN_EXTENT", if not "NO_MAINTAIN_EXTENT"

# Now we set parameters

inRast = "FloridaLandCover_ALbers"
# the extent syntax is a string, with just spaces to delimit coordinates
# these coordinates were found in ArcCatalog 
extent = "708570.41 262722.78 793990.760000002 335650.55"
outRas = "clipped_WP" + inRast
# the template dataset to clip from is WestPalm
tempDS = "WestPalm"
ndVal = "#"
clipGeom = "ClippingGeometry"
maintain_clipExt = "MAINTAIN_EXTENT"

# with parameters set, we run the function.

arcy.Clip_management(inRast, extent, outRas, tempDS, ndVal, clipGeom, maintain_clipExt)

# Check ArcCatalog to verify it was created.

