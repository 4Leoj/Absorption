import pathlib as pl
import pandas as pd
import numpy as np
from uncertainties import unumpy as unp
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import string

# The intensity data was gathered with the app "Phyphox"
Ipath = '../Data/I/11_100_30.csv'
Ipath_ = pl.Path(Ipath)
PARAMS = Ipath_.stem.split('_')
REP, SLEEP, CANT = *map(int, PARAMS),
ΔT = SLEEP*CANT/1000

Data_I = pd.read_csv(Ipath,index_col = 0)
Data_I = Data_I[Data_I>0].dropna()
Split_I = np.array_split(Data_I.values, REP) ##### path
Split_T = np.array_split(Data_I.index.values, REP)


def Pfit(xdata, ydata,deg):
  """ Helper function to fit (ydata) vs (xdata) 
      with a polynomial of degree (deg) """
  poly_params, cov = np.polyfit(xdata,ydata,deg, cov = True)
  p = np.poly1d(poly_params)

  err = np.sqrt(np.diag(cov))
  uParams = unp.uarray(poly_params,err) 
  R = np.corrcoef(p(xdata), ydata)[0,1]
  return p, uParams, R

def splitd(array, num):
  """ Split the intensity data by colors based on
      when the intensity stops increasing 
      array: Intensity data at one repetition
      num: number of colors to split the data"""

  ary = array.flat
  mask = np.gradient(ary) > 0
  ary = ary[mask]

  peaks, _ = find_peaks(ary, distance = len(ary)/(num+1))
  valleys, _ = find_peaks(ary*(-1), distance = len(ary)/(num+1))
  peaks = np.append(peaks, -2)
  valleys = np.insert(valleys, 0, 0)

  sub_arys = []
  for pe, va in zip(peaks,valleys):
    slic = ary[va:pe+1]
    if len(slic) > len(ary)/(num+1):
      sub_arys.append(np.insert(slic, 0, 0))

  return sub_arys

#
COLORS  = ('#FF0000','#FF9A00','#FFF700','#00FF00','#00FFFF','#0000FF','#DE00FF')

III = []
PPP = []

Split_I = np.array_split(Data_I.values,REP)
for I_rep in Split_I:
  II = splitd(I_rep, len(COLORS))
  params_fit = []
  for col, co in zip(II,COLORS):
    T = np.linspace(0,ΔT,len(col))
    li, uParams, R = Pfit(T,col,1)
    params_fit.append(uParams)
  PPP.append(params_fit)
P_mean = pd.DataFrame(np.mean(PPP,axis=0).T, columns = COLORS)


## Fit Intensity vs Voltage and plot results
deg = 3
polyFit = {}
V_mean = pd.read_csv('../Carac_result/Mean.csv')
T = np.linspace(0,ΔT,len(V_mean))
for col in P_mean: # in V_mean
  V = V_mean[col].values
  linear = np.poly1d(P_mean[col])
  I = linear(T)
  I, uI = unp.nominal_values(I), unp.std_devs(I)
  plt.errorbar(V,I, yerr = uI,fmt= 'o',markersize=4, capsize = 2,color=col)

  V_s = np.linspace(np.min(V),np.max(V),num=100)
  poly_params, cov = np.polyfit(V,I,deg, cov = True)
  p = np.poly1d(poly_params)

  err = np.sqrt(np.diag(cov))
  uParams = unp.uarray(poly_params,err) 
  polyFit[col] = uParams
  R = np.corrcoef(p(V), I)[0,1]

  plt.plot(V_s,p(V_s),color=col,label=f'$R^2$ = {R:.3f}')
  
plt.legend(fontsize=12)
plt.xlabel('V $[V]$',size=20)
plt.ylabel('I $[lx]$',size=20)
plt.title('Intensity vs Voltage', size = 22)
plt.show()

## Save fit params to csv file
polyFit = pd.DataFrame(polyFit)
polyFit_save = unp.nominal_values(polyFit)
polyFit_save = pd.DataFrame(polyFit_save)
polyFit_save.index = tuple(string.ascii_lowercase)[0:deg+1]
polyFit_save.columns = COLORS
polyFit_save.to_csv('../Carac_result/model_IV.csv')
