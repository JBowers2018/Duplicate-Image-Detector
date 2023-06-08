import sys
import os
import time
from PIL import Image, ImageChops
from shutil import copy
from pyspark import SparkContext
from subprocess import PIPE, Popen, check_output, call

start_time = time.time()

sc = SparkContext(appName="MySparkProg")
sc.setLogLevel("ERROR")


if(len(sys.argv) < 2 or len(sys.argv) > 3):
	print("Usage: python3 duplicate_image_detector.py <image_file_name> <optional_search_directory_name>")
	sys.exit(2)

try: 
	image = Image.open(sys.argv[1])
except: 
	print("Error: " + sys.argv[1] + " is not an image. Please provide a valid image file.")
	sys.exit(2)

if(len(sys.argv) == 2): 
	directory_name = "Images/"
else: 
	directory_name = sys.argv[2] + "/"


try:
	image_files = os.listdir(directory_name)
except:
	if(directory_name == "Images/"):
		print("Error: Cannot open default directory \"Images\". Please create this directory or provide a valid one of your own.")
	else:
		print("Error: Cannot open directory \"" + directory_name.rstrip("/") + "\". Please create this directory or provide a valid one.")
	sys.exit(2)


if(os.path.exists("images.txt")): 
	os.remove("images.txt")

text_file = open("images.txt", "a")
for file in image_files:
	text_file.write(file + "\n")

text_file.close()


try:
	tf = call(["/usr/local/hadoop-1.2.1/bin/hadoop", "fs", "-test", "-e", "/user/cc/images.txt"])
	
	df = call(["/usr/local/hadoop-1.2.1/bin/hadoop", "fs", "-rm", "/user/cc/images.txt"], stdout=PIPE)

except:
	pass	


put = call(["/usr/local/hadoop-1.2.1/bin/hadoop", "fs", "-put", "images.txt", "/user/cc/images.txt"], stdin=PIPE, bufsize=-1)

os.remove("images.txt")

images_file = sc.textFile("hdfs://10.56.1.10:54310/user/cc/images.txt")
image_files = images_file.collect()

images = []
duplicate_count = 0


for file in image_files:
	try:
		images.append(Image.open(directory_name + str(file)))
	except:
		print("Cannot open " + str(file))
		pass


for img in images:
	try:
		difference = ImageChops.difference(image, img)

		if not difference.getbbox(): 
			print("Duplicate image! " + img.filename)
			duplicate_count += 1
	except:
		pass

if(duplicate_count == 0):
	print("Not a duplicate! Adding to " + directory_name.rstrip("/") + ".")
	copy(image.filename, directory_name)
#	put = call(["/usr/local/hadoop-1.2.1/bin/hadoop", "fs", "-put", image.filename, "/user/cc/Images/"], stdin=PIPE, bufsize=-1)

print("--- %s seconds ---" %(time.time() - start_time))
