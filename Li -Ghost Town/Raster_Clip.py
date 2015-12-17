# -*- coding: utf-8 -*-
# Created on Mon Dec 14 16:49:54 2015
# Use the County boundary clip the DMSP/OLS night light data 
# Raster_Clip.py
# @author: Li

# import arcpy and set the default workspace
import arcpy


arcpy.env.workspace =r"G:\Share\GEOG6293_Programming\Li\Final_project\DMSP"

# Use the tuple store DMSP/OLS raster layer 
InputRasterLayer = ("2007.tif","2009.tif","2011.tif","2013.tif")

OutputRasterLayer = ("2007_clip.tif","2009_clip.tif","2011_clip.tif","2013_clip.tif")

# Use the Ordos boundry layer clip each DMSP/OLS raster layer 
for Layers in range(len(InputRasterLayer)):
    arcpy.Clip_management(InputRasterLayer[Layers],"#",OutputRasterLayer[Layers],"Ordos.shp","0","ClippingGeometry")