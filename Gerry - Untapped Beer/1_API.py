# -*- coding: utf-8 -*-

## Kady Gerry
## Geog 6392
## Project: Step 1
## Retrieve data using API

#### This script will:
#### 1. Format an API call for the UnTappd social networking site (untappd.com)
#### 2. Open the url to request data from the UnTappd API
#### 3. Parse the JSON data returned from the API call and flatten into a pandas data frame
#### 4. When over 500 results have been retrieved, write out a .csv file and clear the data frame
#### 5. Wait 40 seconds (so the hourly request limit is not exceeded) then repeat the process, formatting the new
####    API call based on the data that was retrieved in the previous call 

#### You may need to install d9t.json to run this script - d9t.json is the full name of the package
#### (not d9t)
#### d9t.json makes dictionaries of dictionaries for complex JSON trees. It's pretty sweet.

import urllib2
from d9t.json import parser
import pandas as pd
import time

## The baseURL and method are the basis for all API call
baseURL = r'https://api.untappd.com/v4/'
method = r'thepub/local'

## The clientID and clientSecret serve as the username & password and must be included in the API call
## These are supposed to be secret. Please don't share them!
clientID = r'client_id=717718327A2BB08D6946A825178257B982AA148B'
clientSecret = r'client_secret=33D67AF75EE4EC746CFB364333E4FE6CB6C6E4F4'

## Geospatial parameters for API call, these are specific to the method "thepub/local"
## The lat/lon provided are for the Washington Monument
lat = r'lat=38.889078'
lon = r'lng=-77.035298'


## min_id is a parameter for the check-in ID. The initial call has no minimum, but
## after the initial call is completed, the value will be updated with the maximum
## id of the data retrived
min_id = 0

## k is used to incrementally number the output .csv file name. Since I already have 104 files
k = 105

## Set up the data frame to contain the results of the API calls
parsedCheckIn = pd.DataFrame()

## Set up the initial API call according to documentation provided by UnTappd: 
## https://untappd.com/api/docs#theppublocal - viewing the documentation requires an account
url = baseURL + method + '?' + lat + '&' + lon + '&' + clientID + '&' + clientSecret

## Open the url to retrieve an initial round of data from the API
result = urllib2.urlopen(url)

## I made the n variable out of curiosity, to see what the maximum number of results
## returned per API call was. It was generally in the single digits, but at some point
## the API was returning errors and when it started working again it maxes out at 25.
n = 0

## The 'for' loop below will generate and execute API calls. Originally, I had range(0,30240), which
## will take 2 weeks at 40 second intervals to complete. Since you might actually want to see
## the entire process, it's set to a more resonable 5 API calls.

## When I was running the script, for an unknonw reason, after about 1 week, the script had run through all iterations.
## Even if all of the API calls failed, the time.sleep(40) function should still function properly and it should 
## still take 2 weeks.
for i in range(0,5):
    ## Incorporate a try/except for when the API returns an unexpected error to prevent
    ## the program from crashing
    try:
        ## print out some useful information about where we are in the process
        print "Query Number: " + str(i) + ", Number of API requests remaining: " + result.headers.dict['x-ratelimit-remaining']
        print "Current length of parsedCheckIn dataframe: " + str(len(parsedCheckIn))
        
        ## retrieve data from the API and prepare the JSON data for parsing
        result = urllib2.urlopen(url)
        readjson = result.read()
        parsed = parser.JsDomParser(readjson)
        data = parsed.parse()
        
        ## There are a lot of extra field dictionaries in the JSON data, we only need three
        checkins = data['response']['checkins']['items']
        
        ## Each checkin is parsed into a row in a the parsedCheckIn data frame
        for j in range(len(checkins)):
            ## n keeps track of the maximum number of results returned by the API query (skipping the first because
            ## the first is guaranteed to be 25 results)            
            if i > 1:
                n = max(n, len(checkins))
                
            ## newID will be used in the next API call as the minimum checkin id
            newID = checkins[j]['checkin_id']
            if newID > min_id:
                min_id = newID
                
            ## Parse the JSON results for the current checkin
            newRating = checkins[j]['rating_score']
            newDate = checkins[j]['created_at']
            newDate = pd.to_datetime(newDate)
            newBeer = checkins[j]['beer']['beer_name']
            newStyle = checkins[j]['beer']['beer_style']
            newBrewery = checkins[j]['brewery']['brewery_name']
            newBrewCity = checkins[j]['brewery']['location']['brewery_city']
            newBrewState = checkins[j]['brewery']['location']['brewery_state']
            newBrewLat = checkins[j]['brewery']['location']['lat']
            newBrewLon = checkins[j]['brewery']['location']['lng']
            newVenueName = checkins[j]['venue']['venue_name']
            newVenueLat = checkins[j]['venue']['location']['lat']
            newVenueLon = checkins[j]['venue']['location']['lng']
            
            ## Create a dictionary for the current checkin
            nextCheckIn = {'id' : newID, 'Rating' : newRating, 'Beer' : newBeer, 'Style' : newStyle,
                           'Brewery' : newBrewery, 'BrewCity' : newBrewCity, 'BrewState' : newBrewState,
                           'Brewery Lat' : newBrewLat, 'Brewery Lon' : newBrewLon,
                           'Venue Lat' : newVenueLat, 'Venue Lon' : newVenueLon,
                           'Date_Time' : newDate, 'Venue Name' : newVenueName}
                           
            ## Append the parsed current check in to the data frame
            parsedCheckIn = parsedCheckIn.append(nextCheckIn, ignore_index = True)
    
    ## If something went wrong (generally with the API call), let me know but keep going    
    except:
        print "An error occurred with query #" + str(i)
    
    ## When the number of results in the data frame is greater than 500, write out a .csv file
    ## Then, empty the data frame and add 1 to k so the next file name will be different
    if len(parsedCheckIn) > 500:
        filepath = r'G:\Share\GEOG6293_Programming\Gerry\Project\Data'
        #filepath = r'C:\Users\User\Documents\School Stuff\GWU\Geo Programming\Project\Data'
        filename = '\Output_' + str(k) + '.csv'
        k = k + 1
        parsedCheckIn.to_csv(filepath+filename, index = False)
        parsedCheckIn = pd.DataFrame()
    
    ## Update the API call url with the maximum checkin id retrieved
    url = baseURL + method + '?' + lat + '&' + lon + '&min_id=' + str(min_id) + '&' + clientID + '&' + clientSecret
    
    ## Wait and repeat
    time.sleep(40)

## After the script iterations are complete, write out the final .csv file
parsedCheckIn.to_csv(filepath+filename, index = False)
