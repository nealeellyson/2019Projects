## Plotting Savgol smoothed, first, second and extrema using the first time step iteration where tstep = seconds(TimeStamp - RunStartTime)
## Using 22 STI, step 6, wavelength C516
import pandas as pd
import glob
import os
import numpy as np
import dask.dataframe as dd
from datetime import datetime,timedelta
import time
import matplotlib.pyplot as plt
from scipy.signal import find_peaks,savgol_filter
from scipy import interpolate
from tqdm import tqdm                       # For progress bar, yay!

# Retrieving Metro Data from .txt files
mfile = []
metro = {}
metro_cols = ['lotid','waferscribe','ext_mv']
print('Reading Metro Data')
for filename in glob.glob("metro/22*"): # GH v 22 for STII
    metro[filename[6:-4]] = pd.read_csv(filename,usecols=metro_cols)[metro_cols] # Using filenames w/out path and file type as dictionary keys
    mfile.append(filename[6:-4])  # Create index of filename strings
    print(f'\t{filename} Data Finished')
    met = pd.concat(metro.values(),ignore_index=True)

# Trim down 'met' to relevant ext_mv values
paramVal = met['ext_mv']
paramBool = met[paramVal%1==0]
dropParam = paramBool.index
met.drop(dropParam, inplace=True)
MetroLots = met.lotid
MetroWafers = met.waferscribe

# Retrieving OES Data from the .csv files, takes MUCH longer, retrieving specfic columns helps
ofile = []
oes = {}
data = {}
oes_cols = ['LOT_ID','WAFER_SCRIBE','RunStartTime', 'TimeStamp','StepID', 'OES_CO483', 'OES_C516', 'OES_CN387'] # For STI INTEGRATED 
#oes_cols = ['LOT_ID','WAFER_SCRIBE','RunStartTime', 'TimeStamp','StepID', 'OES_BCl272', 'OES_C516', 'OES_CN387', 'OES_CO483', 'OES_F703', 'OES_H656', 'OES_O777', 'OES_OH309'] # For STI INTEGRATED
#oes_cols = ['LOT_ID','WAFER_SCRIBE','RunStartTime', 'TimeStamp','StepID', 'OESIB1', 'OESIB2', 'OESIB3', 'OESIB4', 'OESIB5', 'OESIB6', 'OESIB7', 'OESIB8'] # For GH CONTACT 
print('Reading OES Data')
for filename in glob.glob("oes/5030-22 STI INTEGRATED DRY ETCH_*.csv"): #5030-22 STI INTEGRATED DRY ETCH_1 #3500-GH CONTACT OXIDE DRY ETCH_10.csv
    oes[filename[4:-4]] = pd.read_csv(filename, usecols=oes_cols,parse_dates=['RunStartTime', 'TimeStamp'],infer_datetime_format=True)[oes_cols]
    ofile.append(filename[4:-4]) # Create index of filename strings
    data = pd.concat(oes.values(),ignore_index=True) # Struggles with STI INTEGRATED data # pd.concat(oes.values(),ignore_index=True)
    print(f'\t{filename} Data Finished')

# Trim down 'data' to only metro-matching lots by removing them
UniqueLots = data.LOT_ID.unique()
nonLots = np.isin(UniqueLots,list(MetroLots),invert=True)
i = np.where(nonLots)[0]
lotID = []
lotID = (UniqueLots[i])
print('Trimming Down Data to Only Metro-Matching Lots')
indexNames = []
for x in tqdm(lotID):
    LotIDdata = data['LOT_ID']
    dataindex = data[LotIDdata == x]
    indexNames = dataindex.index
    data.drop(indexNames , inplace=True)
print('\tDone!')

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
step = 6

wafer_param_time = met[['waferscribe','ext_mv']]
etch_time = []
# Only temporarily kept in here
for x in range (len(UniqueWafers)): #len(UniqueWafers)): #5): #
    #fig = plt.figure()
    Tsteps = t_sec[x].loc[Wafer[x]['StepID']==step]
    #print(Tsteps)
    x_int = np.linspace(Tsteps.iloc[0], Tsteps.iloc[-1], 100)
    #plt.axvspan(Tsteps.iloc[0], Tsteps.iloc[-1], alpha=0.25) #, ymin=0, ymax=1, **kwargs)
    plt.title(f"Wafer Scribe: {UniqueWafers[x]}, {x}/{len(UniqueWafers)}")
    for y in range(1,2): #len(OES_col)): #
        Intensity = Wafer[x][OES_col[y]].loc[Wafer[x]['StepID']==step]
        #plt.plot(Tsteps,Intensity, label=f"{OES_col[y]}") #,color="tab:orange")                    # OG Data
        SGsmooth = savgol_filter(Intensity,window_length=11, polyorder = 5, deriv = 0)  #
        plt.plot(Tsteps,SGsmooth, label=f"Smooth {OES_col[y]}")#,color="tab:blue")                      # Smoothed Data
        first = savgol_filter(Intensity,window_length=11, polyorder = 5, deriv = 1)
        #plt.plot(Tsteps,first, label=f"1st {OES_col[y]}",linestyle = '--',color="tab:red")          # First Derivative Plot
        second = savgol_filter(Intensity,window_length=11, polyorder = 5, deriv = 2)
        #plt.plot(Tsteps,second, label=f"2nd {OES_col[y]}",linestyle = ':',color="tab:green")        # Second Derivative Plot
        
        peaks, _ = find_peaks(second, height=5e2) #, distance=150)
        #plt.plot(Tsteps[peaks], first[peaks], "x",color="tab:purple", label = "Peaks")              # First Derivative Peaks
        #plt.plot(Tsteps[peaks], second[peaks], "x",color="tab:purple", label = "Peaks")             # Second Derivative Peaks
        #plt.plot(Tsteps.values[peaks], SGsmooth[peaks], "x",color="tab:purple") #, label = "Peaks")              # Smoothed Peaks

#       print("Tsteps[peaks]:",Tsteps.values[peaks])
#       print("Tsteps[peaks]-Tsteps[0]:",Tsteps.values[peaks]-Tsteps.values[0])
#       print("Tsteps[-1]-Tsteps[peaks]:",Tsteps.values[-1]-Tsteps.values[peaks])
#       print("SGsmooth[peaks]:",SGsmooth[peaks])
#       print("first[peaks]:",first[peaks])
#       print("second[peaks]:",second[peaks])

        #print(x,len(peaks))
        #plt.ylim(0,8e5)
        #plt.xlim(215,225)
        #etch_time.append({'waferscribe':UniqueWafers[x],'peaks':Tsteps[peaks[0]]})
    plt.legend()
plt.show()

#print(etch_time)
#fig = plt.figure()
#plt.show()