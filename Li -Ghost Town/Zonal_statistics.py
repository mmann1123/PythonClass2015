# -*- coding: utf-8 -*-
# Created on Mon Dec 14 20:26:57 2015
# Zonal_statistics.py
# Use Zonal statistics tool for DMSP/OLS image 
# @author: Li


# Import arcoy and set the default workspace
import arcpy

arcpy.CheckOutExtension("Spatial")

from arcpy import env
from arcpy.sa import *
env.workspace = r"G:\Share\GEOG6293_Programming\Li\Final_project\DMSP"

# Declare a tuple name and assign varaibles
inZoneData="Ordos.shp"
zoneField = "County"

# Declare a tuple name and assign varaibles
inValueRaster =("2007_clip.tif","2009_clip.tif","2011_clip.tif","2013_clip.tif")
outTable =("Zonal_2007.dbf","Zonal_2009.dbf","Zonal_2011.dbf","Zonal_2013.dbf")

# Use for loop to calculate zonal statistics for the tuple named inValueRaster
for index in range(len(inValueRaster)):
    outZSaT = ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster[index], 
                                 outTable[index], "DATA", "SUM")
           