import arcpy
import os
import re

class Toolbox(object):
    def __init__(self):
        self.label = "BISG Tools"
        self.alias = "BISG_Tools"

        # List of tool classes associated with this toolbox
        self.tools = [Address_Cleaner, Geo_Data_Prep, Spatial_Join, Surname_Proxy, BISG]

class Address_Cleaner(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Address Cleaner"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        workspace = arcpy.Parameter(
            displayName = "Geodatabase",
            name = "gdb",
            datatype = "DEWorkspace",
            parameterType = "Required",
            direction = "Input")

        workspace.defaultEnvironmentName = "workspace"

        param1 = arcpy.Parameter(
            displayName = "Input Feature",
            name = "in_feature",
            datatype = "GPTableView",
            parameterType = "Required",
            direction = "Input"
            )

        param2 = arcpy.Parameter(
            displayName = "Street Address",
            name = "street_address",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )

        param2.parameterDependencies = [param1.name]
        param2.filter.list = ["Text"]

        param3 = arcpy.Parameter(
            displayName = "Suite/Floor/Apt/Unit Information",
            name = "street2",
            datatype = "Field",
            parameterType = "Optional",
            direction = "Input"
            )

        param3.parameterDependencies = [param1.name]
        param3.filter.list = ["Text"]

        param4 = arcpy.Parameter(
            displayName = "Postal Code",
            name = "zip",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )

        param4.parameterDependencies = [param1.name]
        param4.filter.list = ["Text", "Short", "Long"]

        param5 = arcpy.Parameter(
            displayName = "Clean Address",
            name = "Clean_Address",
            datatype = "Field",
            parameterType = "Derived",
            direction = "Output")

        param6 = arcpy.Parameter(
            displayName = "Clean Zip",
            name = "Clean_Zip",
            datatype = "Field",
            parameterType = "Derived",
            direction = "Output")

        param7 = arcpy.Parameter(
            displayName = "GEOCODE Table",
            name = "geocode_table",
            datatype = "DETable",
            parameterType = "Derived",
            direction = "Output")

        param8 = arcpy.Parameter(
            displayName = "FLAGGED Table",
            name = "flagged_table",
            datatype = "DETable",
            parameterType = "Derived",
            direction = "Output")

        params = [workspace, param1, param2, param3, param4, param5, param6, param7, param8]
        return params

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):        
        return

    def updateMessages(self, parameters):
        # Check to see if Street Address and Suite Information are the same field. 
        if parameters[3].value:
            p2 = parameters[2].valueAsText
            p3 = parameters[3].valueAsText
            if p2 == p3:
                parameters[3].setErrorMessage(
                    "Street Address and Suite Information inputs cannot have the same field. "
                    "If Suite Information field does not exist, leave this parameter blank.")
            else:
                parameters[3].setWarningMessage(
                    "This field will be altered permanently. This cannot be undone. If the original contents of "
                    "the field need to be preserved, create a copy of the field before cleaning addresses.")     

        if parameters[4].value:
            p2 = parameters[2].valueAsText
            p3 = parameters[3].valueAsText
            p4 = parameters[4].valueAsText

            if p4 == p3 or p4 == p2:
                parameters[4].setErrorMessage(
                    "The Postal Code field must be different from Street Address and Suite Information "
                    "fields. Addresses cannot be cleaned if information is not parsed into separate fields.")

        if parameters[1].value:
            lst = arcpy.ListFields(parameters[1].valueAsText)
            for f in lst:
                if f.name == "Clean_Address" or f.name == "Clean_Zip5":
                    parameters[1].setErrorMessage(
                        parameters[1].valueAsText + ' includes fields named "Clean_Address" and/or "Clean_Zip5". '
                        'Please delete these fields or change their name before cleanining addresses as fields with '
                        'these names will be added to the table after running the code.')
                    break

            tblgcd = parameters[1].valueAsText + "_GEOCODE"
            tblflg = parameters[1].valueAsText + "_FLAGGED"
            arcpy.env.workspace = parameters[0].valueAsText
            if arcpy.Exists(tblgcd) or arcpy.Exists(tblflg):
                parameters[1].setErrorMessage(
                    "This table appears to be cleaned in geodatabase already."
                    "To continue geocoding, please rename/remove " + tblgcd + " and/or " + tblflg + " tables from "
                    "the Geodatabase or change the Geodatabase above.")


        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        #   IMPORTING MODULES
        import arcpy
        import re

        #   UPDATING GEODATABASE LOCATION
        arcpy.env.workspace = parameters[0].valueAsText

        #   INPUT PARAMETERS
        #           fc  = FEATURE CLASS INPUT
        #   ADDRESS_in  = NAME OF FIELD WITH ADDRESS INFORMATION IN fc
        #       ZIP_in  = NAME OF FIELD WITH ZIPCODE INFORMATION IN fc
        #
        #   ***THIS SCRIPT ASSUMES ADDRESS INFORMATION HAS BEEN PARSED***

        fc = parameters[1].valueAsText    
        ADDRESS_in = parameters[2].valueAsText     
        ZIP_in = parameters[4].valueAsText
        ADDRESS_in2 = parameters[3].valueAsText

        ########################################################################################################
        ########################################################################################################
        #   CREATING NEW FIELDS FOR CLEAN ADDRESS IN THE INPUT FEATURE CLASS
        #   FIELDS ARE SET TO TYPE STRING
        arcpy.AddField_management(fc, "Clean_Address", "TEXT")
        arcpy.AddField_management(fc, "Clean_Zip5", "TEXT")
        arcpy.AddField_management(fc, "WORKS", "TEXT")

        #   SETTING NAMES FOR OUTPUT TABLES
        #               out_geo     = TABLE NAME FOR ADDRESSES READY FOR GEOCODE
        #           out_flagged     = TABLE NAME FOR FLAGGED ADDRESSES
        out_geo = fc + "_GEOCODE"
        out_flagged = fc + "_FLAGGED"

        #   CREATING LIST OF FIELD NAMES TO BE USED IN CURSOR
        #   THE LAST FIELD - "WORKS" - IS A TEMPORARY FIELD THAT IS USED TO STORE INFORMATION ON IF ADDRESS IS
        #   OK TO GEOCODE. THIS FIELD WILL BE USED IN A SQL QUERY TO CREATE THE TWO OUTPUT TABLES.
        fields_raw = (ADDRESS_in, ADDRESS_in2, ZIP_in, "Clean_Address", "Clean_Zip5", "WORKS")


        ########################################################################################################
        ########################################################################################################
        ########################################################################################################
        ########################################################################################################


        #   DEFINING PROGRAM VARIABLES, FUNCTIONS, AND EXPRESSIONS
        #   VARIABLE, REGEXES, FUNCTION, SQL DEFINITIONS:
        #                     symbls    = VARIABLES FOR SYMBOLS TO BE REMOVED FROM ADDRESS.
        #                     flInfo    = REGEX PATTERN TO FIND FLOOR INFORMATION IN ADDRESS.
        #                    isPOBox    = REGEX PATTERN TO CHECK IF ADDRESS IS A PO BOX.
        #               firstNoDigit    = REGEX PATTERN TO CHECK IF FIRST CHARACTER IN ADDRESS IS A DIGIT.
        #                    goodZip    = REGEX PATTERN TO CHECK IF ZIP CODE IS 5 DIGITS ONLY. 
        #                      words    = VARIABLE DEFINING LIST OF KEY WORDS AND ABBREVIATIONS IN ADDRESS THAT 
        #                                 NEED TO BE REMOVED.
        #                    numWrit    = WRITTEN FORM OF NUMBERS ONE THROUGH TEN. THESE NUMBERS WILL BE
        #                                 CONVERTED TO NUMERICS IF THEY ARE IN THE BEGINING OF AN ADDRESS.
        #                   numNumer    = NUMERICAL FORM OF NUMBERS ONE THROUGH TEN. THESE NUMBERS WILL
        #                                 REPLACE THEIR RESPECTIVE WRITTEN FORM NUMBERS IF THEY ARE IN THE 
        #                                 BEGINING OF A SENTENCE. 
        #                      types    = VARIABLE DEFINING LIST OF KEY STREET TYPES WRITTEN IN LONG FORM. IF FOUND
        #                                 THESE WILL BE REPLACED WITH THEIR RESPECTIVE ABBREVIATIONS.
        #                 typesAbbrv    = VARIABLE DEFINING LIST OF STREET TYPE ABBREVIATIONS THAT WILL BE USED TO 
        #                                 REPLACE LONG FORM STREET TYPES IF FOUND.
        #                   poundNum    = CLASS RETURNING RESULTS OF REGEX PATTERN SEARCH USED TO FIND SUITE,
        #                                 APARTMENT, AND FLOOR INFORMATION REPRESENTED WITH A "#" FOLLOWED BY
        #                                 A SERIES OF DIGITS.
        #              findWrongWord    = CLASS RETURNING RESULTS OF REGEX PATTERN SEARCH USED TO FIND KEY
        #                                 WORDS AND ABBREVIATIONS IN ADDRESS THAT NEED TO BE REMOVED OR ALTERED.
        #                                 USER INPUTS WORD AND CLASS RETURNS T/F IF FOUND OR NOT FOUND.     
        #           where_clause_geo    = SQL EXPRESSION TO VERIFY THE TEMPORARY "WORKS" FIELD IS "YES".
        #       where_clause_flagged    = SQL EXPRESSION TO VERIFY THE TEMPORARY "WORKS" FIELD IS "NO".

        #   DEFINING LISTS,VARIBLES, AND REGEXES
        arcpy.AddMessage("Compiling RegExes...")
        symbls = r"[!@$:#\\^]"
        flInfo = re.compile(r"([\d]?[\d]?[\d][\s]?[\s]?((ST)|(ND)|(RD)|(TH))?[\s][\s]?(FL((OOR)|(\s)|($))))")
        isPOBox = re.compile(r"P\.?\s?O\.?(\s{1,2})?((BOX)|(BX))")
        firstNoDigit = re.compile(r"^\D.*$")
        goodZip = re.compile(r"^\d{5}$")
        words = (
            "SUITE", 
            "STE", 
            "APARTMENT", 
            "APT",
            "UNIT",
            "FLOOR",
            "FL",
            "BSMT",
            "BLDG",
            "DEPT",
            "FRNT",
            "HNGR",
            "LBBY",
            "LOWR",
            "OFC",
            "PH",
            "TRLR",
            "UPPR",
            "STUDIO",
            "LEVEL"
            )
        numWrit = (
            "ONE",
            "TWO",
            "THREE",
            "FOUR",
            "FIVE", 
            "SIX",
            "SEVEN",
            "EIGHT",
            "NINE",
            "TEN",
            )
        numNumer = (
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            )
        types = (
            "AVENUE",
            "ROAD",
            "BOULEVARD",
            "COURTS",
            "DRIVE",
            "ROUTE",
            "JUNCTION",
            "HIGHWAY",
            "STREET",
            "TRAIL",
            "PARKWAY",
            "CIRCLE",
            "CENTER",
            "LANE"
            )
        typesAbbrv = (
            "AVE",
            "RD",
            "BLVD",
            "CTS",
            "DR",
            "RT",
            "JCT",
            "HWY",
            "ST",
            "TRL",
            "PKWY",
            "CIR",
            "CTR",
            "LN"
            )

        #   DEFINING FUNCTIONS
        def poundNum(w):
            return re.compile(r'\s({0})[0-9]'.format(w),).search
        def findWrongWord(w):
            return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

        #   DEFINING SQL QUERIES
        where_clause_geo = " \"WORKS\" = 'YES' "
        where_clause_flagged = " \"WORKS\" = 'NO' "


        ########################################################################################################
        ########################################################################################################
        ########################################################################################################
        ########################################################################################################


        #   CREATING A CURSOR TO BE USED TO UPDATE ROWS IN THE ATTRIBUTE TABLE
        arcpy.AddMessage("Cleaning addresses...")
        with arcpy.da.UpdateCursor(fc, fields_raw) as cursor_raw:
            #   THIS FOR LOOP WILL UPDATE THE "Clean_Address" AND "Clean_Zip5" FIELDS. IT WILL ALSO POPULATE THE
            #   "_GEOCODE" AND "_FLAGGED" TABLES WITH THEIR RESPECTIVE ROWS. WHEN READY FOR GEOCODING, USE THE 
            #   "_GEOCODE" TABLE FOR MOST ACCURATE AND EFFICIENT RESULTS.  
            #   
            #   INPUT PARAMETERS:
            #                 row[0]    = ADDRESS_in
            #                 row[1]    = ADDRESS_in2
            #                 row[2]    = ZIP_in
            #                 row[3]    = Clean_Address
            #                 row[4]    = Clean_Zip5
            #                 row[5]    = WORKS (temporary)
            #
            #   KEY VARIABLES:
            #                    addy   = VARIABLE HOLDING AND UPDATING ADDRESS INFORMATION.
            #                   addy2   = VARIABLE HOLDING AND UPDATING ADDRESS LINE 2 INFORMATION IF GIVEN.
            #                   zippy   = VARIABLE HOLDING AND UPDATING ZIPCODE INFORMATION.
            #            flInfo_match   = VARIABLE THAT CHECKS FOR FLOOR INFORMATION IN ADDRESS.
            #           isPOBox_match   = VARIABLE THAT TESTS IF ADDRESS IS A PO BOX.
            #      firstNoDigit_match   = VARIABLE THAT TESTS IF ADDRESS BEGINS WITH DIGIT.
            #           goodZip_match   = VARIABLE THAT TESTS IF ZIP CODE IS ONLY 5 DIGITS. 
            
            for row in cursor_raw:
                #   CREATING VARIABLES TO STORE AND UPDATE VALUES IN FOR LOOP
                addy = row[0]
                if ADDRESS_in2:
                    if row[1] is None:
                        row[1] = ""
                        # cursor_raw.updateRow(row)
                    addy2 = row[1]
                    if addy2 == " ":
                        addy2 = ""

                
                #   UPDATING CLEAN ADDRESS VARIABLE WITH ADDRESS INFORMATION.
                #   TRANSFORMING TO UPPERCASE.
                if addy:
                    addy = addy.upper()
                else:
                    addy = ""

                #   STRIPPING ALL INFORMATION IF PATTERN " #" + [0-9] FOUND.
                #   THE SPACE BEFORE "#" ENSURES THAT ENTIRE ADDRESS IS NOT REMOVED IF ADDRESS STARTS WITH
                #   "#". ALL ADDITIONAL "#" WILL BE REMOVED IN A LATER STEP.
                if poundNum(r"#")(addy):    
                    sep = " #"
                    addy, sep, tail = addy.partition(sep)
                    if ADDRESS_in2:
                        if addy2 == "":
                            addy2 = sep + tail
                            addy2 = addy2.replace(" ", "")

                #   NOTE: WE REMOVE SYMBOLS AFTER CHECKING IF poundNum == True.
                #   THIS IS TO ENSURE WE STRIP ENTIRE SUITE/FLOOR/UNIT INFORMATION IF PRECEEDED BY "#".
                addy = re.sub(symbls, "", addy)
                
                #   THE FOLLOWING CHECKS FOR FLOOR INFORMATION ATTACHED TO THE END OF THE ADDRESS.
                #   EXAMPLE "3RD FLOOR". IF FOUND, THIS INFORMATION IS STRIPPED AND COPIED TO 
                #   ADDRESS_in2 FIELD, IF PROVIDED.
                flInfo_match = re.search(flInfo, addy)
                if flInfo_match is not None:
                    sep = flInfo_match.group(1)
                    addy, sep, tail = addy.partition(sep)
                    if ADDRESS_in2:
                        if addy2 == "":
                            addy2 = sep + tail

                #   THE FOLLOWING LOOP REMOVES COMMON ABBREVIATIONS FOR SUITE/FLOOR/UNIT/APARTMENT
                #   AS WELL AS ALL PROCEEDING TEXT. THIS INFORMATION IS STRIPPED AND COPIED TO
                #   ADDRESS_in2 FIELD, IF PROVIDED.
                for word in words:
                    if findWrongWord(word)(addy):
                        sep = " " + word + " "
                        addy, sep, tail = addy.partition(sep)
                        if ADDRESS_in2:
                            if addy2 == "":
                                sep = sep.replace(" ", "")
                                sep = sep + " "
                                addy2 = sep + tail

                        sep = "," + word
                        addy, sep, tail = addy.partition(sep)           
                        if ADDRESS_in2:
                            if addy2 == "":
                                addy2 = sep + tail
                                addy2 = addy2.replace(",", "")
                                addy2 = addy2.replace(" ", "")

                        sep = "-" + word
                        addy, sep, tail = addy.partition(sep)       
                        if ADDRESS_in2:
                            if addy2 == "":
                                addy2 = sep + tail
                                addy2 = addy2.replace("-", "")
                                addy2 = addy2.replace(" ", "")      
                
                #   COMMAS AND SEMICOLONS ARE TREATED DIFFERENTLY AS THEY COMMONLY ARE USED TO SPLIT
                #   SUIT/FLOOR/UNIT INFORMATION. IF FOUND, WILL REPLACE WITH SPACE, NOT BLANK.  
                addy = re.sub(r"[,;\\.]", " ", addy)
                
                #   THE FOLLOWING LOOP REPLACES WRITTEN NUMBERS WITH NUMERICAL NUMBERS IF THEY ARE IN
                #   THE BEGINING OF AN ADDRESS.
                for i, nums in enumerate(numWrit):
                    if findWrongWord(nums)(addy):
                        sep = nums + " "
                        first_word = addy.split(sep, 1)[0]
                        if first_word == "":
                            addy = addy.split(sep, 1)[-1]
                            addy = numNumer[i] + " " + addy
                
                #   THE FOLLOWING LOOP REPLACES LONG FORM STREET TYPES WITH THE ABBREVIATIONS.
                addy = addy + " "
                for i, typ in enumerate(types):
                    if findWrongWord(typ)(addy):
                        addy = addy.replace(r" "+typ+r" ", r" "+typesAbbrv[i]+r" ")

                #   UPDATING "Clean_Address" AND "ADDRESS_in2" FIELDS
                row[3] = addy
                row[1] = addy2


                ####################################################################################################
                ####################################################################################################
                ####################################################################################################
                ####################################################################################################


                #   THE FOLLOWING SECTION OF THE LOOP FOCUSES ON CLEANING ZIPCODE INFORMATION AND STANDARDIZING IT
                #   TO FIVE DIGIT ZIP CODES. THE "Clean_Zip5" FIELD WILL BE UPDATED.
                #   SETTING zippy TO CURRENT ZIPCODE INFORMATION.
                zippy = str(row[2])

                #   REMOVING SPACES FROM ZIP CODE
                if zippy:
                    zippy = zippy.replace(r" ", "")
                else:
                    zippy = ""
                
                #   STRIPPING ALL INFORMATION IF HYPHEN FOUND.
                #   IF A HYPHEN APPEARS IN THE ZIP CODE, THE HYPHEN AND ALL TEXT TO THE RIGHT OF IT WILL BE REMOVED.
                if re.search(r"-", zippy):
                    sep = "-"
                    zippy, sep, tail = zippy.partition(sep)
                
                #   UPDATING "Clean_Zip5" FIELD. 
                row[4] = zippy
                

                ####################################################################################################
                ####################################################################################################
                ####################################################################################################
                ####################################################################################################


                # PERFORMING TESTS ON CLEANED ADDRESS AND ZIPCODE TO SEE IF RECORD CAN BE GEOCODED.
                isPOBox_match = re.search(isPOBox, addy)
                firstNoDigit_match = re.search(firstNoDigit,addy)
                goodZip_match = re.search(goodZip, zippy)

                #   THE FOLLOWING STATEMENTS ASSIGN THE TEMPORARY "WORKS" FIELD WITH YES/NO AFTER CHEKCING IF THE ADDRESS
                #   IS READY FOR GEOCODING. 
                if addy is None:
                    row[5] = "NO"
                elif isPOBox_match is not None:
                    row[5] = "NO"
                elif firstNoDigit_match is not None:
                    row[5] = "NO"
                elif goodZip_match is None:
                    row[5] = "NO"
                else:
                    row[5] = "YES"

                #   UPDATING INPUT TABLE.
                cursor_raw.updateRow(row)
        del cursor_raw, row

        arcpy.AddMessage("Creating GEOCODE and FLAGGED tables...")
        #   CREATING "_GEOCODE" TABLE FROM RECORDS IN INPUT TABLE THAT ARE READY FOR GEOCODING.
        arcpy.TableSelect_analysis(fc, out_geo, where_clause_geo)
        #   CREATING "_FLAGGED" TABLE FROM RECORDS IN INPUT TABLE THAT CANNOT BE GEOCODED. 
        arcpy.TableSelect_analysis(fc, out_flagged, where_clause_flagged)
        #   DELETING TEMPORARY FIELD.
        arcpy.AddMessage("Deleting temp files...")
        arcpy.DeleteField_management(fc, "WORKS")
        arcpy.DeleteField_management(out_geo, "WORKS")
        arcpy.DeleteField_management(out_flagged, "WORKS")


        return

class Geo_Data_Prep(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Geography Data Prep"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        workspace = arcpy.Parameter(
            displayName = "Geodatabase",
            name = "gdb",
            datatype = "DEWorkspace",
            parameterType = "Required",
            direction = "Input")
        
        param1 = arcpy.Parameter(
            displayName = "Input Feature",
            name = "in_feature",
            datatype = "GPTableView",
            parameterType = "Required",
            direction = "Input"
            )

        param2 = arcpy.Parameter(
            displayName = "Census Race Table State FIPS field",
            name = "censu_race_state_fips_field",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )
        param2.parameterDependencies = [param1.name]

        param3 = arcpy.Parameter(
            displayName = "Census Race Table GEOID field",
            name = "censu_race_geoid_field",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )
        param3.parameterDependencies = [param1.name]

        param4 = arcpy.Parameter(
            displayName = "Output Feature Class",
            name = "out_fc",
            datatype = "DEFeatureClass",
            parameterType = "Required",
            direction = "Output"
            )

        workspace.defaultEnvironmentName = "workspace"
        params = [workspace, param1, param2, param3, param4]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        import arcpy

        arcpy.env.workspace = parameters[0].valueAsText
        census_race_tbl = parameters[1].valueAsText
        cenfips = parameters[2].valueAsText
        cengeoid = parameters[3].valueAsText
        out_fc = parameters[4].valueAsText

        # Intializing Variables for use
        geo_population  = "Total_Pop"
        geo_hispanic    = "Hispanic_Total"
        geo_notHispanic = "Non_Hispanic_Total"
        geo_white       = "NH_White_alone"
        geo_black       = "NH_Black_alone"
        geo_nativ       = "NH_AIAN_alone"
        geo_asian       = "NH_API_alone"
        geo_other       = "NH_Other_alone"
        geo_multi       = "NH_Mult_Total"
        white_other     = "NH_White_Other"
        black_other     = "NH_Black_Other"
        nativ_other     = "NH_AIAN_Other"
        asian_other     = "NH_Asian_HPI"
        api_other       = "NH_API_Other"
        hpi_other       = "NH_Asian_HPI_Other"

        # Converting GEOID's to padded strings in race table
        arcpy.AddMessage("Converting Census Race table GEOIDs to padded strings")
        fields = arcpy.ListFields(census_race_tbl)
        for field in fields:
            if field.name == cenfips:
                if not field.type == "String":
                    arcpy.AddField_management(census_race_tbl, "st_fips_string", "TEXT")
                    with arcpy.da.UpdateCursor(census_race_tbl, [cenfips, "st_fips_string"]) as cursor_raw:
                        for row in cursor_raw:
                            stfips = str(int(row[0]))
                            row[1] = stfips.zfill(2)
                            #   UPDATING INPUT TABLE.
                            cursor_raw.updateRow(row)
                    del cursor_raw, row
                    cenfips = "st_fips_string"
            elif field.name == cengeoid:
                if not field.type == "String":
                    arcpy.AddField_management(census_race_tbl, "geoid_string", "TEXT")
                    with arcpy.da.UpdateCursor(census_race_tbl, [cengeoid, "geoid_string"]) as cursor_raw:
                        for row in cursor_raw:
                            geoid_num = str(int(row[0]))
                            row[1] = geoid_num.zfill(12)
                            #   UPDATING INPUT TABLE.
                            cursor_raw.updateRow(row)
                    del cursor_raw, row
                    cengeoid = "geoid_string"

        # Initializing national level population variables
        national_pop = 0
        national_white = 0
        national_black = 0
        national_nativ = 0
        national_asian = 0
        national_hawn = 0
        national_hispanic = 0

        arcpy.MakeTableView_management(census_race_tbl,  "geoLayer")
        arcpy.AddField_management("geoLayer", "here", "LONG")
        arcpy.AddField_management("geoLayer", "here_given_white", "LONG")
        arcpy.AddField_management("geoLayer", "here_given_black", "LONG")
        arcpy.AddField_management("geoLayer", "here_given_nativ", "LONG")
        arcpy.AddField_management("geoLayer", "here_given_asian", "LONG")
        arcpy.AddField_management("geoLayer", "here_given_multi", "LONG")
        arcpy.AddField_management("geoLayer", "here_given_hispanic", "LONG")

        with arcpy.da.UpdateCursor("geoLayer", [geo_population, geo_hispanic, geo_notHispanic, 
                                                geo_white, geo_black, geo_nativ, geo_asian, geo_other, 
                                                geo_multi, white_other, black_other, nativ_other, 
                                                asian_other, api_other, hpi_other]) as cursor_raw:
            for row in cursor_raw:
                total = row[0]
                hispanic = row[1]
                notHispanic = row[2]
                white = row[3]
                black = row[4]
                nativ = row[5]
                asian = row[6]
                other = row[7]
                multi = row[8]
                whiteOther = row[9]
                blackOther = row[10]
                nativOther = row[11]
                asianOther = row[12]
                apiOther = row[13]
                hpiOther = row[14]

                # Adding others to main race
                white += whiteOther
                black += blackOther
                nativ += nativOther
                asian += asianOther
                asian += apiOther
                asian += hpiOther
                multi = multi - (whiteOther + blackOther + nativOther + asianOther + apiOther + hpiOther)

                # Distributing remaining non_hispanic other population to all other non Hispanic populations evenly
                for i in [white, black,  nativ, asian, multi]:
                    i = i + (i / (total - hispanic-other)) * other
                    if total == 0:
                        i = 0 
                    if notHispanic == other:
                        i = other / 5

                # Updating national population counts
                national_pop += total
                national_white += white
                national_black += black
                national_nativ += nativ
                national_asian += asian 
                national_hispanic += hispanic

                # Converting counts into probabilities given geography
                for i in [white, black,  nativ, asian, multi, hispanic]:
                    i = i / total

                # Updating row 
                row[1] = hispanic
                row[3] = white 
                row[4] = black 
                row[5] = nativ 
                row[6] = asian 
                row[8] = multi 
                cursor_raw.updateRow(row)
            del cursor_raw, row

        with arcpy.da.UpdateCursor("geoLayer", [geo_population, geo_white, geo_black, geo_nativ, geo_asian, 
                                                geo_hispanic,  geo_multi, "here", "here_given_white", 
                                                "here_given_black", "here_given_nativ", "here_given_asian", 
                                                "here_given_hispanic", "here_given_multi"]) as cursor_raw:
            for row in cursor_raw:

                total = row[0]
                white = row[1]
                black = row[2]
                nativ = row[3]
                asian = row[4]
                hispanic = row[5]
                multi = row[6]

                total_here = total / national_pop
                white_here = white / national_white
                black_here = black / national_black
                nativ_here = nativ / national_nativ
                asian_here = asian / national_asian
                multi_here = multi / national_multi
                hispanic_here = hispanic / national_hispanic

                row[7] = total_here 
                row[8] = white_here
                row[9] = black_here
                row[10] = nativ_here
                row[11] = asian_here
                row[12] = hispanic_here
                row[13] = multi_here

        arcpy.CopyRows_management ("geoLayer", out_fc)
        return

class Spatial_Join(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Spatial_Join"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        workspace = arcpy.Parameter(
            displayName = "Geodatabase",
            name = "gdb",
            datatype = "DEWorkspace",
            parameterType = "Required",
            direction = "Input")
        
        param1 = arcpy.Parameter(
            displayName = "Input Feature",
            name = "in_feature",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Input"
            )

        workspace.defaultEnvironmentName = "workspace"

        param2 = arcpy.Parameter(
            displayName = "Input State Abbrevation Field",
            name = "state_field",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )

        param2.parameterDependencies = [param1.name]
        param2.filter.list = ["Text"]

        param3 = arcpy.Parameter(
            displayName = "Block Group Features",
            name = "census_feature",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Input"
            )

        param4 = arcpy.Parameter(
            displayName = "Block Group State FIPS Field",
            name = "state_fips_field",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )
        param4.parameterDependencies = [param3.name]

        param5 = arcpy.Parameter(
            displayName = "Block Group Polygon GEOID Field",
            name = "BG_poly_geoid_field",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )
        param5.parameterDependencies = [param3.name]


        param6 = arcpy.Parameter(
            displayName = "Census Block Group Race Table",
            name = "census_race_feature",
            datatype = "GPTableView",
            parameterType = "Required",
            direction = "Input"
            )

        param7 = arcpy.Parameter(
            displayName = "Census Race Table State FIPS field",
            name = "censu_race_state_fips_field",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )
        param7.parameterDependencies = [param6.name]

        param8 = arcpy.Parameter(
            displayName = "Census Race Table GEOID field",
            name = "censu_race_geoid_field",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )
        param8.parameterDependencies = [param6.name]

        param9 = arcpy.Parameter(
            displayName = "Output Feature Class",
            name = "out_fc",
            datatype = "DEFeatureClass",
            parameterType = "Required",
            direction = "Output"
            )
        
        params = [workspace, param1, param2, param3, param4, param5, param6, param7, param8, param9]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        import arcpy
        import os

        arcpy.env.workspace = parameters[0].valueAsText

        dafc = parameters[1].valueAsText
        dafld = parameters[2].valueAsText
        bgfc = parameters[3].valueAsText
        bgfld = parameters[4].valueAsText
        bggeoid = parameters[5].valueAsText
        census_race_tbl = parameters[6].valueAsText
        cenfips = parameters[7].valueAsText
        cengeoid = parameters[8].valueAsText
        out_fc = parameters[9].valueAsText

        # Creating cross walk for state abbrevation to FIPS
        stateDict = {
            "AL" : "01",
            "AK" : "02",
            "AZ" : "04",
            "AR" : "05",
            "CA" : "06",
            "CO" : "08",
            "CT" : "09",
            "DE" : "10",
            "DC" : "11",
            "FL" : "12",
            "GA" : "13",
            "HI" : "15",
            "ID" : "16",
            "IL" : "17",
            "IN" : "18",
            "IA" : "19",
            "KS" : "20",
            "KY" : "21",
            "LA" : "22",
            "ME" : "23",
            "MD" : "24",
            "MA" : "25",
            "MI" : "26",
            "MN" : "27",
            "MS" : "28",
            "MO" : "29",
            "MT" : "30",
            "NE" : "31",
            "NV" : "32",
            "NH" : "33",
            "NJ" : "34",
            "NM" : "35",
            "NY" : "36",
            "NC" : "37",
            "ND" : "38",
            "OH" : "39",
            "OK" : "40",
            "OR" : "41",
            "PA" : "42",
            "RI" : "44",
            "SC" : "45",
            "SD" : "46",
            "TN" : "47",
            "TX" : "48",
            "UT" : "49",
            "VT" : "50",
            "VA" : "51",
            "WA" : "53",
            "WV" : "54",
            "WI" : "55",
            "WY" : "56",
            "PR" : "72" }

        daStates = set([row[0] for row in arcpy.da.SearchCursor(dafc, (dafld))])
        arcpy.AddMessage("Number of states found: " + str(len(daStates)))
        
        # Creating empty list to hold each state's table
        tmp_tbls=[]
        tmp_fcs=[]
        # Looping through states in the dataset.
        for k,i in enumerate(daStates):
            arcpy.AddMessage("Joining features and merging probabilites in: " + i)
            if i in stateDict:
                fips = stateDict[i]
                arcpy.MakeFeatureLayer_management(dafc, "data_"+i, '"'+dafld+'" = \''+i+'\'') 
                arcpy.MakeFeatureLayer_management(bgfc, "bg_"+i, '"'+bgfld+'" = \''+fips+'\'')
                arcpy.MakeTableView_management(census_race_tbl, "census_"+i, '"'+cenfips+'" = \''+fips+'\'' )

                # Performing Spatial Join for the state
                arcpy.SpatialJoin_analysis("data_"+i, "bg_"+i, 'temps_'+i, 'JOIN_ONE_TO_ONE', 'KEEP_ALL','','WITHIN')

                # Converting feature class to table view so we can perform a join
                arcpy.MakeTableView_management('temps_'+i, "temptbl_"+i)

                # Merging in Block Group  probabilites
                arcpy.AddJoin_management("temptbl_"+i, bggeoid, "census_"+i, cengeoid, "KEEP_ALL") 

                # Adding feature class and table view to list
                tmp_fcs.append('temps_'+i)
                tmp_tbls.append('temptbl_'+i)

        # Reducing temp tables together
        if len(daStates) > 1:
            arcpy.AddMessage("Reducing features...")
            arcpy.Merge_management(tmp_tbls, out_fc)
        else:
            arcpy.AddMessage("Only one state in dataset, no reduce needed...")
            arcpy.CopyRows_management (tmp_tbls[0], out_fc)

        # Deleting the temp feature classes
        arcpy.AddMessage("Deleting temporary files...")
        for i in tmp_fcs:
            arcpy.Delete_management(i)
        return

class Surname_Proxy(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Surname Proxy"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        workspace = arcpy.Parameter(
            displayName = "Geodatabase",
            name = "gdb",
            datatype = "DEWorkspace",
            parameterType = "Required",
            direction = "Input")
        workspace.defaultEnvironmentName = "workspace"

        param1 = arcpy.Parameter(
            displayName = "Input Feature",
            name = "in_feature",
            datatype = "GPTableView",
            parameterType = "Required",
            direction = "Input"
            )

        param2 = arcpy.Parameter(
            displayName = "Surname Field",
            name = "surname_field",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )

        param2.parameterDependencies = [param1.name]
        param2.filter.list = ["Text"]

        param3 = arcpy.Parameter(
            displayName = "Census Surname Table",
            name = "census_feature",
            datatype = "GPTableView",
            parameterType = "Required",
            direction = "Input"
            )

        param4 = arcpy.Parameter(
            displayName = "Census Surname Field",
            name = "census_field",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )
        param4.parameterDependencies = [param3.name]

        param5 = arcpy.Parameter(
            displayName = "Output Feature Class",
            name = "out_fc",
            datatype = "DEFeatureClass",
            parameterType = "Required",
            direction = "Output"
            )
        
        params = [workspace, param1, param2, param3, param4, param5]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        import arcpy
        import os

        arcpy.env.workspace = parameters[0].valueAsText

        tbl = parameters[1].valueAsText
        lname_tbl = parameters[2].valueAsText
        census = parameters[3].valueAsText
        lname_census = parameters[4].valueAsText
        out_tbl = parameters[5].valueAsText


        arcpy.MakeTableView_management(tbl,  "tempLayer")
        arcpy.AddField_management("tempLayer", "Clean_Surname", "TEXT")
        arcpy.AddField_management("tempLayer", "Surname2", "TEXT")


        arcpy.AddMessage("Cleaning surnames...")
        with arcpy.da.UpdateCursor("tempLayer", [lname_tbl, "Clean_Surname", "Surname2"]) as cursor_raw:
            for row in cursor_raw:
                name = row[0]

                # Making surname upper case
                name = name.upper()
                # Removing numbers are symbols
                name = re.sub(r"[,;\\.0-9]", " ", name)
                # Separately removing apostrophes and replacing with no space to account for Irish folk
                name = re.sub(r"[']", "", name)
                # Removing double quotes
                name = re.sub(r'"', ' ', name)
                # Removing common suffixes
                name = re.sub(r" ((JR)|(SR)|(I)|(II)|(III)|(IV)|(MD)|(DDS)|(PHD)) ", " ", name)
                # Removing any remaining lone letters, most likely initials 
                name = re.sub(r" [a-z] ", "", name)
                # Replacing all spaces with non-spaces
                name = re.sub(r" ", "", name)

                # Separating hyphenated last names
                name, sep, lname2 = name.partition("-")
                # Assinging clean names to appropriate columns
                row[1] = name
                row[2] = lname2

                #   UPDATING INPUT TABLE.
                cursor_raw.updateRow(row)
        del cursor_raw, row

        # This tool will only use the first last name. For added functionality to use the second last name
        # as well, follow me on GitHub. Will incorporate in v2.

        # Joining the census surname table to the input table, keeping all features in the Input table, 
        # regardless of match
        arcpy.AddMessage("Merging probabilites...")
        arcpy.AddJoin_management("tempLayer", "Clean_Surname", census, lname_census, "KEEP_ALL") 

        # Creating the final output feature class
        arcpy.AddMessage("Exporting results...")
        arcpy.CopyRows_management("tempLayer", out_tbl)        
        return

class BISG(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "BISG"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        workspace = arcpy.Parameter(
            displayName = "Geodatabase",
            name = "gdb",
            datatype = "DEWorkspace",
            parameterType = "Required",
            direction = "Input")
        
        param1 = arcpy.Parameter(
            displayName = "Input Feature",
            name = "in_feature",
            datatype = "GPFeatureLayer",
            parameterType = "Required",
            direction = "Input"
            )

        workspace.defaultEnvironmentName = "workspace"

        param2 = arcpy.Parameter(
            displayName = "Surname White Field",
            name = "surname_white",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )

        param2.parameterDependencies = [param1.name]

        param3 = arcpy.Parameter(
            displayName = "Surname Black Field",
            name = "surname_black",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )

        param3.parameterDependencies = [param1.name]

        param4 = arcpy.Parameter(
            displayName = "Surname Native American Field",
            name = "surname_nativ",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )

        param4.parameterDependencies = [param1.name]

        param5 = arcpy.Parameter(
            displayName = "Surname Asian Field",
            name = "surname_asian",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )

        param5.parameterDependencies = [param1.name]

        param6 = arcpy.Parameter(
            displayName = "Surname Hispanic Field",
            name = "surname_hispanic",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )

        param6.parameterDependencies = [param1.name]

        param7 = arcpy.Parameter(
            displayName = "Surname Multi Field",
            name = "surname_Multi",
            datatype = "Field",
            parameterType = "Required",
            direction = "Input"
            )

        param7.parameterDependencies = [param1.name]

        param8 = arcpy.Parameter(
            displayName = "Output Feature Class",
            name = "out_fc",
            datatype = "DEFeatureClass",
            parameterType = "Required",
            direction = "Output"
            )

        params = [workspace, param1, param2, param3, param4, param5, param6, param7, param8]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        import arcpy

        arcpy.env.workspace = parameters[0].valueAsText

        probFile = parameters[1].valueAsText

        surname_white = parameters[2].valueAsText
        surname_black = parameters[3].valueAsText
        surname_nativ = parameters[4].valueAsText
        surname_asian = parameters[5].valueAsText
        surname_hispanic = parameters[6].valueAsText
        surname_multi = parameters[7].valueAsText

        out_fc = parameters[8].valueAsText

        here_white    = "here_given_white" 
        here_black    = "here_given_black" 
        here_nativ    = "here_given_nativ" 
        here_asian    = "here_given_asian" 
        here_hispanic = "here_given_hispanic" 
        here_multi    = "here_given_multi"

        geo_white       = "NH_White_alone"
        geo_black       = "NH_Black_alone"
        geo_nativ       = "NH_AIAN_alone"
        geo_asian       = "NH_API_alone"
        geo_hispanic    = "Hispanic_Total"
        geo_multi       = "NH_Mult_Total"

        arcpy.MakeTableView_management(probFile,  "geoLayer")
        arcpy.AddField_management("geoLayer", "BISG_white", "LONG")
        arcpy.AddField_management("geoLayer", "BISG_black", "LONG")
        arcpy.AddField_management("geoLayer", "BISG_nativ", "LONG")
        arcpy.AddField_management("geoLayer", "BISG_asian", "LONG")
        arcpy.AddField_management("geoLayer", "BISG_multi", "LONG")
        arcpy.AddField_management("geoLayer", "BISG_hispanic", "LONG")


        with arcpy.da.UpdateCursor(probFile, [surname_white, surname_black, surname_nativ, 
                                              surname_asian, surname_hispanic, surname_multi, 
                                              here_white, here_black, here_nativ, here_asian, 
                                              here_hispanic, here_multi, geo_white, geo_black, 
                                              geo_nativ, geo_asian, geo_hispanic, 
                                              geo_multi, "BISG_white", "BISG_black", "BISG_nativ",  
                                              "BISG_asian", "BISG_multi", "BISG_hispanic"
                                              ]) as cursor_raw:

            white_surname = row[0]
            black_surname = row[1]
            nativ_surname = row[2]
            asian_surname = row[3]
            hispanic_surname = row[4]
            multi_surname = row[5]

            white_here = row[6]     
            black_here = row[7]     
            nativ_here = row[8]     
            asian_here = row[9]         
            hispanic_here = row[10]
            multi_here = row[11]

            white_geo = row[12]
            black_geo = row[13]
            nativ_geo = row[14]
            asian_geo = row[15]
            hispanic_geo = row[16]
            multi_geo = row[17]

            # u_race = Pr(race|name) * Pr(this block group | race)
            u_white = white_surname * white_here
            u_black = black_surname * black_here
            u_nativ = nativ_surname * nativ_here
            u_asian = asian_surname * asian_here
            u_hispanic = hispanic_surname * hispanic_here
            u_multi = multi_surname * multi_here

            # Calculatin BISG
            pr_white = u_white / (u_white + u_black + u_aian + u_api + u_hispanic + u_mult_other)
            pr_black = u_black / (u_white + u_black + u_aian + u_api + u_hispanic + u_mult_other)
            pr_nativ = u_nativ / (u_white + u_black + u_aian + u_api + u_hispanic + u_mult_other)
            pr_asian = u_asian / (u_white + u_black + u_aian + u_api + u_hispanic + u_mult_other)
            pr_hispanic = u_hispanic / (u_white + u_black + u_aian + u_api + u_hispanic + u_mult_other)
            pr_multi = u_multi / (u_white + u_black + u_aian + u_api + u_hispanic + u_mult_other)

            row[18] = pr_white
            row[19] = pr_black
            row[20] = pr_nativ
            row[21] = pr_asian
            row[22] = pr_hispanic
            row[23] = pr_multi

            cursor_raw.updateRow(row)
        del cursor_raw, row

        arcpy.CopyRows_management ("geoLayer", out_fc)
        return