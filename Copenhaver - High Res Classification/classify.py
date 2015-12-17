########################################################################################################################
# File: classify.py
# Author: Andrew Copenhaver
# Date: December 11, 2015

# Description: This program is used to create an area of interest (AOI) raster file from a
#              two feature class shapefile containing the classification training sites.
#              This AOI raster will then be used as the training data for training a random forests classifier, also
#              include in the program.This program will export reference information about the shapefile, original raster,
#              the new AOI raster, the classification model and the classified imaged
#              to a .txt file named "reference_info.txt", which is saved in a folder of your choice.
#              This script is meant to be finalized in a second script called numpy_to_raster,
#              which rasterizes the output of the classification.

#              Note: This program does not create an additional AOI raster, but burns the shapefile
#              into the existing raw raster using gdal_rasterize. Make sure you have the raw raster
#              saved in a second location so the program doesn't ruin your only copy.

# How to Use: To use this program, define the shapefile which contains the classification
#             information, the raster which you wish to create the AOI with and the raster you want to classify

########################################################################################################################

# Import Modules

# Import OGR
from osgeo import ogr

# Import GDAL
from osgeo import gdal
from osgeo import gdal_array

# Import NumPy
import numpy as np

# import os
import os

# import scikit-learn
from sklearn.ensemble import RandomForestClassifier

# import scikit-image
from skimage.io import imsave

# import matplotlib
import matplotlib.pyplot as plt

# Register all of GDAL's stored drivers
gdal.AllRegister()

########################################################################################################################

# Define Data sources and locations
raster = r"G:\Share\GEOG6293_Programming\Data\ACopenhaver\final_proj_data\smallest_lbpm.img" # Raster  to be used to create AOI
shapefile = r'G:\Share\GEOG6293_Programming\Data\ACopenhaver\final_proj_data\training_sites\smallest_training.shp' # Shapefile containg training site information
raster_2_classify = r'G:\Share\GEOG6293_Programming\Data\ACopenhaver\final_proj_data\smallest_pantex.img' # Raster to classify

# Define save location
home_dir = r"G:\Share\GEOG6293_Programming\Data\ACopenhaver\final_proj_output" # Where the reference file text document is to be saved

# Create output text file to write results of shapefile verification to
text_output = open(os.path.join(home_dir, "reference_info.txt"), "a") # Create the reference text file

########################################################################################################################

# Extract Relevant information from shapefile and export to reference text file

# Open training sites shapefile dataset using OGR
shapefile_open = ogr.Open(shapefile)

# Verify shapefile, throw exception if shapefile does not exist or cannot be found
if not shapefile_open:
    raise Exception('Input shapefile cannot be found')

# Add header to reference file text document
text_output.write("Shapefile Information: \n\n")
print "Shapefile Information: \n"

# Write training sites shapefile filename to text document
text_output.write("Shapefile Filename: " + shapefile + "\n")

# Get shapefile file type and write to text document
driver = shapefile_open.GetDriver()
text_export = ('Data Format: {format}\n'.format(format=driver.name))
print text_export
text_output.write(text_export)

# Get short name (-l) from shapefile for GDAL rasterize command, write to text document
layer = shapefile_open.GetLayerByIndex(0)
text_export = ('Layer Short Name (-l): {name}\n'.format(name=layer.GetName()))
print text_export
layer_call = str(layer.GetName()) # Used in gdal_rasterize command below
text_output.write(text_export)

# Get layer geometry from training sites shapefile, write to text document
geometry = layer.GetGeomType() # This gets the geometry, but it needs to be translated to type name
geometry_name = ogr.GeometryTypeToName(geometry) # translates geom type to geom type name
text_export = ("Layer Geometry Type: {geometry}\n".format(geometry=geometry_name))
print text_export
text_output.write(text_export)

# Get spatial reference of training data, write to text document
spatial_ref = layer.GetSpatialRef() # gets long form information on spatial reference
proj4 = spatial_ref.ExportToProj4() # truncates spatial reference info into proj4
text_export = ('Layer Projection: {proj4}\n'.format(proj4=proj4))
print text_export
text_output.write(text_export)

# Get feature count for training data, write to text document
feature_count = layer.GetFeatureCount()
text_export = ('Feature Count: {number}\n'.format(number=feature_count))
print text_export
text_output.write(text_export)

# Get names of fields in training data, write to text document
defn = layer.GetLayerDefn() # before we can get names of fields, we need layer definition
field_count = defn.GetFieldCount() # calculate number of fields to be used in for-loop below
text_output.write('Field Names and Data Types: ')
for i in range(field_count):
    field_defn = defn.GetFieldDefn(i)
    text_export = ('\n\t\t\t\t - {name} - {datatype}\n\n'.format(name=field_defn.GetName(),
                                         datatype=field_defn.GetTypeName()))
    print text_export
    text_output.write(text_export)

# Get field information to put into gdal_rasterize call below
field_defn = defn.GetFieldDefn(1)
class_call = field_defn.GetName()

# Used to break sections for shapefile and raster info in text document
text_output.write("""_____________________________________________________________________________________________\n""")
print ("""_____________________________________________________________________________________________\n""")

########################################################################################################################

# Get information about raster to be used in gdal_rasterize command line call and to be written to text document

# Add header to raster section of text document
text_output.write("\nRaster Information:\n")
print "\nRaster Information:\n"
# Write raster  full filename and path to text document
text_output.write("\nRaster Dataset Filename:" + raster + "\n")

# Get information from raster using "gdalinfo" command line tool called through python. Read info into python. To be
# used in gdal_rasterize command line tool call

raster_open = gdal.Open(raster)

# Create the command to feed into gdalinfo via the os.popen function
raster_info_command =("gdalinfo -proj4 {raster}").format(raster = raster)
raster_info = os.popen(raster_info_command).read()

# Get corner information for raster information. This section is a pretty hard coded due to gdal's weak
# python API and the fact that I had to extract all of this information from a really long string created
# by the gdalinfo command line utility
#
# Get upper left and lower right corners of raster
upper_left = raster_info[raster_info.find("Upper Left")+15:raster_info.find("Upper Left")+38]
lower_right = raster_info[raster_info.find("Lower Right")+15:raster_info.find("Lower Right")+38]

# Get xmin, xmax, ymin, ymax from corner information retrieved above for raster

x_min = (upper_left[:upper_left.find(",")])
x_min = float(x_min)
y_min = lower_right[lower_right.find(",")+1:]
y_min = (y_min.replace(" ", ""))
y_min = float(y_min)
x_max = float(lower_right[:lower_right.find(",")])
y_max = upper_left[upper_left.find(",")+1:]
y_max = float(y_max.replace(" ", ""))

# Write xmin, xmax, ymin, ymax of raster to text document

text_export = "x min: {x_min}\n".format(x_min = x_min)
print text_export
text_output.write(text_export)
text_export = "y min: {y_min}\n".format(y_min = y_min)
print text_export
text_output.write(text_export)
text_export = "x max: {x_max}\n".format(x_max = x_max)
print text_export
text_output.write(text_export)
text_export = "y max: {y_max}\n".format(y_max = y_max)
print text_export
text_output.write(text_export)

# Get gdal driver code and long file type of raster to be written to text document and used in the gdal_rasterize command

text_export = ("GDAL Driver Code: {short} \nFile Type: {type}\n".format(short = raster_open.GetDriver().ShortName,
                                         type = raster_open.GetDriver().LongName))
print text_export
text_output.write(text_export)
driver_call = raster_open.GetDriver().ShortName


# Get projection info from raster, to be used in gdal_rasterize command and written to text document
projection = str(raster_open.GetProjectionRef())
projection = projection[projection.find("[") + 1: projection.find(",")] # This extracts projection from a long string
text_export = "Raster Projection: {projection}\n".format(projection = projection)
print text_export
text_output.write(text_export)

# Get pixel size information from raster, to be used in gdal_rasterize command and written to text document
geotransform = raster_open.GetGeoTransform()
if not geotransform is None:
    text_export = "Pixel Size = {x}, {y}\n".format(x = geotransform[1],y = geotransform[5])
    print text_export
    text_output.write(text_export)
pixel_call = geotransform[1]

# Creates a string which concatenates all relevant information gathered by code above. This string is a command for
# the gdal_rasterize command line tool. GDAL's python API crashes when I try to use it, so this is a somewhat
# pythonic workaround to keep the script automated

rasterize_command = "gdal_rasterize " + "-a " + '"'+ class_call +'"'+ " -l " + layer_call + " -of " + '"' + driver_call +\
                    '"' + " -a_nodata 0" + " -te " + str(x_min) + " " + str(y_min) + " " + str(x_max) + " " + str(y_max) + \
                    " -tr " + str(pixel_call) + " " + str(pixel_call) + " -ot Byte " +\
                    shapefile + " " + raster

# Write the gdal_rasterize command to the reference file text document
#text_output.write("gdal_rasterize Command: " + rasterize_command + "\n")

# Run the gdal_rasterize command from the command line using os.system to create AOI raster
os.system (rasterize_command)

# Used to break sections for base and the AOI raster info in text document
text_output.write("""_____________________________________________________________________________________________\n""")
print ("""_____________________________________________________________________________________________\n""")
########################################################################################################################

# This section makes sure that everything above worked and outputs information about the new AOI raster

# Add section header to text document
text_output.write("\nNew Area of Interest (AOI) Raster Statistics and Info: \n")
print "\nNew Area of Interest (AOI) Raster Statistics and Info: \n"
text_output.write("\n")

# Open new AOI raster using gdal.open
aoi_open = gdal.Open(raster, gdal.GA_ReadOnly)

# Read AOI raster band as an array, which can be used by numpy to calculate AOI raster statistics
aoi = aoi_open.GetRasterBand(1).ReadAsArray()

# Count number of pixels in each land cover class defined in the shapefile
classes = np.unique(aoi)
for c in classes:
    text_output.write('Class {class1} contains {number} pixels\n'.format(class1=c,
                                                 number=(aoi == c).sum()))
    print ('Class {class1} contains {number} pixels\n'.format(class1=c,
                                                 number=(aoi == c).sum()))

# Get projection info for AOI raster
projection = str(raster_open.GetProjectionRef())
projection = projection[projection.find("[") : projection.find(",")]
text_export = "AOI Raster Projection: {projection}\n".format(projection = projection)
print text_export
text_output.write(text_export)

# Get pixel size for AOI raster
geotransform = raster_open.GetGeoTransform()
if not geotransform is None:
    text_export = "AOI Raster Pixel Size = {x}, {y}\n".format(x = geotransform[1],y = geotransform[5])
    print text_export
    text_output.write(text_export)
pixel_call = geotransform[1]

text_output.write("""_____________________________________________________________________________________________\n""")
print ("""_____________________________________________________________________________________________\n""")

#######################################################################################################################

# This portion of code is focused on the classification of the image defined in the raster_2_classify variable
# at the top of the script.

# Add header to classification section in text document
text_output.write("Classification Information:\n")
print "Classification information\n"

# Using GDAL's Open tool, read the image we wish to classify and the AOI raster into python
print "Loading the raster to be classified and the AOI Raster \n"
classify_open = gdal.Open(raster_2_classify, gdal.GA_ReadOnly)
AOI_open = gdal.Open(raster, gdal.GA_ReadOnly)

print "Creating a numpy array to hold raster values\n"
#Creates a new numpy array filled with zeroes based on the size of the image to be classified, set to variable X_test
X_test = np.zeros((classify_open.RasterYSize, classify_open.RasterXSize, classify_open.RasterCount),
               gdal_array.GDALTypeCodeToNumericTypeCode(classify_open.GetRasterBand(1).DataType))

print "Counting bands\n"
# Get band count, print and send to text document
band_count = classify_open.RasterCount
text_export = "Number of bands in raster_2_classify variable: {band_count}\n".format(band_count = band_count)
text_output.write(text_export)
print text_export


# This portion of the script struggles with images of different resolutions or sizes, as it creates a "jagged array",
# which numpy is ill equipped to handle. I am currently looking into the possibility of masking the arrays with no data
# areas based on the length of the longest array.

print "Writing bands to numpy array\n"
# For all bands in the array (img.shape[2] is the depth of the array's third dimension), read raster band as array
for band in range(X_test.shape[2]):
    X_test[:, :, band] = classify_open.GetRasterBand(band + 1).ReadAsArray() # Read raster band into array, band+1 used to increment through for-loop

# Getting shape of the X_test array, which was modified in the above for loop
x_test_shape =  X_test.shape
text_export = "Shape of X_test (the test set): {test_shape}\n".format(test_shape = x_test_shape)
text_output.write(text_export)
print text_export

# Read AOI raster as array
y_test = AOI_open.GetRasterBand(1).ReadAsArray().astype(np.uint8)

# Count the number of training samples we have by counting non-zero values in AOI raster
sample_count = (y_test > 0).sum()
text_export = 'The dataset contains {number} samples\n'.format(number=sample_count)
text_output.write(text_export)
print text_export

# Find the unique classification labels in the AOI Raster
labels = np.unique(y_test[y_test > 0])
text_export = ('Training data classes in AOI raster: {classes}\n'.format(classes=labels))
text_output.write(text_export)
print text_export

# Define the training data to be used to train the random forest classifier
X_train = X_test[y_test > 0, :] # Training sites are indexed to anywhere that isn't a 0 within the AOI raster
y_train = y_test[y_test > 0]    # Training sites are indexed to anywhere that isn't a 0 within the AOI raster


# Build random forests classifier using scikit-learn
clf = RandomForestClassifier(n_estimators=2,  criterion="gini", oob_score=True, max_features= None, max_depth=30,
                             bootstrap=True, n_jobs=1) # n_jobs set to 1 to avoid memory issues

# Fit the model using the variables defined above
clf = clf.fit(X_train, y_train)

# Print the random forest classifier's out of bag score (a metric of classification error)
oob = clf.oob_score_
text_export = "OOB Score: {oob}\n ".format(oob = oob)
text_output.write(text_export)
print text_export


# Flatten the stacked image into a two dimensional array so that it can be used by scikit-learn
flat = (X_test.shape[0] * X_test.shape[1], X_test.shape[2])
X_test_flat = X_test.reshape(flat)
text_export = ('Flattened X_test shape {n}\n'.format(n=X_test_flat.shape))
text_output.write(text_export)
print text_export

# Delete unused variables to free up system memory
del X_train, y_train, y_test

# Predict the classes for the entire image using the flattened array
predictions = clf.predict(X_test_flat)

# Reshape our classification map to match our classification labels
predicted_classes = predictions.reshape(X_test[:, :, 0].shape)

# Save predicted classes to .csv file, which is to be converted in the
# numpy_to_raster script
np.savetxt(os.path.join(home_dir, "classification_output.csv"), predicted_classes, fmt= '%1.4f')

# Close reference file text document
text_output.close()
