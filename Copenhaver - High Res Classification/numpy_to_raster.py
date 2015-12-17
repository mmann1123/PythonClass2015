########################################################################################################################
# File: classify.py
# Author: Andrew Copenhaver
# Date: December 11, 2015

# Description: This is a simple program that is written to take the .csv file created by the classify.py script
#              and convert it to a raster


# How to Use: To use this program, define the predicted classification array and
#             the raster which you wish used to create the AOI

########################################################################################################################

# Import Modules

# import arcpy
import arcpy

#import numpy
import numpy as np

# import pandas
import pandas as pd

# import gdal
from osgeo import gdal

#import os
import os
########################################################################################################################

# Set variables

raster = r"G:\Share\GEOG6293_Programming\Data\ACopenhaver\final_proj_data\hog_ext.img"  # raster used to create AOIs, same variable as defined in classify.py script

# Read in array as dataframe
df =pd.read_csv(r"G:\Share\GEOG6293_Programming\Data\ACopenhaver\final_proj_output\predicted.csv", sep=',',header=None)

# Convert dataframe to numpy array
array = df.as_matrix()

########################################################################################################################
# Create the command to feed into gdalinfo via the os.popen function. This will give us the information we need to feed
# the NumPyArrayToRaster tool
raster_open = gdal.Open(raster)
raster_info_command =("gdalinfo -proj4 {raster}").format(raster = raster)
raster_info = os.popen(raster_info_command).read()


# Get corner information for raster information. This section is a pretty hard coded due to gdal's weak
# python API and the fact that I had to extract all of this information from a really long string created
# by the gdalinfo command line utility

# Get upper left and lower right corners of raster
upper_left = raster_info[raster_info.find("Upper Left")+15:raster_info.find("Upper Left")+38]
lower_right = raster_info[raster_info.find("Lower Right")+15:raster_info.find("Lower Right")+38]

# Get pixel size information from raster, to be used NumPyArrayToRaster function
geotransform = raster_open.GetGeoTransform()
if not geotransform is None:
    pixel_call = float(geotransform[1])
    print pixel_call

# Create and save raster to geodatabase. This doesn't work because the array isn't right. It got messed up when I reshaped
# the array in the other script
created_raster = arcpy.NumPyArrayToRaster(array, x_cell_size = pixel_call, y_cell_size = pixel_call, value_to_nodata = 0)
created_raster.save(r"G:\Share\GEOG6293_Programming\Data\ACopenhaver\final_proj_output\raster_output.gdb\raster_output\classified")