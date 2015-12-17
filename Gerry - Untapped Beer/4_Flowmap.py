# -*- coding: utf-8 -*-

## Kady Gerry
## Geog 6392
## Project: Step 4
## Create flow map

## This script is modeled after the process described by Sathya Prasad, Brad Simantel,
## and Bob Gerlt of the ESRI Applications Prototype Lab. The process is described in
## two blog posts:
## http://blogs.esri.com/esri/apl/2012/09/12/generating-distributive-flow-maps-with-arcgis/
## http://blogs.esri.com/esri/apl/2013/08/26/flow-map-version-2/
##
## The post provides an ArcMap tool that did not run with the UnTappd data being used in
## this project. There were multiple errors generated when the tool was run, so I have recreated
## the process in order to test along the way.
##
## Update: I tried the tool again after collecting all 53k results, and it works. So, I think
## the there may have been an issue with the number of results I was testing initially (2k)
## being spread over the entire world.


import arcpy


## Set up enviornment variables
arcpy.env.workspace = r'G:\Share\GEOG6293_Programming\Gerry\Project\geoDB.gdb'
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

## Two "for" loops will iterate through potential parameters for the flow map script
## Each iteration will output a line shapefile so they can be compared to determine
## what the best settings are (Result: I like the look of Flow_Map_5_160000)
for i in range(1, 10):
    for j in range(20000, 300000, 20000):
        ## Define inputs and parameters to be used for the flow map
        sourceFC = "DC_poly_proj"
        destinationFC = "Country_ct_proj"
        zField = "Join_Count"
        destinationWeight = i
        sourceWeight = 10 - destinationWeight
        c_Size = j
        outputFC = "Flow_Map_" + str(i) + "_" + str(j)
        
        ## Define extent parameters. These values were modified from the original script
        ## to keep the processing extent slightly (one cell size) smaller than the true
        ## extent. This will keep flows from 'wrapping' across the page edges. This issue
        ## is documented in the ESRI blog posts linked at the beginning of this script.
        destExt = arcpy.Describe(destinationFC).extent
        minx = destExt.XMin + (c_Size + 1)
        miny = destExt.YMin + (c_Size + 1)
        maxx = destExt.XMax - (c_Size + 1)
        maxy = destExt.YMax - (c_Size + 1)
        arcpy.env.extent = arcpy.Extent(minx, miny, maxx, maxy)
        extlist = arcpy.env.extent
        maxextdim = max(arcpy.env.extent.width, arcpy.env.extent.height)
        
        ## Define spatial reference parameter
        desc = arcpy.Describe(sourceFC)
        spatref = desc.spatialReference
        
        print "Files imported and extent setup"
        
        ## Define slice value (from original script: SliceValue is used to control the
        ## magnitude of values in the cost surface and normalize the individual cost
        ## surface values so weights have significant effect.)
        sliceValue = int(maxextdim / c_Size)
        
        
        ## Define an evelope polygon (from original script: used later for mask and
        ## background fill). The process in the original script involved casting
        ## extlist as a string and then splitting. I prefer using the properties of
        ## extlist (XMin, YMin, etc) rather than the method in the original script,
        ## but the next step of creating the envelope polygon requires strings, so
        ## convert the values to strings in this step.
        leftEx = extlist.XMin
        botEx = extlist.YMin
        rightEx = extlist.XMax
        topEx = extlist.YMax
        ## LL, UL, UR, UL coordinates to be used to generate the polygon
        polyinfo = [[leftEx, botEx], [leftEx, topEx], [rightEx,topEx], [rightEx,botEx]]
        
        ## Create the envelope polygon
        # features = []
        # for feature in polyinfo:
        #    features.append(arcpy.Polygon(arcpy.Array([arcpy.Point(*coords) for coords in feature]),spatref))
        
        ## Original version (above) generates an error. Corrected the following:
        ## Reformatted as an iterator outside of the append function 
        ## Skip the (unnecessary) appending to the feature list (it would only have one value in this case)
        ## The arcpy.Polygon function requires an arcpy.Array
        ## The arcpy.Polygon function requires the first and last point to be the same
        ## The spatial reference parameter (spatref) is not recognized by the CopyFeatures_management function
        
        points = arcpy.Array()
        for point in polyinfo:
            points.append(arcpy.Point(point[0],point[1]))
        points.append(points[0])
        envPoly = arcpy.Polygon(points)
        extenvelope = "temppoly"
        arcpy.CopyFeatures_management(envPoly, extenvelope)
        arcpy.DefineProjection_management(extenvelope, spatref)
        print "Envelope polygon created"
        
        ## Original script includes conditions for impassable features, but I don't need
        ## to use this feature, so I've intentionally left it out of this script.
        
        ## Create mask polygon. Since no impassable features are being used, this is the
        ## same as the processing extent.
        polymask = extenvelope
        mskgrd = "mskgrd"
        ## Add a field to contain the GridValue
        arcpy.AddField_management(polymask, "GridVal", "DOUBLE")
        ## GridVal is 0
        arcpy.CalculateField_management(polymask, "GridVal", 0)
        ## Convert to a raster with the appropriate cell size (c_Size) we chose earlier
        arcpy.FeatureToRaster_conversion(polymask, "GridVal", mskgrd, c_Size)
        
        ## Set raster processing mask
        arcpy.env.mask = polymask
        print "Mask polygon created"
        
        ## Convert 'source' polygon to point, which will be the center of a DC outline polygon
        sourcePoint = "tempsrcpt"
        arcpy.FeatureToPoint_management(sourceFC, sourcePoint, "CENTROID")
        
        ## Convert the destination polygons (countries) to points - each will be the center of the corresponding country
        destinationPoints = "tempdestpts"
        arcpy.FeatureToPoint_management(destinationFC, destinationPoints)
        print "Source and destination polygons converted to point features"
        
        ## Remove destination points that have z-value (number of UnTappd ratings in that country) of NULL or 0
        with arcpy.da.UpdateCursor(destinationPoints, str(zField)) as cursor:
            for row in cursor:
                if (row[0] is None or row[0] == 0):
                    cursor.deleteRow()
        print "Removed polygons (countries) with no rankings"
        
        ## Create the cost raster
        ## First component is Euclidean distance from source (DC) to all other points
        sourceDistanceRaster = arcpy.sa.EucDistance(sourcePoint)
        ## Covert the first component into distance increments (slices), multiplied by sourceWeight to determine where the lines will merge
        sourceSlicedRaster = arcpy.sa.Slice(sourceDistanceRaster, sliceValue) * sourceWeight
        ## Second component is a 'distance to nearest other' point, using the center points of the countries
        destinationDistanceRaster = arcpy.sa.EucDistance(destinationPoints)
        ## Covert the second component into distance increments, multiplied by destinationWeight to determine where the lines will merge
        destslice = arcpy.sa.Slice(destinationDistanceRaster, sliceValue) * destinationWeight
        ## Add the two components together toget an overall cost raster
        sumSlicedRaster = sourceSlicedRaster + destslice
        
        ## Compute costdistance from source point to each other point using the cost raster created above
        initcostbklnk = "initbklnk"
        initcostdist = arcpy.sa.CostDistance(sourcePoint, sumSlicedRaster)#, out_backlink_raster = initcostbklnk)
        print "Cost raster created"
        
        ## Convert the country center point features to a raster
        destptras = "destptras"
        arcpy.FeatureToRaster_conversion(destinationPoints, zField, destptras, c_Size)
        
        ## Calculate the flow direction based on the cost raster
        flowdir = "flowdir"
        arcpy.gp.FlowDirection_sa(initcostdist, flowdir, "FORCE")
        
        ## Calculate cumulative accumulation (merging of the lines at the source)
        flowaccum = "flowaccum"
        arcpy.gp.FlowAccumulation_sa(flowdir, flowaccum, destptras, "INTEGER")
        
        ## Covert the cumulative flow to integer values
        intflowaccum = arcpy.sa.Int(arcpy.sa.Raster(flowaccum))
        ## Define NULL values on the raster
        flownull = arcpy.sa.SetNull(intflowaccum, intflowaccum, "VALUE = 0")

        ## Save to line shapefile
        arcpy.sa.StreamToFeature(flownull, flowdir, outputFC, "SIMPLIFY")
        print "Flow map completed!"

        ## Clean up the temporary raster files so we don't fill up the server with rasters
        cleanuplist = [initcostbklnk, initcostdist, destptras, flowdir, flowaccum,
                       intflowaccum, sumSlicedRaster, destinationDistanceRaster, sourceDistanceRaster,
                       destslice, sourceSlicedRaster]
        for ras in cleanuplist:
            if arcpy.Exists(ras):
                arcpy.Delete_management(ras)

        print "Temp file cleanup completed"

print "Script 4 is now complete"
