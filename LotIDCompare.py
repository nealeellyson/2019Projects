
import pandas as pd
import glob
import os
import numpy as np
import dask.dataframe as dd
#from datetime import datetime,timedelta
#import time
#import matplotlib.pyplot as plt

# Retrieving Metro Data from .txt files
mfile = []
metro = {}
metro_lotID = ['lotid']
for filename in glob.glob("metro/22*"):
    metro[filename[6:-4]] = pd.read_csv(filename,usecols=metro_lotID)[metro_lotID] # Using filenames w/out path and file type as dictionary keys
    mfile.append(filename[6:-4])  # Create index of filename strings
    print(f'{filename} data finsished')
    met = pd.concat(metro.values(),ignore_index=True)
UniqueMetro = met.lotid
# Retrieving OES Data from the .csv files, takes MUCH longer, retrieving specfic columns helps

ofile = []
oes = {}
oesLots = {}
data = {}
lots = {}
cols = ['LOT_ID','WAFER_ID','RunStartTime', 'TimeStamp','StepID', 'OES_BCl272', 'OES_C516', 'OES_CN387', 'OES_CO483', 'OES_F703', 'OES_H656', 'OES_O777', 'OES_OH309'] # For STI INTEGRATED
#cols = ['LOT_ID','WAFER_ID','RunStartTime', 'TimeStamp','StepID', 'OESIB1', 'OESIB2', 'OESIB3', 'OESIB4', 'OESIB5', 'OESIB6', 'OESIB7', 'OESIB8'] # For GH CONTACT 
for filename in glob.glob("oes/5030*.csv"): #5030-22 STI INTEGRATED DRY ETCH_1 #3500-GH CONTACT OXIDE DRY ETCH_10.csv
    oes[filename[4:-4]] = pd.read_csv(filename, usecols=cols)[cols]
    ofile.append(filename[4:-4]) # Create index of filename strings
    data = pd.concat(oes.values(),ignore_index=True) # Struggles with STI INTEGRATED data # pd.concat(oes.values(),ignore_index=True)
    #data = oes[filename[4:-4]]
    #data.append(files)
    print(f'{filename} data finsished')
UniqueOES = data.LOT_ID.unique()

new = np.isin(UniqueOES,list(UniqueMetro),invert=True)
i = np.where(new)[0]
print((UniqueOES),new,i)
lotID = (UniqueOES[i])
print(data.size)



#print(type(data),len(lotID),len(oesLots))
#for i,x in enumerate(lotID):
#    print(i,x,data)
#    indexNames = data[ data['LOT_ID'] == x ].index
#    data.drop(indexNames , inplace=True)
#    lots[i] = (data.loc[data['LOT_ID'] == x])
    
#    oesLots = pd.concat(lots.values(),ignore_index=True)
#print(len(lots),len(lotID),len(oesLots))
#oesLots.append(oesLots, ignore_index=True)
#print((oesLots))
