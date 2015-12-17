# Code: B_1_NormalizeInverseFishnet.py
# Coder: Max Grossman
# Description: Normalizes Fields in Fishnet and generates inverse dist field
# for powerlines and roads

# Contents
#   A. Set Environment
#   B. Add and calculate new normalized fields
#   C. Add and calculate inverse normalized fields

#%% Set Environment

import arcpy
arcpy.env.workspace = r"G:\Share\GEOG6293_Programming\Grossman\Florida_FinalProject.gdb"
arcpy.env.overwriteOutput = True

#%% B. Add and Calculate new normalized fields

# Before I calculate the fields, I need to add them. I use Addfield_management

# The function takes 3 arguments: 
#   1) the shapefile we add the field to
#   2) the name of the new field
#   3) the data type for the new field

arcpy.Addfield_management("WestPalmFishNet", "NormDistRoad", 'FLOAT')
arcpy.Addfield_management("WestPalmFishNet", "NormPwrDist", 'FLOAT')
arcpy.Addfield_management("WestPalmFishNet", "NormDistCit", 'FLOAT')

# First I set variables
# inTab is the shp where these fields exist
inTab = "WestPalmFishNet"
# expression is the function i will use to calculate the normalized values.
# each expression uses the same function Normalizer(); it takes a field as
# its argument. Note, that the field needs to be passed through the float
# function when passed through as an argument. Also, fields are surrounded by
# exclaimation points

expression_cit = "Normalizer(float(!Cit_DIST!))"
expression_rds = "Normalizer(float(!Rds_DIST!))" 
expression_pwr = "Normalizer(float(!Pwr_DIST!))"


# Next I create the codeblock that corresponds with each field. I must do this
# becuase they each have their own specific maximum valeus that cannot be
# taken from the general code. This is because the function is a string.


codeblock_rds = """def Normalizer(Rds_DIST):
    rds = Rds_DIST
    rdsMin = float(0)
    rdsRng = float(29879.68916)
    rds_transform = rds - rdsMin
    rds_norm = rds_transform / rdsRng
    return rds_norm"""
    
# first I define the Normalizer function
# next I set some local variables
#   First is a rds variable to the RoadsInvDis field value passed through
#   Second is a rdsMin varaible that holds the minimum value for the field
#   Third is the rdsRng variable that holds the range of the field
# with local variables, I compute the nominator of the normalizer fraction
#   to do this I set rds_transform to rds - rdsMin
# next I set rds_norm variable to rds_transform / rdsRng
# with a normalized value = rds_norm, I return it to CalculateField_management
# the following two codeblocks do the same calculations, but with different
# fields as inputs, and different Maxmimums and Minimums
# Note, that these Maximums and Minimums were found by:
#   First exporting the FishNetWestPalm shp
#   Opening it in QGIS and exporting it as a .csv
#   Opening that .csv in excel and running a quick max() and min() function
#       over the fields of interst. using the attribute table over
#       the 7 million polygons in ArcMap was unbearably slow so I used
#       this work around.
    
codeblock_pwr = """def Normalizer(Pwr_DIST):
    pwr = Pwr_DIST
    pwrMin = float(0)
    pwrRng = float(17340.8)
    pwr_transform = pwd - pwrMin
    pwr_norm = pwr_transform / pwrRng
    return pwr_norm"""
    
codeblock_cit = """def Normalizer(Cit_DIST):
    cit = CitinvDis    
    citMin = float(0)
    citRng = float(39334.80954)
    cit_transform = cod - citMin
    cit_norm = cit_transform / pwrRng
    return cit_norm"""
 
# With each expression and codeblock I can run CalculateField_management for
# the function takes 5 arguments in this case
#   1) the shapefile where the field is located
#   2) the field we are calculating
#   3) the expression that will calculate the field
#   4) The scripting language we use to use our code block. 
#       this is a string "PYTHON_9.3"
#   5) the codeblock that defines our calculation
 
arcpy.CalculateField_management(inTab, "NormDistRoad", expression_rds, "PYTHON_9.3", codeblock_rds)
arcpy.CalculateField_management(inTab, "NormPwrDist", expression_pwr, "PYTHON_9.3", codeblock_pwr)
arcpy.CalculateField_management(inTab, "NormDistCit", expression_cit, "PYTHON_9.3", codeblock_cit)

# Once this is complete, use ArcCatelog to check that it works and the new field is there.

#%% C. Add and calculate inverse normalized fields

# With the three normalized fields calculated, we now can calculat fields with
# values inverse to those in NormDistRoad and NormPwrDist

# Before we can calculate these fields, we need to make them! 
# This is the same process for adding normalized value fields.

arcpy.Addfield_management("WestPalmFishNet", "RoadsInvDis", 'FLOAT')
arcpy.Addfield_management("WestPalmFishNet", "PWLInvDis", 'FLOAT')

# With the new fields created, which verify in the gdb with ArcCatelog, we 
# can calculate inverse fields.

# First we set the inputs for the calculate fields function
inTab = "WestPalmFishNet"
# We set our expression, here I made one called FlipValue(). Similar to 
# last time, I make it specific to Rds and Pwr. It takes both features'
# normalized fields
expression_InvRds = "FlipValue(float(!NormDistRoad!))"
expression_InvPwr = "FlipValue(float(!NormPwrDist!))"

# Next I define fields' respective code blocks.
codeblock_InvRds = """def FlipValue(NormDistRoad):
    InvDist = NormDistRoad
    
    dist_to_min = InvDist - float(0)
    dist_to_max = float(1) - InvDist

    if dist_to_min < dist_to_max:
        InvDist = float(1) - dist_to_min
    if dist_to_min > dist_to_max:
        InvDist = 0 + dist_to_max
    else:
        InvDist = InvDist
    
    return InvDist """ 
    
# first I define three local variables
#   first is InvDist, the field value
#   second is dist_to_min, the distance between InvDist and 0
#   third is dist_to_max, the distance between 1 and InvDist
# second I ask an if else argument
#   first, if dist_to_min is greater than dist_to_max, then I set 
#       InvDist to 1 - the dist_to_min, this effectively reflect a low
#           to the opposite side of a numberline between 0 and 1, keeping
#           an equal distance to the closest end of the number line
#   second, I ask if dist_to_min is greater than dist_to_max
#       if true, InvDst = 0 + dist_to_max, which effectively flips a high
#           to the opposite side of a numberline between 0 and 1, keeping
#           an equal distance to the closest end of the number line.
# third, the else statement is the same as asking if dist_to_min = dist_to_max
#   if the two are equal, then the value is 0.5, so the value stays the same.
# After one of these arguments is proven true with InvDist, it is returned
# to CalculateField_management
    
codeblock_InvPwr = """def FlipValue(NormPwrDist):
    InvDist = NormPwrDist
    
    dist_to_min = InvDist - float(0)
    dist_to_max = float(1) - InvDist

    if dist_to_min < dist_to_max:
        InvDist = float(1) - dist_to_min
    if dist_to_min > dist_to_max:
        InvDist = 0 + dist_to_max
    else:
        InvDist = InvDist
    
    return InvDist """ 

# With all inputs, I can calculate the InvDist fields. The arguments are the
# same as they were in the above example 

arcpy.CalculateField_management(inTab, "RoadsInvDis", expression_InvRds, "PYTHON_9.3", codeblock_InvRds)
arcpy.CalculateField_management(inTab, "PWLInvDis", expression_InvPwr, "PYTHON_9.3", codeblock_InvPwr)

# After each of the fields are calculated, check ArcCatelog to see new fields.
