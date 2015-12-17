# -*- coding: utf-8 -*-
##########################################################################
##########################################################################
### 
### Chicago Crime Analysis - With Sporting Event Data
### Amjad Khan 
### this version: 2015-12-16
### 
########################################################################
########################################################################

############   For Submission Purposes: 
##
## To go through the code, the ideal approach is to run the thee code blocks
## as given by the #%% break-points 
## Best way to test the code out is 
## to delete G:\Share\GEOG6293_Programming\Khan\FinalProject\Ghicago.gdb and start from scratch



#%%
#######################################################################
####   Initializing
#######################################################################

# libraries required
import math
import numpy as np
import pandas as pd
import arcpy
import os

# setting directories
projdir = r'G:\Share\GEOG6293_Programming\Khan\FinalProject'
datadir = r'G:\Share\GEOG6293_Programming\Khan\FinalProject\Data'


#%%
#######################################################################
####   Making separate (readable) csvs's with data for each year   
#######################################################################

# This function is for getting the data into a usable format
# given memory limits that i'm running into
# The code takes relevant columns  from the large ChicagoCrimes.csv, 
# accesses it using chunks and extracts 

def yearlycsvs():    
    for year in range(2002,2015):
        # read in the large csv through chunk iterator
        csv_data = pd.read_csv(datadir +r'\ChicagoCrimes.csv',low_memory=False, index_col="id", usecols=["id", "datetime", "date", "year", "primarytype","domestic","arrest","block", "description", "locationdescription","beat", "district","ward","communityarea", "latitude", "longitude"],chunksize=200000) #do we want here?
        # create an empty dataframe for each year with the column headers from csv
        df = csv_data.get_chunk(0)
        count = 0
        # loop through chunk iterator to get all the data for each year
        for chunk in csv_data:
            print type(chunk), chunk.size
            # create a field to identify the current year being iterated through
            # and add that to the df
            currentyear  = chunk['year']==year
            df = df.append(chunk[currentyear], ignore_index=False)
            count += 1
            print "Year:", year, "Iteration Number:",count         
        # save csv for each year once
        df.to_csv(datadir + "CC" + str(year) + ".csv")    
        print "Year done:", year    
    print "All CSV's done"


# calling the function above below:
# the funtion call has been commented out because it only has to be run once to 
# get the required csvs, and it takes a while to execute:

#yearlycsvs()


#%%
#######################################################################
####   Getting Census Tract Data
#######################################################################

# This part of the script takes the US census tract data for 2010
# and clips out the data for Chicago

# Set current directory
os.chdir(projdir)

# check if Chicago.gdb alread exists, otherwise create one
if not(os.path.isdir("Chicago.gdb")):
    arcpy.CreateFileGDB_management(projdir, "Chicago")
else:
    print "Chicago.gdb already exists."

arcpy.env.workspace = os.path.join(projdir,"Chicago.gdb")

# Clip the part of US tract data that falls within Chicago boundaries
if not(arcpy.Exists('ChicagoTractData')):
    arcpy.Clip_analysis(datadir+r'\US_Census_Tracts\Profile-County_Tract.gdb\Tract_2010Census_DP1',datadir+r'\ChicagoBoundaries_CensusTracts-2010\CensusTractsTIGER2010.shp',"ChicagoTractData")
else:
    print "Feature class ChicagoTractData already Exists in Chicago.gdb."

spref = arcpy.Describe("ChicagoTractData").spatialReference
arcpy.ListFeatureClasses()


#%%
#################################
###   Stadium point data 
############################

# United Center: NBA Bulls, NHL Black Hawks (41.880716, -87.674604)
# Soldier Field: NFL Bears (41.862265, -87.616638)
# Cellular Field: Baseball White Sox (41.830009, -87.633773)
# Wrigley Field: Baseball Cubs (41.947454, -87.656134)

rowValues = [["nba",(-87.674604, 41.880716)],["nhl",(-87.674604, 41.880716)],["nfl",(-87.616638, 41.862265)],["sox",(-87.633773, 41.830009)], ["cubs",(-87.656134, 41.947454)]]

arcpy.CreateFeatureclass_management(arcpy.env.workspace, "Stadiums", "POINT", spatial_reference = spref)
arcpy.AddField_management("Stadiums", "NAME", "TEXT")
    
with arcpy.da.InsertCursor("Stadiums", ["NAME","SHAPE@XY"]) as iCur:
    for row in rowValues:
        iCur.insertRow(row)

del iCur


#%%
#########################################################
###   Distance from Tract Centroids to Stadiums
#######################################################

# Create a layer of centroid of each tract

arcpy.FeatureToPoint_management("ChicagoTractData", "TractCentroids", "CENTROID")

keep = ['OBJECTID']  
  
discard = []  
for field in [f.name for f in arcpy.ListFields("TractCentroids") if f.type<>"Geometry"]:   
    if field not in keep: 
        discard.append(field)
arcpy.DeleteField_management("TractCentroids", discard)  
     

# Haversine distance function
# takes two arrays A and B in the format (long, lat) as input 
# and returnss the distance in meters beween the two

def haversinedist(A,B):
        lat_home = math.radians(float(A[1]))
        lon_home = math.radians(float(A[0]))
        
        # Get input of coordinates for ""destination"
        lat_dest = math.radians(float(B[1]))
        lon_dest = math.radians(float(B[0]))
        
        #Calculate distance between the two (Haversine Formula), in meters: 
        dlat = abs(lat_dest - lat_home)
        dlon = abs(lon_dest - lon_home)
        a = (math.sin(dlat / 2.0))**2 + math.cos(lat_home) * math.cos(lat_dest) * (math.sin(dlon/2.0))**2
        b = 2 * math.atan2(math.sqrt(a),math.sqrt(1-a))
        c = 6371 * b *1000 
        return c

# Use the hversinedist function to calculate the distance of each centroid
# to each of the stadiums.
# This adds a field for distance to each stadium field in the
# (not sure how to do this in arcpy directly, might be reinventing the wheel here.

rowValues = [["nba",(-87.674604, 41.880716)],["nhl",(-87.674604, 41.880716)],["nfl",(-87.616638, 41.862265)],["sox",(-87.633773, 41.830009)], ["cubs",(-87.656134, 41.947454)]]
for stadium in rowValues:
    arcpy.AddField_management("TractCentroids", stadium[0]+"Distance", "FLOAT")
    with arcpy.da.UpdateCursor("TractCentroids", [stadium[0]+"Distance", "SHAPE@XY"]) as cur:
        for row in cur:
            row[0] = haversinedist(stadium[1],row[1])
            cur.updateRow(row)
        cur.reset()

del cur

# Add the distance of stadiums to centroid fields back into the tract layer.
# and delete unnecessary temp files used above

arcpy.SpatialJoin_analysis("ChicagoTractData","TractCentroids","tractswithdistance","JOIN_ONE_TO_ONE","KEEP_ALL","","CONTAINS")

arcpy.Delete_management("ChicagoTractData") 
arcpy.Rename_management("tractswithdistance", "ChicagoTractData") 
arcpy.Delete_management("tractswithdistance") 

# ChicagoTractData now has the distances to the centroid of each polygon

#%%
#######################################################################
####   Formatting the crime data for use
#######################################################################

# for now, I will work with a random sample of the 2010 data only
# for copmutational tractability
csvdata = pd.read_csv(datadir +"\CC2010.csv", index_col="id")
sample2010 = csvdata.sample(frac=0.1, random_state=15200)

# Converting date to to datetime format
sample2010.dtypes
pd.to_datetime(sample2010.date,format='%d%b%Y')

sample2010['primarytype'].value_counts()
csvdata['primarytype'].value_counts()
pd.crosstab(csvdata['primarytype'],csvdata['domestic'])


# creating fields for broader crime classifications
# to be used for aggregation by tract after the point to polygon spatial join

sample2010['count'] = 1 

sample2010['violent'] = np.where((sample2010['primarytype']=='BATTERY')| (sample2010['primarytype']=='ASSAULT') | (sample2010['primarytype']=='BATTERY') | (sample2010['primarytype']=='ROBBERY') | (sample2010['primarytype']=='KIDNAPPING') | (sample2010['primarytype']=='HOMICIDE') | (sample2010['primarytype']=='INTIMIDATION') | (sample2010['primarytype']=='CRIM SEX ASSAULT'), 1, 0)
pd.crosstab(sample2010['primarytype'],sample2010['violent'])

sample2010['theft'] = np.where((sample2010['primarytype']=='THEFT')| (sample2010['primarytype']=='BURGLARY')| (sample2010['primarytype']=='MOTOR VEHICLE THEFT')| (sample2010['primarytype']=='ROBBERY'), 1,0)
pd.crosstab(sample2010['primarytype'],sample2010['theft'])

sample2010['substance'] = np.where((sample2010['primarytype']=='NARCOTICS')| (sample2010['primarytype']=='LIQUOR LAW VIOLATION') , 1,0)
pd.crosstab(sample2010['primarytype'],sample2010['substance'])

sample2010['damage'] = np.where((sample2010['primarytype']=='CRIMINAL DAMAGE')| (sample2010['primarytype']=='ARSON') , 1,0)
pd.crosstab(sample2010['primarytype'],sample2010['damage'])

sample2010['trespass'] = np.where((sample2010['primarytype']=='BURGLARY')| (sample2010['primarytype']=='CRIMINAL TRESPASS'), 1,0)
pd.crosstab(sample2010['primarytype'],sample2010['trespass'])

sample2010['other'] = np.where((sample2010['primarytype']=='OTHER OFFENSE')| (sample2010['primarytype']=='STALKING'), 1,0)
pd.crosstab(sample2010['primarytype'],sample2010['other'])

sample2010['deceit'] = np.where((sample2010['primarytype']=='DECEPTIVE PRACTICE'), 1,0)
pd.crosstab(sample2010['primarytype'],sample2010['deceit'])

sample2010['publicpeace'] = np.where((sample2010['primarytype']=='PUBLIC PEACE VIOLATION')| (sample2010['primarytype']=='INTERFERENCE WITH PUBLIC OFFICER') | (sample2010['primarytype']=='INTIMIDATION')| (sample2010['primarytype']=='OBSCENITY')| (sample2010['primarytype']=='PUBLIC INDECENCY') | (sample2010['primarytype']=='WEAPONS VIOLATION'), 1,0)
pd.crosstab(sample2010['primarytype'],sample2010['publicpeace'])

sample2010['sex'] = np.where((sample2010['primarytype']=='PROSTITUTION')| (sample2010['primarytype']=='SEX OFFENSE') | (sample2010['primarytype']=='CRIM SEX ASSAULT'), 1,0)
pd.crosstab(sample2010['primarytype'],sample2010['sex'])

sample2010['gambling'] = np.where((sample2010['primarytype']=='GAMBLING'), 1,0)
pd.crosstab(sample2010['primarytype'],sample2010['gambling'])

sample2010.to_csv(datadir + "\SampleCC" + str(2010) + ".csv")


#%%
#######################################################################
####   Joining the crime data to tracts (one to many)
#######################################################################

# Use the created sample CSV to create a layer of point data
###### this takes a while, so please bear with it

currentyear = str(2010)
arcpy.MakeXYEventLayer_management(datadir +"\sampleCC"+currentyear+".csv", 'longitude', 'latitude', 'eo1', spref)
arcpy.CopyFeatures_management("eo1", "CrimeData"+currentyear)
# and close out
arcpy.Delete_management("eo1")


#%%
###### this also takes a while, so please bear with it
# a one to many join of each tract to all crimes within a 500m radius
arcpy.SpatialJoin_analysis("ChicagoTractData","CrimeData"+currentyear,"tractswithcrimes","JOIN_ONE_TO_MANY","KEEP_ALL","","WITHIN_A_DISTANCE","200 meters")


#############################################################
# So far, the "tractswithcrime" feature has all the data I want
# and that is what needs to be further manipulated
#######################################################

#%%

'''
## This is the last part of the code I got stuck with ##


#######################################################################
####   Bringing Feature Class data into pandas
#######################################################################

arcpy.env.workspace = os.path.join(projdir,"Chicago.gdb")
arcpy.ListFeatureClasses()



# This line of code won't work due to memory issues. 
# Would need 64 bit python, which is probably incompatible with ArcMap, unfortunately
fc_np = arcpy.da.FeatureClassToNumPyArray("tractswithcrimes", ['OBJECTID','GEOID10', 'NAMELSAD10', 'ALAND10', 'AWATER10', 'INTPTLAT10', 'INTPTLON10', 'nbaDistance', 'nhlDistance', 'nflDistance', 'soxDistance', 'cubsDistance', 'id', 'datetime', 'date', 'year', 'primarytype', 'domestic', 'arrest', 'latitude', 'longitude', 'Shape_Length', 'Shape_Area'], skip_nulls=False, null_value=-9999)

# So instead

# Export Attribute Table to CSV and read it back into a dataframe
arcpy.ExportXYv_stats("tractswithcrimes", "*", "COMMA", datadir+r'tractswithcrimescsv', "ADD_FIELD_NAMES")

'''

#######################################################################
####   What's Next? 
#######################################################################

### then collapse the dataframe, once obtained, by date and tract
### then merge, by date, for weather and sports data
### then we'll have the data in a panel format, and normalization by population, etc
### Finally the regression analysis


