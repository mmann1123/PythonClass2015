# -*- coding: utf-8 -*-

## Kady Gerry
## Geog 6392
## Project: Step 2
## Load csv files and analyze data

#### This script will merge all of the .csv files output by the API script into one large .csv file
#### and rename the columns to something ArcGIS will like. The column names could have been defined
#### in the first step, but since the API call process was running I just left it alone.

import os
import fnmatch
import pandas as pd

## The file path where all the data is stored. Originally I stored it on my hard drive so I wouldn't
## have to worry about Citrix connections or anything. I moved all the data to the G: drive.

#filePath = r'C:\Users\Kady\Documents\GIS Programming\Project\Data'
filePath = r'G:\Share\GEOG6293_Programming\Gerry\Project\Data'

## Create a list of all .csv files stored in the file path (.csv files were created in the previous script)
csvFiles = []

for root, dirs, filenames in os.walk(filePath):
    for filename in fnmatch.filter(filenames, '*.csv'):
        csvFiles.append([filename,os.path.join(root, filename)])

print "All .csv files identified"

## Create a single data frame for all data in the csv files
allData = pd.DataFrame()

## Iterate through all of the csv files and append the data the allData data frame
for i in range(len(csvFiles)):
    nextDF = pd.DataFrame()
    nextDF = pd.read_csv(csvFiles[i][1])
    allData = allData.append(nextDF)


## Rename the fields of the data frame (because some are too long for Arc or have spaces)
allData = allData.rename(columns = {'Brewery Lat' : 'BrewLat',
                                    'Brewery Lon' : 'BrewLon',
                                    'Venue Lat' : 'VenueLat',
                                    'Venue Lon' : 'VenueLon',
                                    'Venue Name' : 'VenueName'})
print "All data processed"

## Write out the combined csv files to a new csv
#outFile = r'G:\Share\GEOG6293_Programming\Gerry\Project\CombinedData.csv'
outFile = r'G:\Share\GEOG6293_Programming\Gerry\Project\CombinedData.csv'
allData.to_csv(outFile, index = False)

print "CombinedData.csv file written"
print "Script 2 is now complete"
