######
# Final Project
# G:\Share\GEOG6293_Programming\Stockton\FinalProject\FinalProjectStockton.py
# Jon Stockton
# December 16, 2015
######

## This script is used to explore how land use has changed in the jurisdictions in the DC area (referred
## to here as counties, though also including cities) from 1992 to 2011.
## Input:
##   Land use rasters from National Land Cover Database
##      Stored in: G:\Share\GEOG6293_Programming\Stockton\FinalProject\Rasters
##      30 m resolution
##      Four years: 1992, 2001, 2006, 2011
##      The rasters used could easily be changed if different years become available.
##      All rasters in the specified Rasters directory are used.
##   Polygon feature class of counties
##   Point feature class representing downtown DC (at the White House)
##      Both of these are stored in the working geodatabase
##   Geodatabase: G:\Share\GEOG6293_Programming\Stockton\FinalProject\Project.gdb
## The script is divided into four major sections.
##   1. Tabulate the area of each land type in each county for each year
##   2. Update the tables to include percentage of land area of major land type groups
##        (urban, natural, farmland) for each county for each year
##   3. Calculate the mean center of urban land types in each county for each year and 
##        calculate the distance to downtown DC
##   4. Create change rasters for each county for each year with newly created urban areas for that year
## Each section is described in more detail below.
## All output is written to the geodatabase.


print "Starting Script"

#import and check out spatial analyst
import arcpy
arcpy.CheckOutExtension("Spatial")

arcpy.env.overwriteOutput = True

#define workspace variables
wksp = r'G:\Share\GEOG6293_Programming\Stockton\FinalProject'
wkspgdb = wksp + r'\Project.gdb'

print "Output Geodatabase: %s" % wkspgdb

#create variable for counties feature class, as well as downtown DC point feature class
counties = wkspgdb + r'\counties_all'
downtown = wkspgdb + r'\DowntownDC'

#get the spatial ref from the counties list (Maryland State Plane) and set as the output coordinate system
spatial_ref = arcpy.Describe(counties).spatialReference
arcpy.env.outputCoordinateSystem = spatial_ref

#get the list of rasters in the Rasters directory
raster_dir = wksp + r'\Rasters'
#set the workspace to the rasters directory and list rasters
arcpy.env.workspace = raster_dir
raster_list = arcpy.ListRasters()
#this loop adds the full path name to the raster name in the raster list
#this is so we can change the workspace to the geodatabase so everything outputs there instead of into the
#source rasters folder
for i in range(len(raster_list)):
    raster_list[i] = raster_dir + '\\' + raster_list[i]


#set the workspace to the geodatabase
arcpy.env.workspace = wkspgdb

####################################################################################################
## Section 1
## This section calculates the total land area of each land type by county for every raster.
## It loops through the raster list and uses the Tabulate Area function to create a table.
## The output of this section is a table for each year listing the land area of each land type by county.
## Table name for each year is: "Tabulate_year"

print "Starting Section 1: Tabluate area"

#this is the list of all tables create below, so we can use it in the next section
table_list = []

#loop through the raster list
for raster in raster_list:
    #get the year from the raster name to use in the name of the output table
    year = raster[-8:-4]
    print "Processing: " + year
    #define the name of the output table
    out_table = wkspgdb + r'\Tabulate_' + year
    #add the created table name to the table list
    table_list.append(out_table)
    #tabulate the area of each raster value in each county and store in a table
    arcpy.sa.TabulateArea(counties, "NAME", raster, "VALUE", out_table, 30)



#####################################################################################################
## Section 2
## This section takes the tables created above and adds fields and calculates for each county the
## total area and percentage of three land type categories: urban, natural and farmland.
## The 1992 raster has different land type classifications so its fields are calculated differently
## from the others. There is no new output, the tables created above are updated with fields UrbanPer,
## NaturalPer and FarmPer, percentage of land area of urban, natural and farm land types.

print "Starting Section 2: Update tables"

for tablename in table_list:
    #get the year from the table name
    year = tablename[-4:]
    print "Updating: " + year

    #The first section is for all years other than 1992
    if year != "1992":

        #add a new field for the sum of all the urban land types
        arcpy.AddField_management(tablename, "Urban", "FLOAT")

        #update the urban field with the sum of all the urban land types
        with arcpy.da.UpdateCursor(tablename, ['VALUE_21','VALUE_22','VALUE_23','VALUE_24','Urban']) as cursor:
            for row in cursor:
                urbansum = sum(row[0:4]) #sum the first 4 values, all the urban land areas
                row[4] = urbansum
                cursor.updateRow(row)

        #add a new field for the sum of all the natural land types
        arcpy.AddField_management(tablename, "Natural", "FLOAT")

        #update the natural field with sum of all natural land types
        with arcpy.da.UpdateCursor(tablename, ['VALUE_31','VALUE_41','VALUE_42','VALUE_43','VALUE_52','VALUE_71','VALUE_90','VALUE_95','Natural']) as cursor:
            for row in cursor:
                naturalsum = sum(row[0:8])
                row[8] = naturalsum
                cursor.updateRow(row)

        #add a new field for sum of farm land types
        arcpy.AddField_management(tablename, "Farm", "FLOAT")

        #update the farm field with sum of all farm land types
        with arcpy.da.UpdateCursor(tablename, ['VALUE_81','VALUE_82','Farm']) as cursor:
            for row in cursor:
                farmsum = sum(row[0:2])
                row[2] = farmsum
                cursor.updateRow(row)

        #add a new field for sum of area
        arcpy.AddField_management(tablename, "AreaTotal", "FLOAT")

        #update the area total field with sum of water, plus different land types calculated already
        with arcpy.da.UpdateCursor(tablename, ['VALUE_11','Urban','Natural','Farm','AreaTotal']) as cursor:
            for row in cursor:
                areasum = sum(row[0:4])
                row[4] = areasum
                cursor.updateRow(row)

        #add new field for percent urban
        arcpy.AddField_management(tablename, "UrbanPer", "FLOAT")

        #add new field for percent natural
        arcpy.AddField_management(tablename, "NaturalPer", "FLOAT")

        #add new field for percent farm
        arcpy.AddField_management(tablename, "FarmPer", "FLOAT")

        #update all the percent fields with land type area/total area
        with arcpy.da.UpdateCursor(tablename,['Urban','Natural','Farm','AreaTotal','UrbanPer','NaturalPer','FarmPer']) as cursor:
            for row in cursor:
                urbanper = row[0]/row[3]
                naturalper = row[1]/row[3]
                farmper = row[2]/row[3]
                row[4] = urbanper
                row[5] = naturalper
                row[6] = farmper
                cursor.updateRow(row)

    #This section is for 1992 only
    else:

        #add a new field for the sum of all the urban land types
        arcpy.AddField_management(tablename, "Urban", "FLOAT")

        #update the urban field with the sum of all the urban land types
        with arcpy.da.UpdateCursor(tablename, ['VALUE_21','VALUE_22','VALUE_23','VALUE_85','Urban']) as cursor:
            for row in cursor:
                urbansum = sum(row[0:4]) #sum the first 4 values, all the urban land areas
                row[4] = urbansum
                cursor.updateRow(row)

        #add a new field for the sum of all the natural land types
        arcpy.AddField_management(tablename, "Natural", "FLOAT")

        #update the natural field with sum of all natural land types
        with arcpy.da.UpdateCursor(tablename, ['VALUE_41','VALUE_42','VALUE_43','VALUE_91','VALUE_92','Natural']) as cursor:
            for row in cursor:
                naturalsum = sum(row[0:5])
                row[5] = naturalsum
                cursor.updateRow(row)

        #add a new field for sum of farm land types
        arcpy.AddField_management(tablename, "Farm", "FLOAT")

        #update the farm field with sum of all farm land types
        with arcpy.da.UpdateCursor(tablename, ['VALUE_81','VALUE_82','Farm']) as cursor:
            for row in cursor:
                farmsum = sum(row[0:2])
                row[2] = farmsum
                cursor.updateRow(row)

        #add a new field for sum of area
        arcpy.AddField_management(tablename, "AreaTotal", "FLOAT")

        #update the area total field with sum of water and rock, plus different land types calculated already
        with arcpy.da.UpdateCursor(tablename, ['VALUE_11','VALUE_32','VALUE_33','Urban','Natural','Farm','AreaTotal']) as cursor:
            for row in cursor:
                areasum = sum(row[0:6])
                row[6] = areasum
                cursor.updateRow(row)

        #add new field for percent urban
        arcpy.AddField_management(tablename, "UrbanPer", "FLOAT")

        #add new field for percent natural
        arcpy.AddField_management(tablename, "NaturalPer", "FLOAT")

        #add new field for percent farm
        arcpy.AddField_management(tablename, "FarmPer", "FLOAT")

        #update all the percent fields with land type area/total area
        with arcpy.da.UpdateCursor(tablename,['Urban','Natural','Farm','AreaTotal','UrbanPer','NaturalPer','FarmPer']) as cursor:
            for row in cursor:
                urbanper = row[0]/row[3]
                naturalper = row[1]/row[3]
                farmper = row[2]/row[3]
                row[4] = urbanper
                row[5] = naturalper
                row[6] = farmper
                cursor.updateRow(row)

###############################################################################################
## Section 3
## This section finds the mean center of urban land types in each county for each raster.
## The output of this section is two point feature classes for each county for each year.
## One is the mean center of all urban land typs. The other is a class with a separate point
## for each different urban land type. Also, a text file is created summarizing the results.
## Its contents are a table with the distance from the mean center of urban areas to downtown DC
## for each county for each year.
## Output (ABBR is the county name abbreviation):
##      Mean center of all urban land types FC: ABBR_MeanCenterUrban_year
##      Mean centers of each urban land type FC: ABBR_MeanCenterUrbanTypes_year
##      Results File: Results_Distances.txt
## Also created, but not main output:
##      Raster of just urban land types for each county for each year: ABBR_UrbRaster_year
##      Points features class of all all urban land points: ABBR_urbanpoints_year
##      Table showing distance from urban mean center to downtown DC: ABBR_DistUrb_year


print "Starting Section 3: Calculate Urban Land Types Mean Centers and Distances to Downtown"

#create the output results file
filename = wkspgdb + r'\Results_Distances.txt'
f = open(filename, 'a')
f.write("Distances to Downtown DC in meters\n\t")


##First, we get all the county abbreviations from the counties feature class so that we can
##loop through the counties individually, and we also use the abbreviations to append to new
##file names.

#start with empty list
county_names = []

#use search cursor to loop through counties feature class and extract all name abbreviations
#we also make a feature layer for each county
with arcpy.da.SearchCursor(counties, ['ABBR']) as cursor:
    for row in cursor:
        county = row[0]
        #append name to list
        county_names.append(county)
        #make the feature layer
        #feature layer name is "county_lyr", SQL expression is " ABBR = 'county' "
        arcpy.MakeFeatureLayer_management(counties, county + "_lyr", " ABBR = '" + county + "'")
        #also, write county name to results file as header for the results table
        f.write("%s\t" % county)
        

#This is a list of lists, storing all distances of mean centers of urban land types.
#They are created below and added to the table, the table is printed to file later
distances_array = []

#we also create a list of all the years, used in the next section
year_list = []

#now loop through all the rasters 
for raster in raster_list:
    #get the year string from the raster name so we can append to new file names
    year = raster[-8:-4]
    year_list.append(year)
    print "Starting: " + year

    #create list of distances to downtown DC that are calculated below
    #the first element will be the year
    distance_list = [int(year)]

    #loop through each county
    for county in county_names:
        print "Processing: " + county
        #extract the raster cells in the individual county layer to a new raster with ExtractByMask
        outMaskRaster = arcpy.sa.ExtractByMask(raster, county + "_lyr")
        #extract all points of urban land types
        outAttrRaster = arcpy.sa.ExtractByAttributes(outMaskRaster, '(VALUE >= 21 AND VALUE <= 24) OR VALUE = 85')
        #save the extracted raster to the geodatabase, we use it in the nect section
        outAttrRaster.save(wkspgdb + '\\' + county + "_UrbRaster_" + year)
        #convert raster to points
        urbanPointsFC = wkspgdb + '\\' + county + "_urbanpoints_" + year #output feature class name
        arcpy.RasterToPoint_conversion(outAttrRaster, urbanPointsFC)
        #calculate mean center of all urban areas, and create point feature class
        meanCenterFC = wkspgdb + '\\' + county + "_MeanCenterUrban_" + year
        arcpy.MeanCenter_stats(urbanPointsFC, meanCenterFC)
        #calculate mean centers of each urban area land type, the case field is "grid_code",
        #the field created by raster to point conversion that has the land type value in it
        meanCenterTypesFC = wkspgdb + '\\' + county + "_MeanCenterUrbanTypes_" + year
        arcpy.MeanCenter_stats(urbanPointsFC, meanCenterTypesFC, Case_Field="grid_code")

        #now calculate distance from the urban mean center to downtown DC
        distance_table = wkspgdb + '\\' + county + "_DistUrb_" + year
        arcpy.PointDistance_analysis(meanCenterFC, downtown, distance_table)

        #get the distance out of the created distance table with a search cursor
        with arcpy.da.SearchCursor(distance_table, ['DISTANCE']) as cursor:
            for row in cursor:
                #append distance to list, append as int because we don't care about decimal meters
                distance_list.append(int(row[0]))

        #calculate the distance from the mean center of each urban type to downtown DC
        distanceTypes_table = wkspgdb + '\\' + county + "_DistUrbTypes_" + year
        arcpy.PointDistance_analysis(meanCenterTypesFC, downtown, distanceTypes_table)

    #after the county loop is completed, the distance list includes a distance for each
    #county for the current year, this list is appended to the distance table list
    distances_array.append(distance_list)
    
        
#now print the distance array to a file
f.write("\n")
for distance_list in distances_array:
    for distance in distance_list:
        f.write("%d\t" % distance)
    f.write("\n")
f.close()

print "Results File Created: %s" %filename

####################################################################################
## Section 4
## This section creates a new raster for each county for each year (besides the first year) that shows the
## areas that are now urban that were not urban in the previous year's raster. It uses the county urban rasters
## created in the last section. The output rasters provide the user with a visual of the change in urban areas
## over time. A similar method to the last section could be applied on these to find the mean centers.
## Output raster name: ABBR_UrbChange_year

print "Starting Section 4: Create Change Rasters"

#we use this format so we can use the raster from one year and the previous year to find the change
#it starts with 1 and not 0 because we can't find the new urban areas in the first year
for i in range(1,len(year_list)):
    print "Starting: %s" % year_list[i]
    
    for county in county_names:
        print "Processing: %s" % county
        #create raster object for the county raster for the current year
        newRaster = arcpy.Raster(wkspgdb + '\\' + county + "_UrbRaster_" + year_list[i])
        #raster object for the previous year
        oldRaster = arcpy.Raster(wkspgdb + '\\' + county + "_UrbRaster_" + year_list[i-1])

        #Use conditional statement to create the change raster.
        #The conditional is that the new raster is not null (meaning the cell is urban),
        #and that the old raster is null (meaning not urban). The cells that are newly urban
        #get value 1 and and the cells that are not newly urban are null.
        changeRaster = arcpy.sa.Con(~arcpy.sa.IsNull(newRaster) & arcpy.sa.IsNull(oldRaster),1)
        #save the raster, name is County_UrbChange_year
        changeRaster.save(wkspgdb + '\\' + county + "_UrbChange_" + year_list[i])
    

print "---Script Complete---"
