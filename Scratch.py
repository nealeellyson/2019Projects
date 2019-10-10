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
import matplotlib.pyplot as plt

mfile = []
metro = {}
for filename in glob.glob("metro/*"):
    metro[filename[6:-4]] = pd.read_csv(filename) # Using filenames w/out path and file type as dictionary keys
    mfile.append(filename[6:-4])  # Create index of filename strings
print('metro data finsished')


ofile = []
oes = {}
for filename in glob.glob("oes/*"):
    oes[filename[4:-5]] = pd.read_csv(filename) # Using filename string w/out path and file type as dictionary keys
    ofile.append(filename[4:-5]) # Create index of filename strings
    print(f'{filename} data finsished')
print('oes data finsished')


for filename in glob.glob("oes/*"):
    df = oes[filename[4:-5]] 
    names=df['WAFER_ID'].unique().tolist() # Get a list of WaferIDs
    Wafer = {}
    for i in range(len(names)):
        Wafer[i] = df.loc[df.WAFER_ID == names[i]] # Create new dataframe of only 1 WaferID
    print(f'There are {len(names)} wafers in this data set')



data = oes[filename[4:-5]]
UniqueNames = data.WAFER_ID.unique()
DataFrameDict = {elem : pd.DataFrame for elem in UniqueNames}
t_sec = {}
for i,key in enumerate(DataFrameDict.keys()):
    Wafer[i] = pd.DataFrame.from_dict(data[:][data.WAFER_ID == key]) # Create DataFrame for specific wafers
    delt = Wafer[i]['TimeStamp']-Wafer[i]['RunStartTime'] # Find timedelta for a wafer
    t_sec[i] = delt.dt.total_seconds() # Put timedelta into seconds



OES_col = [col for col in Wafer[i].columns if 'OES' in col] #Create list of all intensity columns w/rt element



fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
for x in range (len(UniqueNames)):
    for y in range (len(OES_col)):
        ax.plot(t_sec[x],Wafer[x][OES_col[y]])

