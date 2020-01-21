#!/usr/bin/env python
# coding: utf-8

# 5030-22 STI INTEGRATED DRY ETCH
# 1230-22 STI INTEGRATED DRY STRIP THK 
# Parameter:
# 5030-22 STI NITRIDE DRY ETCH/THK_OXIDE2_NCHK 
# 
# 1230-53 SPACER NITRIDE DRY STRIP THK 
# 5030-53 SPACER NITRIDE DRY ETCH
# Parameter:
# 5030-53 SPACER NITRIDE DRY ETCH/THK_NITRIDE_PASS 
# 
# 3500-GH CONTACT OXIDE DRY ETCH
# 1230-GH CONTACT PRE METAL CMP THK
# Parameter:
# 5200-GH CONTACT METAL CMP/THK_OXIDE_PASS 
# 

import pandas as pd
import glob
import os
import numpy as np
from datetime import datetime,timedelta
import time
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt

# Retrieving Metro Data from .txt files
mfile = []
metro = {}
for filename in glob.glob("metro/*"):
    metro[filename[6:-4]] = pd.read_csv(filename) # Using filenames w/out path and file type as dictionary keys
    mfile.append(filename[6:-4])  # Create index of filename strings
print('metro data finsished')

# Retrieving OES Data from the .csv files, takes MUCH longer, retrieving specfic columns helps
ofile = []
oes = {}
cols = ['WAFER_ID','RunStartTime', 'TimeStamp','StepID', 'OES_BCl272', 'OES_C516', 'OES_CN387', 'OES_CO483', 'OES_F703', 'OES_H656', 'OES_O777', 'OES_OH309']
for filename in glob.glob("oes/5030-22 STI INTEGRATED DRY ETCH_3.csv"): #5030-22 STI INTEGRATED DRY ETCH_1
    oes[filename[4:-4]] = pd.read_csv(filename, usecols=cols,parse_dates=['RunStartTime', 'TimeStamp'],infer_datetime_format=True)[cols]
    ofile.append(filename[4:-4]) # Create index of filename strings
    print(f'{filename} data finsished')
    data = oes[filename[4:-4]]
UniqueNames = data.WAFER_ID.unique()
DataFrameDict = {elem : pd.DataFrame for elem in UniqueNames}
t_sec = {}
Wafer = {}
for i,key in enumerate(DataFrameDict.keys()):
    Wafer[i] = pd.DataFrame.from_dict(data[:][data.WAFER_ID == key]) # Create DataFrame for specific wafers
    delt = Wafer[i]['TimeStamp']-Wafer[i]['RunStartTime'] # Find timedelta for a wafer
    t_sec[i] = delt.dt.total_seconds() # Put timedelta into seconds
print('Time in seconds completed')


OES_col = [col for col in Wafer[i].columns if 'OES' in col] #Create list of all intensity columns w/rt element
print(OES_col)


fig = plt.figure()
print(len(UniqueNames))
for x in range (len(UniqueNames)):
    fig = plt.figure()
    plt.title(f"{UniqueNames[x]}, {x} of 257") #,f"{len(UniqueNames)}")
    for y in range (len(OES_col)):
        plt.plot(t_sec[x],Wafer[x][OES_col[y]],label = f"{OES_col[y]}")
        plt.xlim(120,145)
        plt.ylim(top=3e5)
    plt.legend()
    plt.show()
