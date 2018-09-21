#!/usr/bin/env python3

import os
import gc

path = os.getcwd()
dirs = os.listdir(path)

scripts = [x for x in dirs if x.startswith('Band')]
scripts.sort()

# print(scripts)

for file in scripts:
	# print('python3 ' + path + '/' + file)
	os.system('python3 ' + path + '/' + file)
	gc.collect()