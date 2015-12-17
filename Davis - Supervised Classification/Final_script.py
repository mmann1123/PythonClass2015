###############################################################################
#
# Eleanor Davis | Final Project | 12/16/2015
#
# This program is based on user interaction with the program. 
# It requires inputs and answers from the user to make decisions.
# There are several modules that need to be installed.
# The images2gif and PIL modules especially will need to be installed as
# seen below.
#
# The object of this program is to conduct user-oriented image processing
# and unsupervised classification. If there are multiple classified images
# the user can choose to display them as a gif for visualization purposes.
#
# Other fun parts of this program are the use of glob.glob and os.path.join.
# Glob.glob produces a list of files that match the specified pattern.
# os.path.join eliminates the need for '//', '/', or '\' when making a path
# name for a file which takes out the chance for error.
#
# Overall, please make sure everything is installed and use either your own,
# or the provided, landsat scenes. Enjoy!
##############################################################################

import arcpy, os, glob, sys, tarfile
from distutils import dir_util
from PIL import Image

#This tries to import modules and if it fails, it installs them either through anaconda or python.
try:
	import images2gif
except:
	if 'Anaconda' in sys.version:
		os.system('conda install images2gif')
	else:
		os.system('pip install images2gif')

try:
	import PIL
except:
	if 'Anaconda' in sys.version:
		os.system('conda install PIL')
	else:
		os.system('pip install PIL')


arcpy.CheckOutExtension("Spatial")

#The runTif function goes through the steps of selecting a landsat scene, selecting the bands, classifying the scenes, and then asking the user what they would like to do next (to gif or not to gif?).
def runTif(tifs,directory):
	dirsave= os.path.join(directory,'Classified')
	#creates a list from past iterations of the for loop until the user chooses a scene - prevents needing to say no to the same scene multiple times
	usedIDs=[]
	for file in tifs:
		#The landsatID is the identifying and unique digits of any landsat file
		landsatID=file[file.rfind('LC8'):file.rfind('_')]
		if landsatID in usedIDs:
			continue
		print "I found landsat scene: " + landsatID + ", is that the scene you would like to process? (y/n)"
		idAnswer=raw_input('>')
		if idAnswer == 'y':
			break
		usedIDs.append(landsatID)
		if idAnswer == 'n':
			print "You didn't select any of the valid files! Exiting..."
		sys.exit()

	#Prints the different bands with that landsatID and asks whether to keep them or not. 		
	#Glob.glob returns a list of file names matching the specified pattern
	chosenFiles=glob.glob(os.path.join(directory,landsatID+'*'))
	print "I found the following bands for scene " + landsatID

	#iterates through chosenFiles and asks to keep the file
	for i in range(len(chosenFiles)): 
		file=chosenFiles[i]
		#just prints from after _ to the . in the file name (easier for band identification)
		print "Would you like to use " + file[file.rfind('_')+1:file.rfind('.')] + "?(y/n)" 
		keepAnswer=raw_input('>')
		while keepAnswer != 'y' and keepAnswer != 'n':
			print "Please enter a valid input (y/n)"
			keepAnswer = raw_input('>')
		if keepAnswer == 'n' or 'B8' in file:
			#This changes the file name to zero to easily remove.
			chosenFiles[i]='0' 
		elif keepAnswer == 'y':
			continue
		#recreates the list chosenFiles with just the files not equal to zero (list comprehension)
		finalFiles=[file for file in chosenFiles if file != '0']  

	inRaster = finalFiles
	print "How many classes would you like in your classification? Please enter a numeric value."

	#Asking for the number of classes input allows for further user interaction
	classes=input('>') 

	print "Commencing unsupervised classification..."

	if not os.path.exists(os.path.join(directory,'Classified')):
		dir_util.mkpath(os.path.join(directory,'Classified'),verbose=False)
	
	#Unsupervised classification is done through arcpy's spatial analyst tool using the specified raster and number of classes
	outUnsupervised = arcpy.sa.IsoClusterUnsupervisedClassification(inRaster, classes)
	outUnsupervised.save(os.path.join(dirsave,landsatID+'_UC.tif'))

	print "Would you like to classify another image? (y/n)"

	#This is where the user can either decide to do more classifications or end the classification cycle
	#If the classification cycle is ended, they can either create a gif out of the classified files for visualization purposes or end the program
	restart=raw_input('>')
	while restart != 'y' and restart != 'n':
		print "Please enter a valid input (y/n)"
		restart = raw_input('>')
	if restart == 'n':
		#To gif or not to gif section
		print "Would you like to create a gif out of your classified files?"
		while gif != 'y' and gif != 'n':
			print "Please enter a valid input (y/n)"
			gif = raw_input('>')
		if gif == 'y':
			try:
				gif()
			except:
				"Sorry the GIF as failed."
				sys.exit()
		elif gif == 'n':
			print "Enjoy your new classification files!"
			sys.exit()
	#Restarts the runTif function for another classification
	elif restart == 'y':
		runTif()

	
	
#This function unpacks the .gz into .tar and then extracts all of the bands into the directory
#It then runs the runTif function
def runTar(gz,directory):
	print "Extracting tar files..."
	for file in gz:
		tar = tarfile.open(os.path.join(directory,file))
		tar.extractall(os.path.join(directory,'gzFiles'))
		tar.close()
		tarFiles=glob.glob(os.path.join(directory,'gzFiles','*.TIF'))
		runTif(tarFiles,os.path.join(directory,'gzFiles'))
		
#This function creates a gif out of the classified files using the images2gif function from the PIL module
#Be sure to install PIL and images2gif!!!
def gif():
	gifFiles=glob.glob(os.path.join(directory,'Classified','*.TIF'))
	images=[Image.open(file) for file in files]
	#Duration in writeGif is in seconds
	images2gif.writeGif(os.path.join('Classified','Classification.gif'),images,duration=1)
	print "Enjoy your GIF!"
	sys.exit()

#This function sets the base for the entire program.
#In this function, the program searches a the workspace folder (wherever the script is saved) for .Tif and .gz files.
#The user then has the option of using the .Tif or .gz files which sends them to those functions.
def main():
	arcpy.env.workspace= os.path.join(os.path.dirname(os.path.realpath(__file__)),'Data')
	directory= os.path.join(os.path.dirname(os.path.realpath(__file__)),'Data')

	#creates variables that contain file names with the specified extensions
	tifFiles=glob.glob(os.path.join(directory,'*.TIF'))
	tarFiles=glob.glob(os.path.join(directory,'*.gz'))

	#if program finds both tifFiles and gzFiles in the folder than it will do:
	if tifFiles and tarFiles:
		print "I have detected both .TIF and .gz file(s). Press 1 to use the .TIF(s) and 2 to use the .gz(s)."
		fileAnswer=raw_input('>')
		while fileAnswer != '1' and fileAnswer != '2':
			print "Please enter a valid choice!"
			fileAnswer=raw_input('>')
		if fileAnswer=='1':
			runTif(tifFiles,directory) #this passes the argument tifFiles to runTif
		else:
			runTar(tarFiles,directory) #passes tarFiles argument
	elif tifFiles and not tarFiles:
		runTif(tifFiles)
	elif tarFiles and not tifFiles:
		runTar(tarFiles)
	else:
		print "Did not find any .Tif or .gz tifFiles to process. Exiting..."
		sys.exit(0)


if __name__=="__main__":
	main()
