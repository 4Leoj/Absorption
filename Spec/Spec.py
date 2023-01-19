from uncertainties import unumpy as unp
import matplotlib.pyplot as plt
import uncertainties as un
from io import BytesIO
import pathlib as pl
import pandas as pd
import numpy as np
import string
import serial
import time
import os

COLORS  = ('#FF0000','#FF9A00','#FFF700','#00FF00','#00FFFF','#0000FF','#DE00FF') 
color_num = len(COLORS)

def Spec_data(params, Sample, concentration = None):
    arduino = serial.Serial(port='COM6', baudrate=115200, timeout=.1)
    while arduino.readline() != b'1':
        pass

    time.sleep(.1)

    # Initial sending of the parameters (with the status set to 'no')
    params_b = bytes('no ' + params+'\r\n','utf-8') 
    arduino.write(params_b)

    ar = lambda x: (x+'\r\n').encode('utf-8')
    rep_ar, sleep_ar, scale_ar, i_ar = *map(ar,params.split(' ')),

    """ It waits until confirming that the arduino has the correct parameters
        when this is the case, the status changes to 'ok'
        and so the arduino can exit the while loop (see Spec.ino code) to collect the data"""
    while True:
        while not arduino.in_waiting:
            pass
        time.sleep(0.001)
        res = arduino.readlines()
        if res != [rep_ar, sleep_ar, scale_ar, i_ar]:
            print(res)
            arduino.write(params_b)
        else:
            params_b = bytes('ok\r\n','utf-8') #####
            arduino.write(params_b)
            break

    print('Final parameters')
    print(res)

    rep, sleep, scale, i = *map(int, params.split(' ')),
    sleep /= 1000
    time.sleep(rep*color_num*(sleep+1))

    # Substance voltage data reading
    Data = arduino.readlines()
    Data_df = pd.read_csv(BytesIO(b'\n'.join(Data)), header = None)
    Data_df.columns = COLORS

    # Save voltage information
    back_dir = f'./{Sample}/V'
    os.makedirs(back_dir, exist_ok=True)
    Data_df.to_csv(f'{back_dir}/{concentration}.csv',index=False)


    """ The absorption of the substance is calculated.
         If the concentration is not known, the model is evaluated.
         concentration vs absorption and is plotted. Otherwise,
         the absorption database for said concentration is updated"""

    Absorption = Abso(Data_df, i)
    
    if concentration is None: 
        path_Absorption = f'./{Sample}/Arbitraria.csv'
        A = Absorption
        Fit_CA(Sample)
        Concentration_prediction(A,Sample)
    else:
        path_Absorption = f'./{Sample}/Absorption.csv'
        path_Absorption_ = pl.Path(path_Absorption)
        # We proceed to add the new absorption data
        if path_Absorption_.is_file():
            A = pd.read_csv(path_Absorption, index_col = 0)
            A[concentration] = Absorption
        else: # If there is no data yet then a dataframe is created with nans
            A = pd.DataFrame(dict.fromkeys(COLORS, np.nan),index=[0]).T
            A[concentration] = Absorption
            A = A.dropna(axis = 1)

    # Data storage and absorption spectrum graphing
    A.to_csv(path_Absorption)
    Plot_spec(path_Absorption, Sample, concentration)

""" Wavelengths data taken from:
    https://en.wikipedia.org/wiki/Visible_spectrum#Spectral_colors """
λ = pd.DataFrame([[625,750],
                [590,625],
                [565,590],
                [500,565],
                [485,500],
                [450,485],
                [380,450]] ,index = COLORS, columns = ('min','max'))
Λ = λ.mean(numeric_only=True, axis=1)

def Abso(Vf, intensity):
  Vf = Vf*5/1023 # To units of [V]
  # Average voltage data reading for distilled water
  Vo = pd.read_csv(f'../Caracterization/Carac_result/Mean.csv')
  Vo = Vo.iloc[intensity-1]

  # Reading the parameters of the adjustment model between intensity and voltage
  pathModel_IV = f'../Caracterization/Carac_result/model_IV.csv'
  polyFit = pd.read_csv(pathModel_IV,index_col = 0)

  # Calculation of the absorption for each repetition carried out in the data collection
  A = []
  for rep in Vf.index:
    Vf_rep = Vf.loc[rep]
    A_rep = []
    for col in polyFit:
        model = np.poly1d(polyFit[col])
        I_o = model(Vo[col]) 
        I_f = model(Vf_rep[col])
        A_rep.append(np.log10(I_o/I_f))
    A.append(A_rep)
  A, uA = np.mean(A,axis=0), np.std(A,axis=0)
  A = unp.uarray(A,uA)
  return pd.Series(A,index = COLORS)

def Fit_CA(Sample):
    path_Absorption = f'./{Sample}/Absorption.csv'

    A = pd.read_csv(path_Absorption,index_col = 0).T
    C = A.index.astype(float)
    A = A.applymap(lambda x: un.ufloat_fromstr(x))
    
    A = unp.nominal_values(A)
    A = pd.DataFrame(A, columns = COLORS)

    # Fit of concentration vs absorption data for each color
    deg = 1
    polyFit = {}
    for col in A:
        poly_params = np.polyfit(A[col], C, deg)
        polyFit[col] = poly_params

    # Save parameters
    polyFit_save = pd.DataFrame(polyFit)
    polyFit_save.index = tuple(string.ascii_lowercase)[0:deg+1]
    polyFit_save.to_csv('./model_CA.csv')

def Plot_spec(path_Absorption, Sample, c):
  A = pd.read_csv(path_Absorption,index_col = 0,)
  A = A[A.columns[-1]].apply(lambda x: un.ufloat_fromstr(x))
  
  A, uA = unp.nominal_values(A), unp.std_devs(A)

  # Plot absorption spectrum
  plt.figure(2)
  plt.scatter(Λ, A, color = COLORS, zorder = 3)
  plt.errorbar(Λ, A, yerr = uA,fmt= '',linestyle = '', capsize = 2, ecolor = 'gray')
  title = f'Absorption spectrum {Sample}' if c is None else f'Absorption spectrum {Sample}, {c = } $[mol/L]$'
  plt.title(title, size = 20)
  plt.ylabel('A', size = 20)
  plt.xlabel(r'$\lambda$ $[nm]$', size = 20)

  path_Absorption_ = pl.Path(path_Absorption)
  dir = path_Absorption_.parent
  os.makedirs(f'{dir}/Plots',exist_ok=True) 
  save = f'{dir}/Plots/Arbitrary.pdf' if c is None else f'{dir}/Plots/{c}.pdf' 
  plt.savefig(save,bbox_inches = "tight")
  plt.show()

def Concentration_prediction(A,Sample):
    polyFit = pd.read_csv('./model_CA.csv', index_col = 0,) 

    # Compute concentration prediction for each color
    C_pred = []
    for col in polyFit:
        model = np.poly1d(polyFit[col])
        C_pred.append(model(A[col]))

    # Plot prediction
    C_pred, uC_pred = unp.nominal_values(C_pred), unp.std_devs(C_pred)
    A = unp.nominal_values(A)
    plt.figure(1)
    plt.scatter(A, C_pred, color = COLORS, zorder=3)
    plt.errorbar(A, C_pred, yerr = uC_pred,fmt= '',linestyle = '', capsize = 2, ecolor = 'gray')
    nc, uc = np.mean(C_pred), np.std(C_pred)
    c = un.ufloat(nc,uc)
    plt.hlines(nc, xmin = np.min(A)*.98, xmax =  np.max(A)*1.02, linestyles = 'dashed',colors = 'gray')
    plt.title('Prediction $\\bar{c}$ = '+f'{c:.1uP} $[mol/L]$', size = 22)
    plt.xlabel('Absorption', size = 20)
    plt.ylabel('Concentration', size = 20)


