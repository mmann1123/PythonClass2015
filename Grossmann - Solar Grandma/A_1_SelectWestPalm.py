# Code: A_1_Select_WestPalm.py
# Coder : Max Grossman
# Description : Selects WestPalm from cntbnd_jul11 layer and outputs single WestPalm shp

# Contents
#	A. Set Environment
#	B. Setting Selection Criteria
#	C. Create New Feature Layer
#	D. Make Selection
#	E. Save Selection to New Layer

#%% A. Set Environment 
import arcpy
arcpy.env.workspace = "G:\Share\GEOG6293_Programming\Grossman\Florida_FinalProject.gdb"
arcpy.env.overwriteOutput = True

#%% B. Setting Selection Criteria

# We will use this selection criteria to select the West Palm County from cntbnd_jul11
# Note, cntbnd_jul11 is a shapefile with all counties in florida.

countySQL = " NAME = 'PALMBEACH' "

#%% C. Create New Feature Layer

# With countySQL set, we can use it to create a WestPalm shapefile with it.

# Makes Feature Layer from cntbnd_jul11 using countySQL and call it WestPalm
arcpy.MakeFeatureLayer_management("cntbnd_jul11", "WestPalm")

# Save temp WestPalm lyr to permanent WestPalm.lyr
arcpy.SaveToLayerFile_management('WestPalm','WestPalm')



