# coding: utf-8

import pprint 
import numpy as np
import pandas as pd
pp = pprint.PrettyPrinter(indent=4, width=40, sort_dicts=True, underscore_numbers=False)

#
# Calculactions and parameters from:
# S. Lagén, L. Giupponi, A. Hansson and X. Gelabert, "Modulation Compression in Next Generation RAN: Air Interface and Fronthaul Trade-offs," in IEEE Communications Magazine, vol. 59, no. 1, pp. 89-95, January 2021, doi: 10.1109/MCOM.001.2000453.
# There are 7 options

BWs = [ 
  {
    'BW': 1.4,
    'PRB': 6
  }, 
  # {
  #   'BW': 3,
  #   'PRB': 15
  # }, 
  # {
  #   'BW': 5,
  #   'PRB': 25
  # }, 
  {
    'BW': 10,
    'PRB': 50
  }, 
  # {
  #   'BW': 15,
  #   'PRB': 75
  # }, 
  {
    'BW': 20,
    'PRB': 100
  },
  # {
  #   'BW': 100,
  #   'PRB': 500
  # }
]

# Reference parameters
BW_ref = 20
NL_ref = 2
M_ref = 6 # 6 bits for 64 QAM
SIGNAL = 16
CR = 44
R = 1/3
MAC_info_7_1 = 120
MAC_info_7_2 = 700
MAC_info_7_3 = 800
N_sc = 12
N_symb = 14
W = 32
N_ap = 2

# System parameters
PR = 150# reference of DL BW = 20Mhz, NL = 2 layers, M_ref = 64-QAM 
M = 6 # 6 bits for 64 QAM
NL = 2

'''
From:
M. Shehata, A. Elbanna, F. Musumeci and M. Tornatore, "Multiplexing Gain and Processing Savings of 5G Radio-Access-Network Functional Splits," in IEEE Transactions on Green Communications and Networking, vol. 2, no. 4, pp. 982-991, Dec. 2018, doi: 10.1109/TGCN.2018.2869294.
Functions: 
F1: FFT/IFFT
F2: Filtering 
-------------------------------------- Split 7-1
F3: Sampling
F4: Demapping/mapping
-------------------------------------- Split 7-2
F5: Channel estimation
F6: Predistortion
-------------------------------------- Split 7-3
F7: MIMO precoding
F8: Equalizer
F9: Equalization computation
F10: OFDM Modulation
-------------------------------------- Split 6
F11: Channel coding
F12: Time domain estimation and computation
-------------------------------------- Split 4
F13: RLC 
-------------------------------------- Split 2
F14: PDCP 
-------------------------------------- Split 1
F15: RRC
-------------------------------------- Split 0
'''

splitNames = ['SPLIT0', 'SPLIT1', 'SPLIT2', 'SPLIT4', 'SPLIT6', 'SPLIT7_3',\
  'SPLIT7_2', 'SPLIT7_1']

def GetRate(split, BW, PRBs):
  if (split == splitNames[0]):
    return 0
  elif (split == splitNames[1]):  
    return PR*BW/BW_ref*NL/NL_ref*M/M_ref
  elif (split == splitNames[2]):  
    return (PR*BW/BW_ref*NL/NL_ref*M/M_ref)+SIGNAL
  elif (split == splitNames[3]):  
    return PR*BW/BW_ref*NL/NL_ref*M/M_ref
  elif (split == splitNames[4]):  
    return (PR+CR)*BW/BW_ref*NL/NL_ref*M/M_ref
  elif (split == splitNames[5]):  
    return (PR+CR)*BW/BW_ref*NL/NL_ref*M/M_ref*(1/R)+MAC_info_7_3
  elif (split == splitNames[6]):  
    return (N_sc*PRBs*N_symb*W*NL)/1000+MAC_info_7_2
  elif (split == splitNames[7]):  
    return (N_sc*PRBs*N_symb*W*N_ap)/1000+MAC_info_7_1      

delays = {
  splitNames[0]: np.NaN,
  splitNames[1]: 1e4,
  splitNames[2]: 5e3,
  splitNames[3]: 100,
  splitNames[4]: 250,
  splitNames[5]: 250,
  splitNames[6]: 250,
  splitNames[7]: 250,
}
  
alphas = {
  splitNames[0]: [0,1],
  splitNames[1]: [1/15, 14/15],
  splitNames[2]: [2/15, 13/15],
  splitNames[3]: [3/15, 12/15],
  splitNames[4]: [5/15, 10/15],
  splitNames[5]:[9/15, 6/15],
  splitNames[6]:[11/15, 4/15],
  splitNames[7]:[13/15, 2/15],
}

alphas_cu =[0, 1/15, 2/15, 3/15, 5/15, 9/15, 11/15, 13/15]
def GetCompComplexity (split, PRBs):
  all = (3*N_ap*+ pow(N_ap, 2) + 1/3* M * R * NL) * PRBs/5
  return [alphas[split][0]*all,alphas[split][1]*all]

if __name__ == '__main__':

  cols = ['SPLIT', 'PRB', 'DR', 'DELAY', 'CU_CAP', 'DU_CAP']
  df = pd.DataFrame(columns=cols).set_index(['SPLIT','PRB'])
  selectedSpltis = ['SPLIT1', 'SPLIT4', 'SPLIT6', 'SPLIT7_3']
  for BW in BWs :
    for splitName in selectedSpltis:
      delay  = delays[splitName]
      dr = GetRate(splitName, BW['BW'], BW['PRB'])
      cc = GetCompComplexity(splitName, BW['PRB'])
      df.loc[(splitName, BW['PRB']), :] = [dr, delay, cc[0], cc[1]]
    
  print(df)
  df.to_csv('splitParams.csv', sep='\t', float_format='%0.4f')

  cols = ['TYPE', 'NAME', 'DELAY_MIN', 'DELAY_MAX', 'DR_MIN', 'DR_MAX']
  df = df = pd.DataFrame(columns=cols).set_index(['TYPE', 'NAME'])

  df.loc[(0, 'micro6_15Ghz'), :]  = [250, 250, 2000, 2000]
  df.loc[(1, 'micro18_42Ghz'), :] = [250, 250, 3700, 3700]
  # df.loc[(2, 'microWave'), :]     = [200, 200, 100,  1000]

  # df.loc[(3, 'V_BAND'), :] = [500, 500, 1000, 1000]
  df.loc[(2, 'E_BAND'), :] = [50,  100, 3000, 10000]
  # df.loc[(5, 'mmWave'), :] = [200, 200, 500,  2000]
  
  df.loc[(3, 'NGPON'), :] = [5, 5, 10000, 10000]
  # df.loc[(7, 'E_PON'), :]  = [1000, 1000, 10, 1000]
  # df.loc[(8, 'GE_PON'), :] = [1000, 1000, 10, 10000]
  
  
  

  print(df)
  df.to_csv('linksParams.csv', sep='\t', float_format='%0.4f')
  

