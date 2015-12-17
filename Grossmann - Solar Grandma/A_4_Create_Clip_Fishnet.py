# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 16:21:06 2015

@author: maxgrossman
"""

# Code: Create_Clip_Fishnet.py
# Coder: Max Grossman
# Description: Creates Fishnet to be used to calculate Euclidean Disance for
# cities, powerlines, and roads

# Contents:
#   A. Environment Settings
#   B. Creating Fishnet
#   C. Adding fields with distance to roads, powerlines, cities
#   D. Clip Fishnet


#%% A. Set Environment

import arcpy
arcpy.env.workspace = r"G:\Share\GEOG6293_Programming\Grossman\Florida_FinalProject.gdb"
arcpy.env.outputOverwrite = True

#%% B. Create Fishnet

# Before I create my fishnet, I need to get the extent of WestPalm shape file
# so to mimic it's extent when I create the fishnet. First I need to grab
# the extent from arcpy.Describe()

# To do so, I first set fc to "WestPalm"
fc = "WestPalm"

# Next I use the Describe and extent to get the extent of WestPalm
extent = arcpy.Describe(fc).extent # set extent to extent within Describe function

# This returns an object and not the string input that the fishnet 
# function requires. To do this I Call XMin,Ymin,XMax, and YMax on extent
west = str(extent.XMin) # set west to extent's XMin ; I also make it and the rest a string
south = str(extent.YMin) # set south to extent's Ymin
east = str(extent.XMax) # set east to extent's XMax
north = str(extent.YMax) # set north to extent's YMax

# Print each to verify output is correct
print "XMin: " + west
print "XMax: " + east
print "YMin: " + south 
print "YMax: " + north 

# Now I can create my fishnet. First I set the fishnet inputs

out_feature_class = "WestPalmFishNet" #Fishnet to create

coordOrigin = west + " " + north  # The origin pnt; top left corner of fishnet
cell_width = "30" # CellWidth; This will be in meters because of  
cell_height = "30" # CellHeight; This be in meters becuase of GEOCOORDSYS
num_rows = 0 # Setting this to 0 makes num_rows determined by cell height
num_col = 0 # Setting this to 0 makes num_rows determined by cell width
corn_coord = east + " " + south # the opposite corner of origin
labels = "NO_LABELS" # No labels will be added to each polygon
template = west, east, south, north # Template is the extent of WestPalm
geometry_type = "POLYGON" # I will make Polygons

# Next I set the output coordinate system.

# To get the output coordinate system of choice as a prj file, in ArcGIS :
#   ArcMap>TableOfContents>Righclick Layers>Properties>CoordinateSystem
#   GeographicCoordinateSystem>Find GCS of interest >RightClick > Save As
#   Save to file of choice

# With GCS.prj, set arcpy.outputCoordinateSystem to arcpy.SpatialReference()
# with the file path passed through. 
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(r"G:\Share\GEOG6293_Programming\Grossman\FinalProject\NAD 1983 HARN.prj")

# Finally, call arcpy.CreateFishnet_management with variables passed through.
arcpy.CreateFishnet_management(out_feature_class, coordOrigin, cell_width, cell_height ,num_rows, num_col, corn_coord, labels, template, geometry_type)

# See function documentation for extra help -> is.gd/MEOhYx

#%% C. Add Fields with Distance to roads, powerlines, cities

# This process can be automated with a nice script
# found here -> http://goo.gl/W9ZtwA

# In the end it should fields with Distance fields for each of the three
# features (roads, powerlines, and cities)

# First I set the three fc I want to calculate distance from to variables

Cities = "WP_Cities"
Roads = "WP_Roads"
Powerlines = "WP_Powerlines"
FedLands = "clipped_WP_fedland_Albers_Straight"

# I then add these to a dictionary with these variables as the keys and 
# the name of what they are as their corresponding values.

WPdict = {}
WPdict [Cities] = "Cit"
WPdict [Roads] = "Rds"
WPdict [Powerlines] = "Pwr"
WPdict [FedLands] = "Fed"

# Note, I have do include FedLands becuase they are but two polygons inside
# the 

# Next, I create a list that will track the fields I create as they are added
# to the fishnet

addedfields = []

# Last, I set "WestPalmFishNet" to a variable used in for loop
shp = "WestPalmFishNet"

# Now I will use a forloop to iterate through the analysis

# First, I create a new array that will direct the automated analysis.
# The names correspond with the key names I created for WPdict 
for NearFC in [Cities, Roads, Powerlines, FedLands]:
        
    # Perform Near Analysis
    arcpy.Near_analysis(shp, NearFC)
        
       
    # Add fields that will store these results
    arcpy.AddField_management(shp, WPdict[NearFC] + "_DIST", "DOUBLE")
        
    # Store the Analysis information in these fields    
    arcpy.CalculateField_management(shp, WPdict[NearFC] + "_DIST", "!NEAR_DIST!", "PYTHON_9.3")

    # Next I will delete the original Near_FID and Near_DIST fields
    # I do not need them as I copied their information to new fields
    arcpy.DeleteField_management(NearFC, "NEAR_DIST")
        
    # Lastly, Track the added fields and print it to verify
    addedfields.append(WPdict[NearFC], + "_DIST")
    print addedfields 

# Before proceeding to next codeblock, open up ArcCatelog/ArcMap to verify 
# fields have been added

#%% D. Clip the FishNet
    
# With the fishnet and respective fields added, I must now clip it to 
# The WestPalm.shp file's shape. 

ClipperFC = "WestPalm" # I clip with WestPalm
TargetFC = "WestPalmFishNet" # I am targeting WestPalmFishNet to clip 
ResultFC = TargetFC + "_clipped" # I rename it with _clipped

# I use the Clip_analysis tool
arcpy.Clip_analysis(ClipperFC,TargetFC,ResultFC)

