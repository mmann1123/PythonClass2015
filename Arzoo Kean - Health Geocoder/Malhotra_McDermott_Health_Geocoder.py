##### Introduction
"""
Analyzing Doctor Payment Data 
Utilizing Open Payments Data from the Department of 
Created by Arzoo Malhotra and Kean McDermott
"""

####### Part 0: Set up
#### This is the step where modules are imported, variables and workspaces are set, and 
#### and other logistics and managed

print "\nThis is the start of Part 0: Set up" 

## Import and set up environments
import arcpy, os
import csv
arcpy.env.workspace = r"G:\Share\GEOG6293_Programming\Malhotra\Final Project\diabeetus.gdb"
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984")
arcpy.env.overwriteOutput=True
print "\tImport and Environment set up step complete"

## Assign variables

# VARIABLES FOR PART 1

fastfood = "BP_2011_00A1_with_ann"
obesity = "T2012_ObesityPrevalence"
diabetes = "T2012_DiagnosedDiabetesPrevalence"
payments = "Texas_bydureon"
UScounties = "UScounties"
tx_sel_exp = """ "STATE_NAME" = 'Texas' """
fips_exp = """[FIPS_Codes]"""
del_fields = [
"TX_ob_di_TX_ob_T2012_ObesityPrevalence_OBJECTID", 
"TX_ob_di_TX_ob_T2012_ObesityPrevalence_State", 
"TX_ob_di_TX_ob_T2012_ObesityPrevalence_FIPS_Codes", 
"TX_ob_di_TX_ob_T2012_ObesityPrevalence_County", 
"TX_ob_di_TX_ob_T2012_ObesityPrevalence_F2012_lower_con",
"TX_ob_di_TX_ob_T2012_ObesityPrevalence_F2012_upper_con",
"TX_ob_di_TX_ob_T2012_ObesityPrevalence_ob_2012_age_perc"
"TX_ob_di_TX_ob_T2012_ObesityPrevalence_ob_2012_age_lowcon",
"TX_ob_di_TX_ob_T2012_ObesityPrevalence_ob_2012_age_highcon", 
"TX_ob_di_TX_ob_T2012_ObesityPrevalence_FIPS",
"TX_ob_di_T2012_DiagnosedDiabetesPrevalence_OBJECTID",
"TX_ob_di_T2012_DiagnosedDiabetesPrevalence_State",
"TX_ob_di_T2012_DiagnosedDiabetesPrevalence_FIPS_Codes",
"TX_ob_di_T2012_DiagnosedDiabetesPrevalence_County",
"TX_ob_di_T2012_DiagnosedDiabetesPrevalence_F2012_lowcon",
"TX_ob_di_T2012_DiagnosedDiabetesPrevalence_F2012_highcon",
"TX_ob_di_T2012_DiagnosedDiabetesPrevalence_F2012_age_perc",
"TX_ob_di_T2012_DiagnosedDiabetesPrevalence_F2012_age_lowcon",
"TX_ob_di_T2012_DiagnosedDiabetesPrevalence_F2012_agehighcon",
"TX_ob_di_T2012_DiagnosedDiabetesPrevalence_FIPS",
"BP_2011_00A1_with_ann_OBJECTID",
"BP_2011_00A1_with_ann_GEO_id",
"BP_2011_00A1_with_ann_GEO_id2",
"BP_2011_00A1_with_ann_GEO_display_label",
"BP_2011_00A1_with_ann_NAICS_id",
"BP_2011_00A1_with_ann_NAICS_display_label",
"BP_2011_00A1_with_ann_YEAR_id",
"BP_2011_00A1_with_ann_EMP",
"BP_2011_00A1_with_ann_PAYQTR1",
"BP_2011_00A1_with_ann_PAYANN"
]
txcounties = "TX_METRICS"

# VARIABLES FOR PART 2

concat_exp = "!Recipient_Primary_Business_Street_Address_Line1! + ' ' + !Recipient_City! + ' ' + !Recipient_State!"
#  +  ' ' + !Recipient_Zip_Code!"
doc_exp = "!Physician_First_Name! + ' ' + !Physician_Last_Name!"
index_exp = """[ObjectID]"""
outws = r"G:\Share\GEOG6293_Programming\Malhotra\Final Project"
Input_Table = "G:\Share\GEOG6293_Programming\Malhotra\Final Project\\writtencsv.csv"
Output_Geodatabase = "G:\Share\GEOG6293_Programming\Malhotra\Final Project\diabeetus.gdb"
table_dbf = "G:\Share\GEOG6293_Programming\Malhotra\Final Project\diabeetus.gdb\writtencsv"
table2layer1 = "table2layer1"
payment_pnt = "\\Share\\GEOG6293_Programming\\\Malhotra\Final Project\\diabeetus.gdb\\TX_payment_shp"
long_exp = """[Field4]"""
lat_exp = """[Field3]"""
txpayments = "TX_PAYMENTS"

# VARIABLES FOR PART 3

count_exp = "1"
pay_dissolve_field = "Texas_bydureon_doc_full_name"
doc_dissolve_field = "TX_ob_di_TX_ob_TX_counties_FIPS"
pay_dissolve = "TX_pay_dis"
join_dissolve = "TX_join_dis"
out_join = "TX_join"
final_output = "TX_FINAL"
pay_dissolve_stats = [["pay_count", "SUM"], ["Texas_bydureon_Total_Amount_of_Payment_USDollars", "SUM"], ["doc_count", "FIRST"]]
doc_dissolve_stats = [
["TX_ob_di_TX_ob_TX_counties_NAME", "FIRST"],
["TX_ob_di_TX_ob_T2012_ObesityPrevalence_F2012_percent", "FIRST"], 
["TX_ob_di_T2012_DiagnosedDiabetesPrevalence_F2012_percent", "FIRST"], 
["BP_2011_00A1_with_ann_ESTAB", "FIRST"], 
["SUM_pay_count", "SUM"], 
["SUM_Texas_bydureon_Total_Amount_of_Payment_USDollars", "SUM"], 
["FIRST_doc_count", "SUM"]
]
txname_exp = """ [FIRST_TX_ob_di_TX_ob_TX_counties_NAME] """
txfips_exp = """ [TX_ob_di_TX_ob_TX_counties_FIPS] """
txobesity_exp = """ [FIRST_TX_ob_di_TX_ob_T2012_ObesityPrevalence_F2012_percent] """
txdiabetes_exp = """ [FIRST_TX_ob_di_T2012_DiagnosedDiabetesPrevalence_F2012_percent] """
txestab_exp = """ [FIRST_BP_2011_00A1_with_ann_ESTAB] """
txpayments_exp = """ [SUM_SUM_pay_count] """
txvalue_exp = """ [SUM_SUM_Texas_bydureon_Total_Amount_of_Payment_USDollars] """
txdoctors_exp = """ [SUM_FIRST_doc_count] """
del_messy = [
"FIRST_TX_ob_di_TX_ob_TX_counties_NAME",
"TX_ob_di_TX_ob_TX_counties_FIPS",
"FIRST_TX_ob_di_TX_ob_T2012_ObesityPrevalence_F2012_percent",
"FIRST_TX_ob_di_T2012_DiagnosedDiabetesPrevalence_F2012_percent",
"FIRST_BP_2011_00A1_with_ann_ESTAB",
"SUM_SUM_pay_count",
"SUM_SUM_Texas_bydureon_Total_Amount_of_Payment_USDollars",
"SUM_FIRST_doc_count"
]
print "\tVariable assignment step complete"

print "All steps in Part 0 are complete" 

##########################################################################################

####### Part 1: Clipping the Data
#### This section is designed to clean up the data so that it is trimmed to the region 
#### that we have selected for our study area (Texas) 

print "\nThis is the start of Part 1: Clipping, Joining, and Preprocessing" 

## Counties Subset Step
# create  layer, select TX counties, populate new counties layer
arcpy.MakeFeatureLayer_management(UScounties, "select_counties")
arcpy.SelectLayerByAttribute_management ("select_counties", "NEW_SELECTION", tx_sel_exp)
arcpy.CopyFeatures_management("select_counties", "TX_counties")
print "\tTX counties step successful"

## Obesity FIPS Set-up Step
# the FIPS column in the original dataset is numerical, I need to convert it to make it text
# so it can be joined with FIPS codes from other layers
arcpy.AddField_management(obesity, "FIPS", "TEXT", 6)
arcpy.CalculateField_management(obesity, "FIPS", fips_exp)
print "\tObesity FIPS step complete"

## Obesity Join Step
# use newly created TX counties shapefile and join obesity values to it
arcpy.MakeFeatureLayer_management("TX_counties", "join_obesity")
arcpy.AddJoin_management ("join_obesity", "FIPS", obesity, "FIPS", "KEEP_COMMON") 
arcpy.CopyFeatures_management("join_obesity", "TX_ob")
print "\tTX obesity join step successful"

## Diabetes FIPS Set-up Step
# the FIPS column in the original dataset is numerical, I need to convert it to make it text
# so it can be joined with FIPS codes from other layers
arcpy.AddField_management(diabetes, "FIPS", "TEXT", 6)
arcpy.CalculateField_management(diabetes, "FIPS", fips_exp)
print "\tDiabetes FIPS step complete"

## Diabetes Join Step
# use newly created TX_ob shapefile and join diabetes values to it
arcpy.MakeFeatureLayer_management("TX_ob", "join_diabetes")
arcpy.AddJoin_management ("join_diabetes", "TX_counties_FIPS", diabetes, "FIPS") 
arcpy.CopyFeatures_management("join_diabetes", "TX_ob_di")
print "\tTX diabetes join step successful"

## Fast Food Join Step
# use newly created TX counties shapefile and join fastfood values to it
arcpy.MakeFeatureLayer_management("TX_ob_di", "join_fastfood")
arcpy.AddJoin_management ("join_fastfood", "TX_ob_TX_counties_FIPS", fastfood, "GEO_id2") 
arcpy.CopyFeatures_management("join_fastfood", "TX_OB_DI_FF")
print "\tTX fastfood join step successful"

## Fast Food Populate Null Step
# use the update cursor to cycle through number of fast food establishment values and 
# replace all null values with 0 values so they will be included in the processing.
with arcpy.da.UpdateCursor("TX_OB_DI_FF", "BP_2011_00A1_with_ann_ESTAB") as null:
	for row in null:
		if row[0] == None:
			row[0] = 0
			null.updateRow(row)
print "\tTX fastfood null update step successful"

## Table Clean Up
# because of the sheer number of joins I did in the creation of this table, there are
# a ton of columns in it's attribute table that I have no use for. Just to make everything
# simpler later on, I decided to clean up the unnecessary columns
arcpy.Copy_management("TX_OB_DI_FF", txcounties)
arcpy.DeleteField_management(txcounties, del_fields)
print "\tTX table clean up step successful"

print "All steps in Part 1 are complete" 

##########################################################################################

####### Part 2: Geocoding the data
#### The purpose of the script in this section is to geocode the addresses doctors to whom
#### payments were made, in order to use them for spatial processes later

print "\nThis is the start of Part 2: Geocoding the data"

## Add fields and calculate field values
# calculate field for doctors full name
arcpy.AddField_management(payments, "conc_address", "STRING")
arcpy.CalculateField_management(payments, "conc_address", concat_exp, "PYTHON")
# add a field that has the doctors full name
# Caluculate field for concatenated address
arcpy.AddField_management(payments, "doc_full_name", "STRING")
arcpy.CalculateField_management(payments, "doc_full_name", doc_exp, "PYTHON")
#add field thats a unique ID
# Calculate UniqueID for Geolocating in next step
arcpy.AddField_management(payments, "index", "SHORT")
arcpy.CalculateField_management(payments, "index", index_exp)
print "\tAdd fields and calculate field values step complete"

## Export csv for geocoding
arcpy.TableToTable_conversion(payments, outws, 'payment_outfile.csv')
print "\tExport csv for geocoding step complete"


import geopy
from geopy.geocoders import GoogleV3
geolocator = GoogleV3(api_key="AIzaSyCgOKuJ3ruW3miaWTsGEh9Po5ed5MrydQE") #insert your API KEY HERE
## begin the geolocating
print "\t\tImported geolocator"

with open('G:\Share\GEOG6293_Programming\Malhotra\Final Project\payment_outfile.csv', 'rb') as csvinput:
    with open('G:\Share\GEOG6293_Programming\Malhotra\Final Project\google_geocode.csv', 'w') as csvoutput:
       output_fieldnames = ['doc_full_name', 'conc_address', 'Latitude', 'Longitude']
       writer = csv.DictWriter(csvoutput, delimiter=',', fieldnames=output_fieldnames)
       reader = csv.DictReader(csvinput)
       for row in reader:
            #here you have to replace the dict item by your csv column names
            query =row["conc_address"]

            try:
                address, (latitude, longitude) = geolocator.geocode(query)
            except:
                latitude = 'N/A'
                longitude = 'N/A'

            #here is the writing section
            output_row = {}
            output_row['doc_full_name'] = row['doc_full_name']
            output_row['conc_address'] = row['conc_address']
            output_row['Latitude'] = latitude
            output_row['Longitude'] = longitude
            #add more of the applicable rows here or rejoin the two tables
            writer.writerow(output_row)
print "\tGeocoding step complete"

out_fnam = "G:\Share\GEOG6293_Programming\Malhotra\Final Project\\writtencsv.csv"
in_fnam = "G:\Share\GEOG6293_Programming\Malhotra\Final Project\google_geocode.csv"
input = open("G:\Share\GEOG6293_Programming\Malhotra\Final Project\google_geocode.csv", 'rb')
output = open(out_fnam, 'wb')
writer = csv.writer(output)
print "assign additional variables for geocode complete"

#attempt to use a csv writer to delete null values
input = open(in_fnam, 'rb')
output = open(out_fnam, 'wb')
writer = csv.writer(output)
for row in csv.reader(input):
    if row:
        writer.writerow(row)
input.close()
output.close()
print "\t\tremove null values complete"     

## Table convert
arcpy.TableToGeodatabase_conversion (Input_Table, Output_Geodatabase)  
print "\ttable convert step complete"

## create new fields that are float type for lat and long 
arcpy.AddField_management(table_dbf, "longitude", "FLOAT")
arcpy.CalculateField_management(table_dbf, "longitude", long_exp)
arcpy.AddField_management(table_dbf, "latitude", "FLOAT")
arcpy.CalculateField_management(table_dbf, "latitude", lat_exp)
print "\tLat/Long float field creation step complete"

## Make XY Event Layer
#"x_coord", "y_coord" are where you have your lat long
arcpy.MakeXYEventLayer_management(table_dbf, "longitude", "latitude", table2layer1, "", "") 
# Process: Copy Features
arcpy.CopyFeatures_management(table2layer1, payment_pnt, "", "0", "0", "0")
print "\tMake event layer and shapefile step complete"

## Join Data
# use update cursor to get rid of null values
arcpy.MakeFeatureLayer_management(payment_pnt, "Join_Texas_bydureon")
arcpy.AddJoin_management ("Join_Texas_bydureon", "OBJECTID", "Texas_bydureon", "OBJECTID", "KEEP_COMMON") 
arcpy.CopyFeatures_management("Join_Texas_bydureon", txpayments)
print "\tJoin data step complete"

print "All steps in Part 2 are complete"

##########################################################################################

####### Part 3: Combining the Payments data 
#### In this section, I will capture key information about the payments point data 
#### and summarize it within the counties polygon layer for analysis in the later steps. 
#### During this step, I will be creating usable values for 3 metrics: (1) The number of 
#### doctors who received payements per census tract, (2) the total value of the payments 
#### made to doctors in that census tract and (3) the total number of payments made in the 
#### census tract. 

print "\nThis is the start of Part 3: Combining the Payments data" 

## Create payments count field
# in this step I create a payments count step with a value of 1 for every payment made, 
# so that when payment data is aggregated up to only have one row per recipient doctor, 
# the number of payments received by the doctor can be summed
arcpy.AddField_management(txpayments, "pay_count", "SHORT")
arcpy.CalculateField_management(txpayments, "pay_count", count_exp)
print "\tCreate payments count field step complete"

## Create doctor count field
# in this step, much like I did for the payments count field, I will create a new column
# with a value of 1 for every doctor row so that when I do a spatial join between the 
# counties layer and the payments layer, I can sum the doctor count column to store the 
# number of doctors that receive payments per county
arcpy.AddField_management(txpayments, "doc_count", "SHORT")
arcpy.CalculateField_management(txpayments, "doc_count", count_exp)
print "\tCreate doctor count field step complete"

## Dissolve payments layer 
# In this step, I will aggregate the payments data to create one value per doctor
# without loosing the information about the number of payments and the value of all the 
# payments received
arcpy.Dissolve_management(txpayments, pay_dissolve, pay_dissolve_field, pay_dissolve_stats)
print "\tDissolve payments layer step complete" 

## Spatial join data
# in this step, I will do a spatial join to combine the data from the payments data and 
# counties data such that I have the values for (1) The number of doctors who received
# payements per census tract, (2) the total value of the payments made to doctors
# in that census tract and (3) the total number of payments made in the census tract all 
# aggregated to the county level 
arcpy.SpatialJoin_analysis(txcounties, pay_dissolve, out_join, "JOIN_ONE_TO_MANY", "", "", "CONTAINS")
print "\tSpatial join data step complete"


## Dissolve doctors layer
# in this step I will aggregate the information about doctors to count the number of 
# doctors operating and receiving payments in each county
arcpy.Dissolve_management(out_join, join_dissolve, doc_dissolve_field, doc_dissolve_stats)
print "\tDissolve doctors layer step complete" 

## Add new fields
# with all the joins and processes run on the tables, the field names have gone awry. 
# This step will create new fields and copy the values from the relevant old columns 
arcpy.AddField_management(join_dissolve, "County_Name", "TEXT")
arcpy.CalculateField_management(join_dissolve, "County_Name", txname_exp)
arcpy.AddField_management(join_dissolve, "County_FIPS", "DOUBLE")
arcpy.CalculateField_management(join_dissolve, "County_FIPS", txfips_exp)
arcpy.AddField_management(join_dissolve, "Obesity_Perc", "DOUBLE")
arcpy.CalculateField_management(join_dissolve, "Obesity_Perc", txobesity_exp)
arcpy.AddField_management(join_dissolve, "Diabetes_Perc", "DOUBLE")
arcpy.CalculateField_management(join_dissolve, "Diabetes_Perc", txdiabetes_exp)
arcpy.AddField_management(join_dissolve, "Fastfood_Estab", "DOUBLE")
arcpy.CalculateField_management(join_dissolve, "Fastfood_Estab", txestab_exp)
arcpy.AddField_management(join_dissolve, "Num_Payments", "DOUBLE")
arcpy.CalculateField_management(join_dissolve, "Num_Payments", txpayments_exp)
arcpy.AddField_management(join_dissolve, "Pay_USDValue", "DOUBLE")
arcpy.CalculateField_management(join_dissolve, "Pay_USDValue", txvalue_exp)
arcpy.AddField_management(join_dissolve, "Num_Doctors", "DOUBLE")
arcpy.CalculateField_management(join_dissolve, "Num_Doctors", txdoctors_exp)
print "\tAdd new fields step complete"

## Delete old fields
# to make processing and final work easier, I am deleting the columns with the 
# crazy long and confusing field names
arcpy.Copy_management(join_dissolve, final_output)
arcpy.DeleteField_management(final_output, del_messy)
print "\tDelete old fields step successful"

## Populate null values
# use the update cursor to cycle through values for payments data (docs, values, payments) 
# and replace all null values with 0 values so they will be included in the processing.
with arcpy.da.UpdateCursor(final_output, "Num_Payments") as null:
	for row in null:
		if row[0] == None:
			row[0] = 0
			null.updateRow(row)
with arcpy.da.UpdateCursor(final_output, "Pay_USDValue") as null:
	for row in null:
		if row[0] == None:
			row[0] = 0
			null.updateRow(row)
with arcpy.da.UpdateCursor(final_output, "Num_Doctors") as null:
	for row in null:
		if row[0] == None:
			row[0] = 0
			null.updateRow(row)
print "\tPopulate null values step successful"

print "All steps in Part 3 are complete" 
print "your file is: TX_FINAL in the geodatabase."

##########################################################################################

print "This is the start of part 4: Statistics"

import arcpy

# Set property to overwrite existing outputs
arcpy.env.overwriteOutput = True

# Local variables...
workspace = r"G:\Share\GEOG6293_Programming\Malhotra\Final Project\diabeetus.gdb"

#workspace = r"G:\\Share\Programming_6293\Malhotra\Final Project\diabeetus.gdb"

final = "TX_FINAL"


try:
    # Set the current workspace (to avoid having to specify the full path to the feature classes each time)
    arcpy.env.workspace = workspace

    # amount of money as a function of {diabetes, overweight,
    # fast food restraunts}
    # Process: Geographically Weighted Regression... 
    gwramt = arcpy.GeographicallyWeightedRegression_stats(final, "Pay_USDValue", 
                        "Obesity_Perc;Diabetes_Perc;Fastfood_Estab",
                        "amtGWR.shp", "ADAPTIVE", "Bandwidth_Parameter", "")

    # number of payments as a function of {diabetes, overweight,
    # fast food restraunts}
    # Process: Geographically Weighted Regression... 
    gwrnumb = arcpy.GeographicallyWeightedRegression_stats(final, "Num_Payments", 
                        "Obesity_Perc;Diabetes_Perc;Fastfood_Estab",
                        "numbGWR.shp", "ADAPTIVE", "Bandwidth_Parameter", "")

    # number of doctors as a function of {diabetes, overweight,
    # fast food restraunts}
    # Process: Geographically Weighted Regression... 
    gwrdoc = arcpy.GeographicallyWeightedRegression_stats(final, "Num_Doctors", 
                        "Obesity_Perc;Diabetes_Perc;Fastfood_Estab",
                        "docGWR.shp", "ADAPTIVE", "Bandwidth_Parameter", "")

    # Calculate Moran's Index of Spatial Autocorrelation
    # Process: Spatial Autocorrelation (Morans I)...      
    moransIamt = arcpy.SpatialAutocorrelation_stats(r"G:\Share\GEOG6293_Programming\Malhotra\Final Project\amtGWR.shp", "LocalR2",
                        "GENERATE_REPORT", "INVERSE_DISTANCE", 
                        "EUCLIDEAN_DISTANCE", "NONE", "#")

    # Calculate Moran's Index of Spatial Autocorrelation
    # Process: Spatial Autocorrelation (Morans I)...      
    moransInumb = arcpy.SpatialAutocorrelation_stats(r"G:\Share\GEOG6293_Programming\Malhotra\Final Project\numbGWR.shp", "LocalR2",
                        "GENERATE_REPORT", "INVERSE_DISTANCE", 
                        "EUCLIDEAN_DISTANCE", "NONE", "#")

    # Calculate Moran's Index of Spatial Autocorrelation
    # Process: Spatial Autocorrelation (Morans I)...      
    moransIdoc = arcpy.SpatialAutocorrelation_stats(r"G:\Share\GEOG6293_Programming\Malhotra\Final Project\docGWR.shp", "LocalR2",
                        "GENERATE_REPORT", "INVERSE_DISTANCE", 
                        "EUCLIDEAN_DISTANCE", "NONE", "#")
except:
    print(arcpy.GetMessages())
    # If an error occurred when running the tool, print out the error message.
print "All Steps Complete 3 GWR/Moran's I Generated"
