#%%
# Final Project Initial Data import and transformation
#
# consider putting multiple e00 in a file and running a for-in to convert all
#
#

# import system modules-- conversion is within arcpy
import arcpy
from arcpy import env
import os

# set my workspace
arcpy.env.workspace = "G:/Share/GEOG6293_Programming/Alles/Final/nsocs.e00"

# assign variables
importE00File = "nsocs.e00"
outDirectory = "G:/Share/GEOG6293_Programming/Alles/Final/nsocs.e00"
outNames = "nsocs.aml"

# now we need to delete any pre-existing files with same name since
# the tool does not auto-overwrite
# Delete pre-existing ouput

# Error message may appear because there is no file with that name, Coverage is still imported
if env.overwriteOutput :
	if os.path.exists(nsocs.aml):
		os.remove(outNames)

# import .aml from within the E00 file
arcpy.ImportFromE00_conversion(importE00File, outDirectory, outNames)

#%%