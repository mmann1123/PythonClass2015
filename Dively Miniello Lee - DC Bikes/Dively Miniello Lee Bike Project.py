# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 17:49:41 2015

@author: cdively
"""
########################################################################################################################
#  Authors: Chris Dively, Sue Lee and Veronica Miniello
# Description: This is a script to read in and manipulate a large CSV file containing records of departures from
#   Capital BikeShare stations in 2012 as Pandas Dataframes.  It reads in data from the CSV, selects departures in the morning and afternoon, 
#   On this selection, it aggregates the morning and afternoon departures by the station name, and gives a count of
#   Departures for each station.
#  
#   After finding the count of departures for each station, it finds the top quartile for each (morning and afternoon) and stores that as a variable
#   Next it copies the pandas dataframs as new CSV files.
#
#   Using the selected Morning stations and Afternoon Stations CSV files, it copies the CSVs into the BikeShareProject.gdb as tables,
#   And Joins the tables to a BikeShare Station Point Shapefile.
#   
#   After the Join Operation is complete, it selects by attributes the stations with the top quartile for both morning and afternoon, 
#   Copies the Selections as New Layers
#
#   Next it Selects By Location on the Top25PCT layers that fall within different buffer regions of Metro Stations, .25 Mile, .5 Mile and 1 Mile
#
#   It then prints out the count of how many features fall within the buffer regions (this could have been done without the buffer, but I liked
#   Having the visual references).
#
# Caveat: The script is clunky, memory intensive and inefficent.  I could have written it much more elegantly. 
#   Please wait for a little while for the script to complete
#   See "Variable Explorer" in Spyder to see variables created
#   The Cells are for my sanity when testing the script. You can run it as a single block.
#######################################################################################################################

import pandas as pd
import arcpy
from pandas import read_csv

# Set ARcpy Workspace and tell arcpy to overwrite outputs
arcpy.env.workspace = r"G:\Research\Bike_share_project\BikeShareProject.gdb"
arcpy.env.overwriteOutput = True

# read CSV using pandas as a Pandas Dataframe.
q3_2012 = read_csv(r'G:\Research\Bike_share_project\spreedsheet_data\2012-Q3-Trips-History-Data.csv')

# This was the part you helped with.  Treats the "Start Date" column of the dataframe as a string, splits it at the space between Day and Time.
str(q3_2012['Start date'][0])

str.split( str(q3_2012['Start date'][0]),' ' )[1]

#Creates an new column "Year", sets that value to 0, creates an empty list a that will be used in the For loop.

q3_2012['year'] = 0
a = list()
# For Loop over the entire dataframe (which is huge), splits the column at the space, appends the result, just the Time from the split, to the list "a"
for i in range(0,636683):
    splitted = str.split( str(q3_2012['Start date'][i]),' ' )
    a.append(splitted[1])
# Creates new column "Time"
q3_2012['Time']= ""
# Fills in the values of A as "time" 
q3_2012['Time'] = a
# Sorts the colmns by the Start Station (did this so I could look at it)
q3_2012.sort(columns='Start Station')

# OK this ia really ugly way to accomplish what could be done in 1 second with an SQL expression. 
# I subsequently learned that pandas can parse SQL quereys with "pandas.read_sql_query(querey here)" 
# but there's no way in hell I'm rewriting it at this point.
 
# Creates variable "Morning" that is all the times that are >= 0630
morning=q3_2012[q3_2012['Time'] >= '6:30']
# Further cuts down on "Morning" by selecting only the departures that are before 0930
# the result is Morning2 which are departures between 0630 and 0930
morning2=morning[morning['Time'] <= '9:30']
# Does the same thing with Afternoon, results with 'afternoon2' that is all departures between 1630 and 1900
afternoon=q3_2012[q3_2012['Time'] >= '16:30']
afternoon2=afternoon[afternoon['Time'] <= '19:00']

# delete unneeded columns from morning2 and afternoon2, results with "thin" dataframes.  Get it?
afternoonthin = afternoon2.drop (['Duration', 'End date' , 'End Station', 'Bike#' , 'Subscriber Type', 'year'], axis=1)
morningthin = morning2.drop (['Duration', 'End date' , 'End Station', 'Bike#' , 'Subscriber Type', 'year'], axis=1)

#%%
#create columns "count', sets the value 1 for all the records
afternoonthin['count'] = 1
morningthin['count'] = 1

#%%
# Creates variables afternooncount and morningcount, grooping the "thin" variables by 'Start Station' and summing the 'Count' column.
afternooncount = afternoonthin.groupby (['Start Station']) ['count'].sum()
morningcount = morningthin.groupby (['Start Station']) ['count'].sum()

#%%
# creates variables that contain the number for the top 25% of each, morncount and afternooncount
morntopquarter = morningcount.quantile(.75)
afttopquarter = afternooncount.quantile(.75)


#%%
#Writes afternnoncount and morningcount to new CSVs
afternooncount.to_csv(r"G:\Research\Bike_share_project\spreedsheet_data\aftcount.csv")

morningcount.to_csv(r"G:\Research\Bike_share_project\spreedsheet_data\morncount.csv")
#%%

# Copies the aftcount and morncount CSVs to the Geodatabase as geodatabase tables
arcpy.CopyRows_management (r"G:\Research\Bike_share_project\spreedsheet_data\morncount.csv", "G:\Research\Bike_share_project\BikeShareProject.gdb\MorningDepartures")

arcpy.CopyRows_management (r"G:\Research\Bike_share_project\spreedsheet_data\aftcount.csv", "G:\Research\Bike_share_project\BikeShareProject.gdb\AftDepartures")

#%%
# Makes a Featurelayer for the existing Bikeshare stations FeatureClass, calls it Mornstations
arcpy.MakeFeatureLayer_management ("BikeShareStations", "MornStations")
# Joins "MorningDepartures" to the temp FeatueLayer based on the "Address" field
arcpy.AddJoin_management ("MornStations", "Address" , "MorningDepartures", "Field1", "")
# Copies the Temp FeatureLayer to a real FeatureClass "MorningBikeshareDepartures"
arcpy.CopyFeatures_management ("Mornstations", "MorningBikeshareDepartures")

#%%
# Does the same as above for the Afternoon stations
arcpy.MakeFeatureLayer_management ("BikeShareStations" , "AfternoonStations")
arcpy.AddJoin_management ("AfternoonStations", "Address", "AftDepartures", "Field1", "")
arcpy.CopyFeatures_management ("AfternoonStations" , "AftBikeshareDepartures")

#%%
# Makes 2 Temp FeatureLayers, Morning and Afternoon
arcpy.MakeFeatureLayer_management ("MorningBikeshareDepartures" , "MornSelectLyr")
arcpy.MakeFeatureLayer_management ("AftBikeshareDepartures", "AftSelectLyr")
# Prints the top quartiles for both the morning and afternoon (for reference only, the value is already baked into the script, I didn't
# want to risk arcpy not being able to handle my sql expression with a derived value).  Some people call that cheating.
# I call it setting myself up for success
print morntopquarter
print afttopquarter
# Selects Morning and Afternoon layers where Field2 (the departure time) is greater than the top quartile value
# Exports the selections as new real layers.
arcpy.SelectLayerByAttribute_management ("MornSelectLyr" , "NEW_SELECTION", '  "MorningDepartures_Field2" > 845.75  ')
arcpy.CopyFeatures_management ("MornSelectLyr" , "MornTop25PCT")
arcpy.SelectLayerByAttribute_management ("AftSelectLyr" , "NEW_SELECTION" , '  "AftDepartures_Field2" >= 1299.75  ')
arcpy.CopyFeatures_management ("AftSelectLyr" , "AftTop25PCT")


#%%
# Creates a .25 mile buffer around each Metro Entrance
arcpy.MakeFeatureLayer_management ("Metro_Stations_Regional" , "MetroEntrancelyr")
arcpy.Buffer_analysis ("MetroEntrancelyr" , "MetroRegEntranceBuff" , ".25 Miles" , "FULL", "ROUND", "NONE" , "")

#%%
# First Select operation.  This creates temp feature classes for MorningTop25, AfternoonTop25 and MetroEntrance Buffer
arcpy.MakeFeatureLayer_management ("MornTop25PCT" , "MornTopPCTLyr")
arcpy.MakeFeatureLayer_management ("AftTop25PCT" , "AftTopPCTLyr")
arcpy.MakeFeatureLayer_management ("MetroRegEntranceBuff", "MetroBufferLyr")
# For MorningTopPCT and AfternoonTopPCt, selects by location where they intersect with the .25 mile metro entrance buffer
# exports the result as MornTopPCTMetro, AftTopPCTMetro
arcpy.SelectLayerByLocation_management ("MornTopPCTLyr" , "INTERSECT", "MetroBufferLyr" , "" , "NEW_SELECTION")
arcpy.CopyFeatures_management ("MornTopPCTLyr", "MornTopPCTMetro")
arcpy.SelectLayerByLocation_management ("AftTopPCTLyr" , "INTERSECT" , "MetroBufferLyr", "",  "NEW_SELECTION" )
arcpy.CopyFeatures_management ("AftTopPCTLyr" , "AftTopPCTMetro")

#%%
# Creates variables for the Count of Total stations in morning Top25PCT and MornTop25PCT within the .25 mile metro buffer
MornTotalCount = arcpy.GetCount_management ("MornTop25PCT")
MornCountQuarterMile = arcpy.GetCount_management ("MornTopPCTMetro")
#%%
# Creates the same variables as above, but for the Afternoon
AftTotalCount = arcpy.GetCount_management ("AftTop25PCT")
AftCountQuarterMile = arcpy.GetCount_management ("AftTopPCTMetro")

#%%
# Second buffer, Buffers .5 miles around the metro stations, creates new MetroEntranceBIG buffer zones
arcpy.MakeFeatureLayer_management ("Metro_Stations_Regional" , "MetroEntrancelyrBIG")
arcpy.Buffer_analysis ("MetroEntrancelyr" , "MetroRegEntranceBuffBIG" , ".5 Miles" , "FULL", "ROUND", "NONE" , "")
#%%
# Third buffer, Buffers 1 whole mile around the Metro Stations, creates Metro Stations EXTRA buffer zones
arcpy.MakeFeatureLayer_management ("Metro_Stations_Regional" , "MetroEntrancelyrEXTRA")
arcpy.Buffer_analysis ("MetroEntrancelyr" , "MetroRegEntranceBuffEXTRA" , "1 Miles" , "FULL", "ROUND", "NONE" , "")

#%%
# Second select operation. .5 Miles. Creates TempFeatureLayers for MorningTop25, AfternoonTop25 and MetroBufferBIG (.5 miles)
arcpy.MakeFeatureLayer_management ("MornTop25PCT" , "MornTopPCTLyrBIG")
arcpy.MakeFeatureLayer_management ("AftTop25PCT" , "AftTopPCTLyrBIG")
arcpy.MakeFeatureLayer_management ("MetroRegEntranceBuffBIG", "MetroBufferLyrBIG")

#For morning and afternoon temp FeatureLayers, selects where they intersect with the BIG metro buffer (.5 miles), exports each selection
# as a new FeatureClass

arcpy.SelectLayerByLocation_management ("MornTopPCTLyrBIG" , "INTERSECT", "MetroBufferLyrBIG" , "" , "NEW_SELECTION")
arcpy.CopyFeatures_management ("MornTopPCTLyrBIG", "MornTopPCTMetroBIG")
arcpy.SelectLayerByLocation_management ("AftTopPCTLyrBIG" , "INTERSECT" , "MetroBufferLyrBIG", "",  "NEW_SELECTION" )
arcpy.CopyFeatures_management ("AftTopPCTLyrBIG" , "AftTopPCTMetroBIG")

#%%
# Gets the count for how manystations fall within the .5 mile buffer for morning and afternoon, creates a variable for each
MornCountHalfMile = arcpy.GetCount_management ("MornTopPCTMetroBIG")
AftCountHalfMile = arcpy.GetCount_management ("AftTopPCTMetroBIG")

#%%
# Third Select operation, 1 mile.  Creats 3 temp FeatureLayers, Morning,afternoon and MetroEntranceEXTRA (1 mile)
arcpy.MakeFeatureLayer_management ("MornTop25PCT" , "MornTopPCTLyrEXTRA")
arcpy.MakeFeatureLayer_management ("AftTop25PCT" , "AftTopPCTLyrEXTRA")
arcpy.MakeFeatureLayer_management ("MetroRegEntranceBuffEXTRA", "MetroBufferLyrEXTRA")

# For afternoon and morning temp feature layers, selects where they intersect with the 1 mile metro station buffer

arcpy.SelectLayerByLocation_management ("MornTopPCTLyrEXTRA" , "INTERSECT", "MetroBufferLyrEXTRA" , "" , "NEW_SELECTION")
arcpy.CopyFeatures_management ("MornTopPCTLyrEXTRA", "MornTopPCTMetroEXTRA")
arcpy.SelectLayerByLocation_management ("AftTopPCTLyrEXTRA" , "INTERSECT" , "MetroBufferLyrEXTRA", "",  "NEW_SELECTION" )
arcpy.CopyFeatures_management ("AftTopPCTLyrEXTRA" , "AftTopPCTMetroEXTRA")

#%%
# Gets the count of top 25% Morning and Afternoon departures that fall within 1 mile of a metro station, creates a variable for each
MornCountMile = arcpy.GetCount_management ("MornTopPCTMetroEXTRA")
AftCountMile = arcpy.GetCount_management ("AftTopPCTMetroEXTRA")
#%%
# Prints results.
print "For BikeShare stations with morning departures, %r stations make up the top quarter of all departures." %MornTotalCount
print "For BikeShare Stations with afternoon departures, %r stations make up the top quarter of all departures." %AftTotalCount
print "\n"
print "Of the %r top Morning Departure stations, %r of them are within 1 mile of a Metro station." % (MornTotalCount , MornCountMile)
print "%r of them are within Half a mile. \n %r of them are within a quarter of a mile of a metro station" % (MornCountHalfMile, MornCountQuarterMile)
print "\n"
print "Of the %r top Afternoon Depattures, %r are within 1 mile \n, %r are within half a mile and %r are within a quarter mile of a metro station" % (AftTotalCount, AftCountMile, AftCountHalfMile, AftCountQuarterMile)
print "Script Complete!"
