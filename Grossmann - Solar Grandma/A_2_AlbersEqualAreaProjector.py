# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 16:13:09 2015

@author: maxgrossman
"""

# Code: A_4_AlbersNadHarnProjector.py
# Coder: Max Grossman
# Description: Projects all Files Not in appropriate projected and geographic
# coordinate system in appropriate projected and geographic coordinate 
# systems.

# Contents:
#   A. Set Environment
#   B. Create List of Shapefiles to project
#   C. Project Shapefiles
#   D. Project Rasterfile

#%% A. Set Environment

import arcpy
arcpy.env.workspace = r"G:\Share\GEOG6293_Programming\Grossman\Florida_FinalProject.gdb"
arcpy.env.overwriteOutput = True


#%% B. Create Diction of Shapefiles to project

# First I shapefiles in a list

ShpProjList = ['GHI_US','FloridaPopDen','fedland']

#%% C. Project Shapefiles

# Projecting shapefiles is done with the Project_management tool
# To project the files in the list we will use a for loop over the list. 
for Shp in ShpProjList:
    InShp = Shp # The Shp from ShpProjList to be projected
    OutShp = Shp + "_Albers" # The new shapefile after being projected
    OutPCS = r"G:\Share\GEOG6293_Programming\Grossman\FinalProject\AlbersConicalEqualArea.prj"
    # OutPCS is the new projected coordinate system.
    arcpy.ProjectManagement(InShp,OutShp,OutPCS)
    # Finally I run this, and have new correctly projected Shapefiles.

# To verify, check the Florida_FinalProject.gdb

#%% Project Raster

# The Landcover raster for florida needs to be projected correctly
# this is done with ProjectRaster_management()

inRaster = 'FloridaLandCover' # This is the in raster data set
outRaster = inRaster + '_Albers' # This is the out raster dataset
outCoord = r"G:\Share\GEOG6293_Programming\Grossman\FinalProject\AlbersConicalEqualArea.prj"
# outCoord is the PCS the new raster will be projected into
arcpy.ProjectRaster_management(inRaster,outRaster,outCoord)

# To verify, check the Florida_FinalProject.gdb
