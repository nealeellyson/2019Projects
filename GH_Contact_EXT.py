## Plots GH_Contact phase transformation step (4)[can be changed], it's 1st & 2nd Derivative and respective critical points. 
import pandas as pd
import glob
import os
import numpy as np
import dask.dataframe as dd
from datetime import datetime,timedelta
import time
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy import interpolate
from tqdm import tqdm                       # For progress bar, yay!

# Retrieving Metro Data from .txt files
mfile = []
metro = {}
metro_cols = ['waferscribe','ext_mv']
print('Reading Metro Data')
for filename in glob.glob("metro/GH*"): # GH v 22 for STII
    metro[filename[6:-4]] = pd.read_csv(filename,usecols=metro_cols)[metro_cols] # Using filenames w/out path and file type as dictionary keys
    mfile.append(filename[6:-4])  # Create index of filename strings
    print(f'\t{filename} Data Finished')
    met = pd.concat(metro.values(),ignore_index=True)

# Trim down 'met' to relevant ext_mv values
paramVal = met['ext_mv']
paramBool = met[paramVal%1==0]
dropParam = paramBool.index
met.drop(dropParam, inplace=True)
MetroWafers = met.waferscribe

# Retrieving OES Data from the .csv files, takes MUCH longer, retrieving specfic columns helps
ofile = []
oes = {}
data = {}
#oes_cols = ['WAFER_SCRIBE','RunStartTime', 'TimeStamp','StepID', 'OES_CO483', 'OES_C516', 'OES_CN387'] # For STI INTEGRATED 
#oes_cols = ['LOT_ID','WAFER_SCRIBE','RunStartTime', 'TimeStamp','StepID', 'OES_BCl272', 'OES_C516', 'OES_CN387', 'OES_CO483', 'OES_F703', 'OES_H656', 'OES_O777', 'OES_OH309','OES_Si251','OES_Si288'] # For STI INTEGRATED
oes_cols = ['WAFER_SCRIBE','RunStartTime', 'TimeStamp','StepID', 'OESIB1', 'OESIB2', 'OESIB3', 'OESIB4', 'OESIB5', 'OESIB6', 'OESIB7', 'OESIB8'] # For GH CONTACT 
print('Reading OES Data')
for filename in glob.glob("oes/3500.csv"): #5030-22 STI INTEGRATED DRY ETCH_1 #3500-GH CONTACT OXIDE DRY ETCH_10.csv
    oes[filename[4:-4]] = pd.read_csv(filename, usecols=oes_cols,parse_dates=['RunStartTime', 'TimeStamp'],infer_datetime_format=True)[oes_cols]
    ofile.append(filename[4:-4]) # Create index of filename strings
    data = pd.concat(oes.values(),ignore_index=True) # Struggles with STI INTEGRATED data # pd.concat(oes.values(),ignore_index=True)
    print(f'\t{filename} Data Finished')

# Trim down 'data' to only metro-matching wafers by removing them
UniqueWafers = data.WAFER_SCRIBE.unique()
nonWafers = np.isin(UniqueWafers,list(MetroWafers),invert=True)
i = np.where(nonWafers)[0]
WaferScribe = []
WaferScribe = (UniqueWafers[i])
print('Trimming Down Data to Only Metro-Matching Wafers')
indexNames = []
for x in tqdm(WaferScribe):
    WaferScribeData = data['WAFER_SCRIBE']
    dataindex = data[WaferScribeData == x]
    indexNames = dataindex.index
    data.drop(indexNames , inplace=True)
print('\tDone!') 
UniqueWafers = data.WAFER_SCRIBE.unique()

# Turning Data into Wafer for easy keys and converting dates into 
t_sec = {}
Wafer = {}
DataFrameDict = {elem : pd.DataFrame for elem in UniqueWafers}
print('Creating Wafer Data Set & Processing Dates into Time in Seconds')
for i,key in enumerate(tqdm(DataFrameDict.keys())):
    Wafer[i] = pd.DataFrame.from_dict(data[:][data.WAFER_SCRIBE == key]) # Create DataFrame for specific wafers
    delt = Wafer[i]['TimeStamp']-Wafer[i]['RunStartTime'] # Find timedelta for a wafer
    t_sec[i] = delt.dt.total_seconds() # Put timedelta into seconds
print('\tDone!')
OES_col = [col for col in Wafer[i].columns if 'OES' in col] #Create list of all intensity columns w/rt element

wafer_param_time = met[['waferscribe','ext_mv']]
etch_time = []
step = 4
# Only temporarily kept in here
for x in range (len(UniqueWafers)):
    #fig = plt.figure()
    Tsteps = t_sec[x].loc[Wafer[x]['StepID']==step]
    x_int = np.linspace(Tsteps.iloc[0], Tsteps.iloc[-1], 100)
    #plt.axvspan(Tsteps.iloc[0], Tsteps.iloc[-1], alpha=0.25) #, ymin=0, ymax=1, **kwargs)
    plt.title(f"Wafer Number: {UniqueWafers[x]}")
    for y in range (1,2): #len(OES_col)):
        Intensity = Wafer[x][OES_col[y]].loc[Wafer[x]['StepID']==step]
        plt.plot(Tsteps,Intensity, label=f"{OES_col[y]}") #,color="tab:orange")                 # OG Data
        try:
            tck = interpolate.splrep(Tsteps,Intensity, k = 3, s = 1e5) #1e6
        except ValueError:
            tck = interpolate.splrep(Tsteps[::-1],Intensity[::-1], k = 3, s = 1e5) #1e6
        y_int = interpolate.splev(x_int, tck, der = 0)
        #plt.plot(x_int,y_int, label=f"Smooth {OES_col[y]}")#,color="tab:blue")                 # Smoothed Data
        first = interpolate.splev(x_int, tck, der = 1)
        #plt.plot(x_int,first, label=f"1st {OES_col[y]}",linestyle = '--',color="tab:red")      # First Derivative Plot
        second = interpolate.splev(x_int, tck, der = 2)
        peaks, _ = find_peaks(second) #, height=1e5) #, distance=150)
        #print(x_int[peaks]-x_int[0])
        #plt.plot(x_int,second, label=f"2nd {OES_col[y]}",linestyle = ':',color="tab:green")    # Second Derivative Plot
        #plt.plot(x_int[peaks], second[peaks], "x",color="tab:purple", label = "Peaks")         # Second Derivative Peaks
        #plt.plot(x_int[peaks], first[peaks], "x",color="tab:purple", label = "Peaks")          # First Derivative Peaks
        plt.plot(x_int[peaks], y_int[peaks], "x",color="tab:purple", label = "Peaks")          # Smoothed Peaks
        
        #plt.plot(t_sec[x],Wafer[x][OES_col[y]],label = f"{OES_col[y]}")                        # Whole plot

        #plt.xlim(Tsteps.iloc[0]-1,Tsteps.iloc[0]+15)
        #plt.ylim(-2e4,2e4)
        try:
            peakTime.append(x_int[-1]-x_int[peaks[0]]) # x_int[peaks[0]]) # 
            waferScribe.append(UniqueWafers[x])
        except IndexError:
            pass
        
    plt.legend()
#plt.show()
#print(len(peakTime))
#print(len(waferScribe))
etch_time = pd.DataFrame({'waferscribe':waferScribe,'peaks':peakTime})

etch_time.drop(etch_time.loc[etch_time['peaks'] < 1,'peaks'].index, inplace=True)
etch_time.drop(etch_time.loc[etch_time['peaks'] > 30,'peaks'].index, inplace=True)

#print('Etch',(etch_time))
#print('Param',(wafer_param_time))
result = pd.merge(etch_time, wafer_param_time, on = ['waferscribe'])
#print('Result',result)

fig = plt.figure()
plt.scatter(result.peaks, result.ext_mv)
plt.show()