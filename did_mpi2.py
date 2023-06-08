#!/usr/bin/env python

from mpi4py import MPI
import sys
import os
import io
import time
from subprocess import call
import hashlib


start_time = time.time()

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
num_processes = comm.Get_size()
name = MPI.Get_processor_name()
hasher_1 = hashlib.md5()
hasher_2 = hashlib.md5()

image_files = []
add_on = {}
hashes = {}
param_file = {}
images_file = open("images_mpi", "w")

try:
	f = open(sys.argv[1], "rb")
	result = f.read()
	hasher_2.update(result)
	f.close()
	file_hash = hasher_2.hexdigest()
	param_file.update({sys.argv[1] : file_hash})
except:
	pass

if(len(param_file) > 0):
	req = comm.isend(param_file, dest=0, tag=12)


try:
	jpg = call(["find", "-name", "*.jpg"], stdout=images_file)
	png = call(["find", "-name", "*.png"], stdout=images_file)

except Exception as e:
	print(e)

images_file.close()

images_file = open("images_mpi", "r")

for line in images_file:
	image_files.append(line.rstrip("\n"))

images_file.close()

for im in image_files:
	hasher_1 = hashlib.md5()
	hfile = open(im, "rb")
	result = hfile.read()
	hasher_1.update(result)
	hfile.close()
	hashes[im] = hasher_1.hexdigest()
	

num_received = 0

if rank == 0:
	print("Collecting file hashes for process " + str(rank) + " on " + name + ".")

	while num_received < (num_processes - 1):
		req_2 = comm.irecv(source=MPI.ANY_SOURCE, tag=11)
		add_on = req_2.wait()

		if(len(add_on) > 0):
			for key, value in add_on.items():
				match = 0 
				for k in hashes.keys():
					if(key == k):
						match += 1
						break
				if match == 0:
					hashes.update({key : value})

			add_on = {}
			num_received += 1


	req_3 = comm.irecv(source=MPI.ANY_SOURCE, tag=12)
	param_file = req_3.wait()
	file_name = param_file.keys()[0]
	file_hash = param_file.values()[0]

	duplicate = 0

	for key, value in hashes.items():
		if(file_hash == value) and (file_name != key.lstrip("./")):
			print("Duplicate image found! " + str(key))
			duplicate += 1

	if duplicate == 0:
		print("There's no duplicate!")

else:
	print("Sending file hashes from process " + str(rank) + " on " + name + ".")
	req = comm.isend(hashes, dest=0, tag=11)
if rank == 0:
	print("--- %f seconds ---" %(time.time() - start_time))
