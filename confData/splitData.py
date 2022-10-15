# coding: utf-8

import configparser
import pprint 
import pandas as pd
pp = pprint.PrettyPrinter(indent=4, width=40, sort_dicts=True, underscore_numbers=False)

#
# Calculactions and parameters from:
# Transmission capacity and delay for each functional split: Small Cell Forum document 159.07.02
# Transport block sizes: 3GPP TS 36.213
# Processing capacities dereived from:
# - A Flexible and Future-Proof Power Model for Cellular Base Stations (DOI: 10.1109/VTCSpring.2015.7145603)
# - DU/CU Placement for C-RAN over Optical Metro_aggregation Networks (DOI: https://doi.org/10.1007/978-3-030-38085-4_8)

N_PRBS = [6,15,25,50,75,100]
ITBS = [
[152,  392,	 680,	1384,	2088,	2792],
[200,  520,	 904,	1800,	2728, 3624],
[248,  648,	 1096, 2216, 3368, 4584],
[320,  872,	 1416, 2856, 4392, 5736],
[408,  1064, 1800, 3624, 5352, 7224],
[504,  1320, 2216, 4392, 6712, 8760],
[600,  1544, 2600, 5160, 7736, 10296],
[712,  1800, 3112, 6200, 9144, 12216],
[808,  2088, 3496, 6968, 10680, 14112],
[936,  2344, 4008, 7992, 11832, 15840],
[1032, 2664, 4392, 8760, 12960, 17568],
[1192, 2984, 4968, 9912, 15264, 19848],
[1352, 3368, 5736, 11448,	16992, 22920],
[1544, 3880, 6456, 12960,	19080, 25456],
[1736, 4264, 7224, 14112,	21384, 28336],
[1800, 4584, 7736, 15264,	22920, 30576],
[1928, 4968, 7992, 16416,	24496, 32856],
[2152, 5352, 9144, 18336,	27376, 36696],
[2344, 5992, 9912, 19848,	29296, 39232],
[2600, 6456, 10680, 21384, 32856, 43816],
[2792, 6968, 11448,	22920, 35160,	46888],
[2984, 7480, 12576,	25456, 37888,	51024],
[3240, 7992, 13536,	27376, 40576,	55056],
[3496, 8504, 14112,	28336, 43816,	57336],
[3624, 9144, 15264,	30576, 45352,	61664],
[3752, 9528, 15840,	31704, 46888,	63776],
[4008, 9912, 16416,	32856, 48936,	75376]
]



def Config2Dict (config):
  dict = {}
  for section in config.sections():
    dict[section.upper()] = {}
    for key, val in config.items(section):
      dict[section.upper()][key.upper()] = int(val) if val.isdigit() else float(val)
  return dict

def  DumpConfig(config):
  aux = {section: dict(config[section]) for section in config.sections()}
  pp.pprint(aux)

## DOWNLINK L2/L3
def DlMtuPerTti (params):
  tbs_dl = params['L2L3']['TBS_DL']
  mtu = params['TRAFFIC']['MTU']
  hdr_pdcp = params['L2L3']['HDR_PDCP']
  hdr_rlc = params['L2L3']['HDR_RLC']
  hdr_mac = params['L2L3']['HDR_MAC']
  return (tbs_dl /((mtu + hdr_pdcp + hdr_rlc + hdr_mac)*8))

def DlRrcPdcp(params): 
  mtuPerTti = DlMtuPerTti(params)
  mtu = params['TRAFFIC']['MTU']
  ntbs = params['L2L3']['N_TBS_DL']
  return (mtuPerTti*mtu*ntbs*8*1e3)/1e6

def DlPdcpRlc(params): 
  mtuPerTti = DlMtuPerTti(params)
  mtu = params['TRAFFIC']['MTU']
  hdr_pdcp = params['L2L3']['HDR_PDCP']
  ntbs = params['L2L3']['N_TBS_DL']  
  return (mtuPerTti*(mtu+hdr_pdcp)*ntbs*8*1e3)/1e6

def DlRlcMac(params): 
  mtuPerTti = DlMtuPerTti(params)
  mtu = params['TRAFFIC']['MTU']
  hdr_pdcp = params['L2L3']['HDR_PDCP']
  hdr_rlc = params['L2L3']['HDR_RLC']
  ntbs = params['L2L3']['N_TBS_DL']
  return (mtuPerTti*(mtu+hdr_pdcp+hdr_rlc)*ntbs*8*1e3)/1e6
  
def DlIntraMac(params): 
  mtuPerTti = DlMtuPerTti(params)
  mtu = params['TRAFFIC']['MTU']
  hdr_pdcp = params['L2L3']['HDR_PDCP']
  hdr_rlc = params['L2L3']['HDR_RLC']
  hdr_mac = params['L2L3']['HDR_MAC']
  ntbs = params['L2L3']['N_TBS_DL']  
  sched = params['L2L3']['SCHED']
  return ((mtuPerTti*(mtu+hdr_pdcp+hdr_rlc+hdr_mac)*ntbs*8*1e3)/1e6)+sched

def DlMacPhy(params): 
  mtuPerTti = DlMtuPerTti(params)
  mtu = params['TRAFFIC']['MTU']
  hdr_pdcp = params['L2L3']['HDR_PDCP']
  hdr_rlc = params['L2L3']['HDR_RLC']
  hdr_mac = params['L2L3']['HDR_MAC']
  ntbs = params['L2L3']['N_TBS_DL']  
  fapi = params['L2L3']['FAPI_DL']
  return ((mtuPerTti*(mtu+hdr_pdcp+hdr_rlc+hdr_mac)*ntbs*8*1e3)/1e6)+fapi

## UPLINK L2/L3
def UlMtuPerTti (params):
  tbs_ul = params['L2L3']['TBS_UL']
  mtu = params['TRAFFIC']['MTU']
  hdr_pdcp = params['L2L3']['HDR_PDCP']
  hdr_rlc = params['L2L3']['HDR_RLC']
  hdr_mac = params['L2L3']['HDR_MAC']
  return (tbs_ul /((mtu + hdr_pdcp + hdr_rlc + hdr_mac)*8))  

def UlRrcPdcp(params): 
  mtuPerTti = UlMtuPerTti(params)
  mtu = params['TRAFFIC']['MTU']
  ntbs = params['L2L3']['N_TBS_UL']
  return (mtuPerTti*mtu*ntbs*8*1e3)/1e6

def UlPdcpRlc(params): 
  mtuPerTti = UlMtuPerTti(params)
  mtu = params['TRAFFIC']['MTU']
  hdr_pdcp = params['L2L3']['HDR_PDCP']
  ntbs = params['L2L3']['N_TBS_UL']  
  return (mtuPerTti*(mtu+hdr_pdcp)*ntbs*8*1e3)/1e6

def UlRlcMac(params): 
  mtuPerTti = UlMtuPerTti(params)
  mtu = params['TRAFFIC']['MTU']
  hdr_pdcp = params['L2L3']['HDR_PDCP']
  hdr_rlc = params['L2L3']['HDR_RLC']
  ntbs = params['L2L3']['N_TBS_UL']
  return (mtuPerTti*(mtu+hdr_pdcp+hdr_rlc)*ntbs*8*1e3)/1e6
  
def UlIntraMac(params): 
  mtuPerTti = UlMtuPerTti(params)
  mtu = params['TRAFFIC']['MTU']
  hdr_pdcp = params['L2L3']['HDR_PDCP']
  hdr_rlc = params['L2L3']['HDR_RLC']
  hdr_mac = params['L2L3']['HDR_MAC']
  ntbs = params['L2L3']['N_TBS_UL']  
  sched = params['L2L3']['SCHED']
  return ((mtuPerTti*(mtu+hdr_pdcp+hdr_rlc+hdr_mac)*ntbs*8*1e3)/1e6)+sched

def UlMacPhy(params): 
  mtuPerTti = UlMtuPerTti(params)
  mtu = params['TRAFFIC']['MTU']
  hdr_pdcp = params['L2L3']['HDR_PDCP']
  hdr_rlc = params['L2L3']['HDR_RLC']
  hdr_mac = params['L2L3']['HDR_MAC']
  ntbs = params['L2L3']['N_TBS_UL']  
  fapi = params['L2L3']['FAPI_UL']
  return ((mtuPerTti*(mtu+hdr_pdcp+hdr_rlc+hdr_mac)*ntbs*8*1e3)/1e6)+fapi

if __name__ == '__main__':
  config = configparser.ConfigParser()
  config.read('config.ini')

  iTbsDl = 26 # 6QAM and highest I_MS
  iTbsUl = 20 # 16AM and highest I_MS
  
  params = Config2Dict(config)
  cols = ['SPLIT', 'PRB', 'CAP']
  df = pd.DataFrame(columns=cols)
  # df = df.set_index('SPLIT')
  

  for idx, prb in enumerate(N_PRBS):
    params['L2L3']['TBS_DL'] = ITBS[iTbsDl][idx]
    params['L2L3']['TBS_UL'] = ITBS[iTbsUl][idx]
    
    print('-- Uplink/downlink capacity requirements with {} PRBs'.format(prb))

    df.loc[len(df.index)] = ['RRC_PDCP',  prb, DlRrcPdcp(params)  + UlRrcPdcp(params)]
    df.loc[len(df.index)] = ['PDCP_RLC',  prb, DlPdcpRlc(params)  + UlPdcpRlc(params)]
    df.loc[len(df.index)] = ['RLC_MAC',   prb, DlRlcMac(params)   + UlRlcMac(params)]
    df.loc[len(df.index)] = ['INTRA_MAC', prb, DlIntraMac(params) + UlIntraMac(params)]
    df.loc[len(df.index)] = ['MAC_PHY',   prb, DlMacPhy(params)   + UlMacPhy(params)]

print(df.head(100))  

df = df.pivot_table('CAP', ['SPLIT'], 'PRB')
df['DELAY'] = [30, 30, 6,6,2]
df['CU_CAP'] = [2.7, 4.7, 6.7, 8.7, 10.7]
df['DU_CAP'] = [18.3, 16.3, 14.3, 12.3, 10.3]
print(df.head()) 

df.to_csv('params.csv', sep='\t', float_format='%0.4f')


