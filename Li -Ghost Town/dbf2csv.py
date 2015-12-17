# -*- coding: utf-8 -*-
# Created on Tue Dec 15 13:01:21 2015
# Python script to convert DBF database file to CSV
# First download dbfpy: http://sourceforge.net/projects/dbfpy/files/latest/download?source=files 
#                                                       Then install: sudo python setup.py install
# dbf2csv.py
# Code taken and adapted from https://gist.github.com/bertspaan/8220892
# @author: Li

import csv
from dbfpy import dbf
import os
import sys

arcpy.gp.overwriteOutput = True

for files in os.listdir("G:\Share\GEOG6293_Programming\Li\Final_project\Convert_DBF2_CSV"):
    filename = files
    if filename.endswith('.dbf'):
        print "Converting %s to csv" % filename
        csv_fn = filename[:-4]+ ".csv"
        with open(csv_fn,'wb') as csvfile:
            in_db = dbf.Dbf(filename)
            out_csv = csv.writer(csvfile)
            names = []
            for field in in_db.header.fields:
                names.append(field.name)
            out_csv.writerow(names)
            for rec in in_db:
                out_csv.writerow(rec.fieldData)
            in_db.close()
            print "Done..."
    else:
      print "Filename do not end with .dbf"
