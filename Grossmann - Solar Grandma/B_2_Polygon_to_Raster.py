# Code: B_2_Polygon_to_Raster.py
# Coder: Max Grossman
# Description: Converts all polygon files to raster files

# Contents
#   A. Set Environment and universal inputs
#   B. Population Density Rasterize
#   C. FedLands Raseterize
#   D. GHI Rasterize
#   E. Cities Rasterize
#   F. Powerlines Rasterize
#   G. Roads Rasterize

#%% A. Set Environment
import arcpy
arcpy.env.workspace = r'G:\Share\GEOG6293_Programming\Grossman\Florida_FinalProject.gdb'
aoi = "WestPalm"
arcpy.env.mask = aoi
arcpy.env.overwriteOutput = True

# each polygon will be converted to a raster with 30 meter pixels
cell_size = 30
# each new raster cell will be assigned per the vector file's polygons
# that take the maximum area in the raster pixel being created.
cell_assignment = "MAXIMUM_AREA"

# the PolygonToRaster() function is used for each of these conversions.
# this function takes 6 arguments
#   1) The features to be converted to a raster
#   2) The field within the respective feature used to calcualte pixel values
#   3) The name of the new raster
#   4) The cell assignment schema
#   5) priority field, which I set to "#"
#   6) The size of the cell

#%% B. Population Density Rasterize 

# the feature being rasterized is a clippd PopulationDensity shape in WestPalm
in_features_popden = "clipped_WP_FloridaPopDen_Albers"
# the PopulationDensity per SqKm is used 
# (this is a bit counter intuitive I recognize now, as cell_size > km)
field_popden = "PopDenSqKm" 
# the new name is the infeature concatonated with "raster"
out_raster_popden = "go_WP_FloridaPopDen"
# Next I run the function
arcpy.PolygonToRaster_conversion(in_features_popden,field_popden,out_raster_popden, cell_assignment, "#", cell_size)

#%% C. Fed Land Rasterize

# the feature being rasterized is a WestPalmFishNet_clipped
in_features_fedlands = "WestPalmFishNet_clipped"
# the field for values is FedLandsDis
field_fedlands = "FedLandsDis"
# raster name
out_raster_fedlands =  "WP_FedLandsDis_raster"
# the functoion
arcpy.PolygonToRaster_conversion(in_features_fedlands,field_popden,out_raster_popden, cell_assignment, "#", cell_size)

#%% GHI Rasterize

# the feature rasterized is clipped_WP_GHI_US_Albers_Straight
in_features_GHI = "clipped_WP_GHI_US_Albers_Straight"
# the field is ANN_GHI, annual Global Horizontal Irradiance
field_GHI = "ANN_GHI"
# the output 
out_raster_GHI = "go_WP_GHI"

# Polygon to Raster function
arcpy.PolygonToRaster_conversion(in_features_GHI,field_GHI,out_raster_GHI, cell_assignment, "#", cell_size)

#%% Rasterize Distance to Cities

# the in feacture is WestPalmFishNet_clipped
in_features_cities = "WestPalmFishNet_clipped"
# the in field
field_cities = "NormDistCit"
# the out raster name
out_raster_cities =  "norm_CitiesDist_raster"
# the function
arcpy.PolygonToRaster_conversion(in_features_cities, field_cities, out_raster_cities, cell_assignment, "#", cell_size)

#%% Rasterize Powerlines


# The in feature class
in_features_pw = "WestPalmFishNet_clipped"
# the field to calculate pixels
field_pw = "PWLInvDis"
# the new output raster
out_raster_pw = "norm_go_InvPowrDist_raster"
# function
arcpy.PolygonToRaster_conversion(in_features_pw, field_pw, out_raster_pw, cell_assignment, "#", cell_size)

#%% Rasterize Roads

# The in feature class
in_features_road = "WestPalmFishNet_clipped"
# This is the field to calculate the distnace
field_road = "RoadsInvDis"
# output raster name
out_raster_road = "norm_go_RoadsInvDist_raster"
# function
arcpy.PolylineToRaster_conversion(in_features_road, field_road, out_raster_road, cell_assignment, "#", cell_size)

# All feature classes should be rasterized. Check ArcCatelog to check gdb