import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd
import numpy as np
import serial
import time
import os

""" It is defined in params: the number of repetitions (rep),
    the delay between each measurement (sleep) and
    the number of intensities for each color (cant) """
params = '12 100 30\r\n' # rep sleep cant 
COLORS  = ('#FF0000','#FF9A00','#FFF700','#00FF00','#00FFFF','#0000FF','#DE00FF') 
color_num = len(COLORS)

arduino = serial.Serial(port='COM6', baudrate=115200, timeout=.1)

""" It waits until the arduino sends a 1
    indicating that it is ready to receive the parameters """
while arduino.readline() != b'1':
    pass

params_b = bytes(params,'utf-8')
arduino.write(params_b)

rep, sleep, cant = *map(int, params.split(' ')),
sleep /= 1000

# Wait until the data collection is finished
time.sleep(rep*color_num*(sleep*cant+1))


Data = arduino.readlines()
for da in Data:
    print(da.decode('utf-8'))
Data_df = pd.read_csv(BytesIO(b'\n'.join(Data)), header = None).T

# Separation of data for each repetition and creation of csv
Sep_data = np.split(Data_df, rep, axis=1)
params = params[:-2]
dir = f'../Data/V/{params}'
os.makedirs(dir)
for i, data in enumerate(Sep_data):
    data.columns = COLORS
    data.to_csv(f'{dir}/{params}_{i}.csv',index=False)

# Average voltage data across all repetitions
VVV = []
for i in range(rep):
  V_data = pd.read_csv(f'{dir}/{params}_{i}.csv')
  V_data.dropna(inplace=True)
  VVV.append(V_data)

V_concat = pd.concat(VVV)
V_mean = V_concat.groupby(V_concat.index).mean()
V_mean *= 5/1023 # To units of [V] 
V_mean.to_csv('../Carac_result/Mean.csv')

# Plot mean voltage vs time
ΔT = sleep*cant/1000
V_std = V_concat.groupby(V_concat.index).std() 
T = np.linspace(0,ΔT,len(V_mean))
for col in V_mean:
  plt.errorbar(T,V_mean[col],yerr = V_std[col], fmt= 'o',markersize=4, capsize = 2,color = col)

plt.title('Mean voltage vs. time', size=22)
plt.ylabel('V $[V]$', size=20)
plt.xlabel('T $[s]$', size=20)