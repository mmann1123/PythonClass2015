######################################################################
## The purpose of this script is to identify good Helicopter Landing Zones (HLZs)
## in near trails in Yellowstone National Park to help rescue hikers in duress.
## The script uses, Digitial Evelation Data and Land Cover rasters, Streams and Lake shapefiles,
## and a Point of Interest (POI) shapefile.
##
## The script returns the areas of Land that have a slope of less than 7 degrees, Land Cover types (31, 52, 71, 81, 82),
## are not within 100 meters of streams or lakes, are within 2.5 km of the POI and have a size greater than 20,000 sq meters
##
## Author: Jeff Babinowich
######################################################################

# Sets the workspace, checks out extensions, and allows for overwriting of outputs
import arcpy
from arcpy.sa import *
arcpy.env.workspace = r'G:\Share\GEOG6293_Programming\Babinowich\Final\Yellowstone.gdb'
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

# Calculates the Slope using the Digital Elevation Data and then Reclassifies the Slope Raster to only include cells that have a slope
# between 0 and 7 (a good slope to land a helicopter) and then saves this as a new Raster called "Good_Slope"
inRaster = "imgn45w111_13"
outMeasurement = "DEGREE"

Slope = Slope(inRaster, outMeasurement)
Slope.save('G:\Share\GEOG6293_Programming\Babinowich\Final\Yellowstone.gdb\Slope')

Good_Slope = Reclassify("Slope", "Value", RemapRange([[0,7,1]]), "NODATA")
Good_Slope.save('G:\Share\GEOG6293_Programming\Babinowich\Final\Yellowstone.gdb\Good_Slope')

# Reclassifies the Land Cover Raster to only include LandCover values that are good for a Helicopter to Land,
# Creates a new raster and names it "Good_LC"
# Land Cover codes: 31 = Barren, 52 = Shrub/Scrub, 71 = Grassland/Herbaceous, 81 = Pasture/Hay, 82 = Cultivated Crops
LC = "LC"

Good_LC = Reclassify(LC, "Value", RemapValue([[31,1],[52,1],[71,1],[81,1],[82,1]]), "NODATA")
Good_LC.save('G:\Share\GEOG6293_Programming\Babinowich\Final\Yellowstone.gdb\Good_LC')

# Creating new raster using the Plus funtion that consists of only cells that are in both "Good_Slope" and "Good_LC" rasters
# Saves this new raster as "Good_Land", and then converts it to a polygon called "Good_Land_poly"
outPolygon = 'G:\Share\GEOG6293_Programming\Babinowich\Final\Yellowstone.gdb\Good_Land_poly'

Good_Land = Plus("Good_Slope", "Good_LC")
Good_Land.save('G:\Share\GEOG6293_Programming\Babinowich\Final\Yellowstone.gdb\Good_Land')
arcpy.RasterToPolygon_conversion("Good_Land", outPolygon, "NO_SIMPLIFY")

# Creates a Buffer with a radius of 2.5 km around the Point of Interest (the distressed hiker),
# and then clips "Good_Land_poly" to its extent and saves the new polygon as "AOR_Land"
POI = "POI"

arcpy.Buffer_analysis(POI, "G:\Share\GEOG6293_Programming\Babinowich\Final\Yellowstone.gdb\AOR", "2.5 Kilometers", "FULL", "ROUND", "ALL")
arcpy.Clip_analysis("Good_Land_poly", "AOR", "G:\Share\GEOG6293_Programming\Babinowich\Final\Yellowstone.gdb\AOR_Land")

# Buffer Lakes and Streams 100 Meters (to ensure HLZ is not too close to water) and then remove these areas from Good Land polygon
# creating "AOR_Final" Polygon
River = "Streams"
Lake = "Lakes"

arcpy.Buffer_analysis(River, "G:\Share\GEOG6293_Programming\Babinowich\Final\Yellowstone.gdb\Streams_Buff", "100 Meters", "FULL", "ROUND", "ALL")
arcpy.Buffer_analysis(Lake, "G:\Share\GEOG6293_Programming\Babinowich\Final\Yellowstone.gdb\Lakes_Buff", "100 Meters", "FULL", "ROUND", "ALL")

arcpy.Erase_analysis("AOR_Land", "Streams_Buff", "G:\Share\GEOG6293_Programming\Babinowich\Final\Yellowstone.gdb\AOR_Land_River")
arcpy.Erase_analysis("AOR_Land_River", "Lakes_Buff", "G:\Share\GEOG6293_Programming\Babinowich\Final\Yellowstone.gdb\AOR_Good_Land")
arcpy.MultipartToSinglepart_management("AOR_Good_Land", "G:\Share\GEOG6293_Programming\Babinowich\Final\Yellowstone.gdb\Final\AOR_Final")

# Select Features from the "AOR_Final" shapefile that have a area >= 20000 square meters (large enough for an HLZ)
# Creates Final shapefile "Good_HLZ"
AreaSQL = 'Shape_Area' + ' >= 20000'
arcpy.MakeFeatureLayer_management("AOR_Final", "AOR_Final_lyr")
arcpy.SelectLayerByAttribute_management ("AOR_Final_lyr", "NEW_SELECTION", AreaSQL)
arcpy.CopyFeatures_management("AOR_Final_lyr", "G:\Share\GEOG6293_Programming\Babinowich\Final\Yellowstone.gdb\Final\Good_HLZ")

# Uses the GenerateNear Table to identify the 5 Features that are nearest to POI that have area > 20000 square meters
# and then join this tbale to the Good_HLZ feature class and create a new final shapefile that of only the 5 closests HLZs
arcpy.GenerateNearTable_analysis("POI", "Good_HLZ", "Close_HLZ", "2500 Meters", "", "", "ALL", "5")
arcpy.MakeFeatureLayer_management ("Good_HLZ", "Good_HLZ_lay")
arcpy.AddJoin_management("Good_HLZ_lay", "OBJECTID", "Close_HLZ", "NEAR_FID", "KEEP_COMMON")
arcpy.CopyFeatures_management("Good_HLZ_lay", "G:\Share\GEOG6293_Programming\Babinowich\Final\Yellowstone.gdb\Final\Nearest_Good_HLZ")
