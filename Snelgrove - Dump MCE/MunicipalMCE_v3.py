###################
#
# Author: Christian Snelgrove
# Last Update: 12/15/2015
# Description: This version of my script will focus on list comprehension
# and overall simplification of the processes being performed (repetitive tasks)
#
#
# NOTE: Due to restrictions on what you can reclassify a raster as, this MCE will
# use a weighting system out of 100 rather than 1.
#
# Weighting System (higher is better):
#   Rivers Total: 20
#      0 - 2000M: 0
#         2001+M: 20
#   
#    Roads Total: 30
#      0 - 2000M: 30
#   2001 - 4000M: 20
#   4001 - 6000M: 10
#         6001+M: 0 
#
#    Urban Total: 20
#      0 - 1000M: 20
#   1001 - 2000M: 15
#   2001 - 3000M: 10
#   3001 - 4000M: 5
#   4001 - 5000M: 0
#   5001 - 6000M: 20
#
# Railroad Total: 10
#      0 - 5000M: 0
#          5001+: 10
#
#   Border Total: 20
#      0 - 2000M: 0
#   2001 - 4000M: 4
#   4001 - 6000M: 8
#   6001 - 8000M: 12
#  8001 - 10000M: 16
#        100001+: 20
#
#   Highly Suitable: 80 - 100 (3)
#   Moderately Suitable: 50 - 79 (2)
#   Unsuitable: 0 - 49 (1)
#
###################

import arcpy
arcpy.CheckOutExtension("Spatial")
import os

#Set workspace
arcpy.env.workspace = r"G:\Share\GEOG6293_Programming\Data\Snelgrove\Final Project\Illinois MCE.gdb"
print "Workspace set!"

#Sets some environment settings
arcpy.env.overwriteOutput = True
arcpy.env.pyramid = "PYRAMIDS -1 NEAREST DEFAULT"
print "Environments sets!"

#Reads in polygons that need to be reprojected/sets output coordinate system
need_projecting = arcpy.ListFeatureClasses()
outCS = arcpy.SpatialReference('USA Contiguous Equidistant Conic')
n = 1

#Reprojects input shapefiles into USA Continguous Equidistant Conic
for fc in need_projecting:
    outFC = fc + "_projected"
    arcpy.Project_management(fc, outFC, outCS)
    print "Reprojection", n, "complete!"
    n += 1

#Sets more environment settings
arcpy.env.mask = "Illinois_projected"
arcpy.env.extent = "Illinois_projected"

#Clips the shapefiles that are not already clipped
need_clipping = arcpy.ListFeatureClasses()
clipFC = "Illinois_projected"
n = 1

for fc in need_clipping:
    if "Illinois" not in fc and "projected" in fc:
        outFC = "Illinois_" + fc
        arcpy.Clip_analysis(fc, clipFC, outFC)
        print "Clip", n, "complete!"
        n += 1
    else:
        pass

#Calculates Euclidean Distance for all feature classes
cell = 50
eucdistlist = arcpy.ListFeatureClasses()
n = 1

for fc in eucdistlist:
    if "Illinois" in fc and "projected" in fc:
        outeucdist = arcpy.sa.EucDistance(in_source_data = fc, cell_size = cell)
        outeucdist.save(arcpy.env.workspace + os.sep + fc + "_eucdist")
        print "Euclidean distance", n, "calculated!"
        n += 1
    else:
        pass


#Uses tuples and a nested list to pair raster with their proper reclassify range
river_range = ("Illinois_rivers_projected_eucdist", [[0, 2000, 0], [2000, 10000000, 20]])
road_range = ("Illinois_roads_projected_eucdist", [[0, 2000, 30], [2000, 4000, 20], [4000, 6000, 10], [6000, 100000000, 0]])
urban_range = ("Illinois_urbanareas_projected_eucdist", [[0, 1000, 20], [1000, 2000, 15], [2000, 3000, 10], [3000, 4000, 5], [4000, 5000, 0], [5000, 1000000000, 20]])
railroad_range = ("Illinois_Railroads_projected_eucdist", [[0, 5000, 0], [5000, 10000000000, 10]])
border_range = ("Illinois_Borders_projected_eucdist", [[0, 2000, 0], [2000, 4000, 4], [4000, 6000, 8], [6000, 8000, 12],[8000, 10000, 16], [10000, 1000000000, 20]])
remap = [river_range, road_range, urban_range, railroad_range, border_range]
n = 1

for item in remap:
    outreclass = arcpy.sa.Reclassify(item[0], "Value", arcpy.sa.RemapRange(item[1]))
    outreclass.save(arcpy.env.workspace + os.sep + item[0] + "_reclass")
    print "Reclass", n, "done!"
    n += 1

#Adds rasters together to output MCE values
MCE = arcpy.sa.Raster("Illinois_Railroads_projected_eucdist_reclass") + arcpy.sa.Raster("Illinois_Borders_projected_eucdist_reclass") + arcpy.sa.Raster("Illinois_rivers_projected_eucdist_reclass") + arcpy.sa.Raster("Illinois_roads_projected_eucdist_reclass") + arcpy.sa.Raster("Illinois_urbanareas_projected_eucdist_reclass")

MCE.save(arcpy.env.workspace + os.sep + "MCE_zone")
print "Raster calc done!"

#Reclassifies the final MCE raster layer into highly suitable, moderately suitable, and unsuitable.
outReclass = arcpy.sa.Reclassify("MCE_zone", "Value", arcpy.sa.RemapRange([[0, 50, 1], [50, 80, 2], [80, 100, 3]]))
outReclass.save(arcpy.env.workspace + os.sep + "MCE_zone_reclass")
        
print "Work complete!"




    



