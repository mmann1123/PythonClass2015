# Code: C_1_NormalizeRasters.py
# Coder: Max Grossman
# Description: Normalize the Rasters that come from places other than the 
# Fishnet, which have already been normalized

# Contents
#   A. Set Environment
#   B. List the Rasters
#   C. Normalize the Rasters

#%% Set Environment
import arcpy
arcpy.env.workspace = r"G:\Share\GEOG6293_Programming\Grossman\Florida_FinalProject.gdb"
# I will need the spatial analyst later in the for loop
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

#%% List the Rasters

# I save the list of rasters with ListRasters in Ras. 
# Note, the wildcard I used is based on a pre-fix I gave the rasters to 
# normalize in ArcCatelog
Ras = arcpy.ListRasters("go_*")

#%% Normalize the Rasters

# To normalize all rasters in the list, I use a for loop that:
#   first grabs the max and min value within each iteration over each raster.
#       I do this by setting minpix to GetRasterProperties. I pass through
#           the 'ra' raster and "MINIMUM". This gives me the information
#           but not as a float, which I need. To resolve this I reset minpix
#           to a raw_input, where i type the information, passed though
#           the float function. I do the same with the maximum value.
#   second I set value x to the pixel value, which I grab with arcpy.sa.Raster
#       with ra passed through, minus the minimum value
#   third I store the range, max minum min, in rangepix variable
#   fourth I store x / rangepix in norm_rast, which is the final normalized
#       value
#   finally I save each rater


# I iteratate through this for loop
for ra in Ras:
    minpix = arcpy.GetRasterProperties_management(ra, "MINIMUM")
    print minpix
    minpix = float(raw_input(">"))
    maxpix = arcpy.GetRasterProperties_management(ra, "MAXIMUM")
    print maxpix
    maxpix = float(raw_input(">"))
    x = arcpy.sa.Raster(ra) - minpix
    rangepix = maxpix - minpix
    norm_rast = x / rangepix
    norm_rast.save("norm_" + ra)
    print "This has been completed" # Once each raster has been normalized
    # I print "This has been completed" to verify
    
# Once the for loop has been run through, check ArcCatelog to verify
# The rasters are in the gdb.
    


