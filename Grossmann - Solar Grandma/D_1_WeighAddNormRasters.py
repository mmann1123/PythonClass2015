# Coder: Max Grossman
# CodeName: ApplyingRanks.py
# Description: Applies Ranks to Normalized Raster files, adds them, and 
# normalizes them once again.

# Contents:
#   A. Set environment
#   B. Apply raster weights
#   C. Add Rasters together
#   D. Normalize final raster

#%% A. Set Environment

import arcpy
aoi = 'WestPalm'
arcpy.env.workspace = r'G:\Share\GEOG6293_Programming\Grossman\Florida_FinalProject.gdb'
arcpy.env.outputOverwri
arcpy.env.mask = aoi
out_workspace = arcpy.env.workspace
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

#%% B. Apply Raster Weights

# The Ranks are as follows
#   GHI = 3
#   Inverse Distance from Powerlines = 2
#   Inverse Distance to Roads = 1
#   Distance to Cities = 1
#   Population Density = 1
#   Federal Lands = 1
#   Landcover = 1



# First I create a list with only the raster files I will weigh 
# I grab these with a fishnet that singles them out by the beginning of their
# name.

# I store this list in a variable Ras.
Ras = arcpy.ListRasters("norm_go*")

# Next I use a for loop to add weights to proper rasters
for ra in Ras:
    # First set the Raster object to a local variable, Raster_Weight
    Raster_Weight = arcpy.sa.Raster(ra)
    
    # Using if/else argument, decide what weight should be added
    
    # if statement uses Describe function and .name to get string of ra.
    # if it it is equal to "norm_go_WP_GHI", it goes to nested code block.
    if arcpy.Describe(Raster_Weight).name == "norm_go_WP_GHI":
        # If so, print the name to verify, then let user create new name for weighted raster
        print arcpy.Describe(Raster_Weight).name ; Raster_Name = raw_input("Name the output raster > ")
        # Weigh the raster appropriately.        
        Raster_Weighted = Raster_Weight * 3
        
    # if statement uses Describe function and .name to get string of ra.
    # if it it is equal to "norm_go_InvPowrDist_raster", it goes to nested code block.
    if arcpy.Describe(Raster_Weight).name == "norm_go_InvPowrDist_raster":
        # If so, print the name to verify, then let user create new name for weighted raster        
        print arcpy.Describe(Raster_Weight).name ; Raster_Name = raw_input("Name the output raster > ")
        # Weigh the raster appropriately.          
        Raster_Weighted = Raster_Weight * 2
        
    # When neither of those two conditions are met, the ra is passed to this
    # nested code block.
    else:
        # Print the name to verify, then let user create new name for weighted raster        
        print arcpy.Describe(Raster_Weight).name ; Raster_Name = raw_input("Name the output raster > ")
        # Weigh the raster appropriately and save it in Raster_Weightedd
        Raster_Weighted = Raster_Weight * 1
    
    # Save the raster as Raster_Name string concatenated with _weighted
    Raster_Weighted.save(str(Raster_Name) + "_weighted")
    # Laslty, print to verify that one ineteration has completed
    print "It has been weighted playa, nice job!"
    
#%% C. Add all Rasters Together

# With rasters weighed, I add them all together to make a final raster.

# First I store added raster in Added_Rasters variable 
Added_Rasters = arcpy.sa.Raster("weighted_Cities") + arcpy.sa.Raster("weighted_FedLands") + arcpy.sa.Raster("weighted_FloridaPopDen") + arcpy.sa.Raster("weighted_GHI") + arcpy.sa.Raster("weighted_InvPowrDist") + arcpy.sa.Raster("weighted_InvRoadDist") + arcpy.sa.Raster("weighted_LandCoverSolarLands")
# Next, I save Added_Rasters as "FinalWPSolarRaster
Added_Rasters.save("non_normalized_final_raster")

#%% D. Normalize final raster

# With a final raster created, I normalize it to values between 0 and 1.

# First I store final raster in FinRaster value. I use arpy.sa.Raster to do it
FinRaster = arcpy.sa.Rasters("non_normalized_final_raster")

# Next I grab the minimum value from FinRaster. 
# I use arcpy.GetRasterProperties to do so.
# I pass through FinRaster and "MINIMUM" to do so.
minpix = arcpy.GetRasterProperties_management(FinRaster, "MINIMUM")
# This is not a float so I need to print to get the Minimum and use
# raw_input and float functions to set the value as a float.
print minpix
minpix = float(raw_input(">"))
# Next I grab the maximum value from FinRaster. 
# I use arcpy.GetRasterProperties to do so.
# I pass through FinRaster and "MAXIMUM" to do so.
maxpix = arcpy.GetRasterProperties_management(FinRaster, "MAXIMUM")
print maxpix
maxpix = float(raw_input(">"))
# With the values I need, I can do the calculations to normalize

# First set x to FinRaster minus minpix
x = arcpy.sa.Raster(ra) - minpix
# Net I set the range to a variable, subtracting minpix from maxpix
rangepix = maxpix - minpix
# Lastly, I set norm_rast value to x / rangepix and save it as
# "norm_" and FinRaster concatonated 
norm_rast = x / rangepix
norm_rast.save("Normalized_finalSolarMCE")
