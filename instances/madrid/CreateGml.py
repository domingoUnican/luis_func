import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import math as m
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
mpl.use('Agg')
import random as rnd

rnd.seed(1)


def IsInCircle (row, radius, center): 
  dist = m.sqrt(pow(row['X']-center[0], 2) + pow(row['Y']-center[1], 2))
  return (dist < radius)

def IsInRectangle (row, xs, ys): 
  return (row['X'] >= xs[0] and row['X'] < xs[1] and row['Y'] >= ys[0] and row['Y'] < ys[1])      

def GenerateVdus (prbs): 
  aux = prbs
  maxCells = int(aux/100)
  nMacro = rnd.randint(0, maxCells)
  aux = aux-nMacro*100
  maxCells = int((aux)/50)
  nSmall = rnd.randint(0, maxCells) if maxCells > 0 else 0
  aux = aux-nSmall*50
  maxCells = int((aux)/6)
  nMicro = rnd.randint(0, maxCells) if maxCells > 0 else 0
  return [nMacro, nSmall, nMicro]

def GenerateVbss (scenSize, step):   
  cols = ['id', 'X', 'Y', 'eta']
  dus = pd.DataFrame(columns=cols).set_index(['id'])
  fIn = open (f'rawInfo/pdus{scenSize}.dat','r')
  for line in tqdm(fIn, desc='Loading DUs'):
    data = line.strip().split(',')
    dus.loc[(data[0]), :] = [float(data[1]), float(data[2]), 100]
  xmin = float(dus['X'].min())-step/2
  xmax = float(dus['X'].max())+step/2
  ymin = float(dus['Y'].min())-step/2
  ymax = float(dus['Y'].max())+step/2
  Xs = np.arange(xmin, xmax+step, step)
  Ys = np.arange(ymin, ymax+step, step)

  VBs = []
  areas = []
  for x1, x2 in zip(Xs, Xs[1:]):
    for y1, y2 in zip(Ys, Ys[1:]):
      xc = (x2+x1)/2
      yc = (y2+y1)/2
      print('---------------------------------------------------------')
      
      xc = (x1 + x2) / 2
      yc = (y1 + y2) / 2
      print(f'\nLimits --- X: [{x1}, {x2}], Y: [{y1}, {y2}]: C [{xc}, {yc}]')
      hipo = round(m.sqrt(pow(xc-x2, 2)+pow(yc-y2, 2)))
      du2 = dus[dus.apply(IsInRectangle, xs=[x1, x2], ys=[y1, y2], axis=1)]
      prbs = du2["eta"].sum()
      vDus = GenerateVdus(prbs)
      print(f'Generate {vDus[0]} macro, {vDus[1]} small, {vDus[2]} micro for {prbs}')
      for i in range(1, vDus[0]+1):
        VBs.append({
          'x' : xc, 
          'y': yc,
          'rho': hipo,
          'eta': 100,
          'type': 1
        })
      for i in range(1, vDus[1]+1):
        VBs.append({
          'x' : xc, 
          'y': yc,
          'rho': hipo,
          'eta': 50,
          'type': 1
        })
      for i in range(1, vDus[2]+1):
        VBs.append({
          'x' : xc, 
          'y': yc,
          'rho': hipo,
          'eta': 6,
          'type': 1
        })
      areas.append({
        'anchor': [x1, y1],
        'side': x2-x1,
        'macro': vDus[0],
        'small': vDus[1],
        'micro': vDus[2]
      })
      
  fOut = open(f'./madridRequest{scenSize}.gml', 'w')
  fOut.write('graph\n[')
  

  nodeCtr = 1
  for i in range(0, len(VBs)):
    str = f'\n  node\n  [\
      \n    id {nodeCtr}\
      \n    type 2\
      \n  ]'
    fOut.write(str)
    nodeCtr +=1

  for vb in VBs:
    str = f"\n  node\n  [\
      \n    id {nodeCtr}\
      \n    type 1\
      \n    x {vb['x']}\
      \n    y {vb['y']}\
      \n    eta {vb['eta']}\
      \n    rho {vb['rho']}\
      \n  ]"
    fOut.write(str)
    nodeCtr +=1  

  for i in range(1, len(VBs)+1):
    str = f'\n  edge\n  [\
      \n    source {i}\
      \n    target {i+len(VBs)}\
      \n  ]'
    fOut.write(str)

  fOut.write('\n]') 
  return areas

def GenerateScenario (scenSize):
  fOut = open(f'./madrid{scenSize}.gml', 'w')
  fOut.write('graph\n[')

  fIn = open (f'rawInfo/pcus{scenSize}.dat','r')
  for line in tqdm(fIn, desc='Loading CUs'):
    data = line.strip().split(',')
    str = f'\n  node\n  [\
      \n    id {data[0]}\
      \n    x {data[1]}\
      \n    y {data[2]}\
      \n    type 2\
      \n    omega {1000}\
      \n  ]'
    fOut.write(str)

  fIn = open (f'rawInfo/pdus{scenSize}.dat','r')
  for line in tqdm(fIn, desc='Loading DUs'):
    data = line.strip().split(',')
    str = f'\n  node\n  [\
      \n    id {data[0]}\
      \n    x {data[1]}\
      \n    y {data[2]}\
      \n    type 1\
      \n    omega {20}\
      \n    eta {200}\
      \n  ]'
    fOut.write(str)

  fIn = open (f'rawInfo/plinks{scenSize}.dat','r')
  for line in tqdm(fIn, desc='Loading links'):
    data = line.strip().split(',')
    str = f'\n  edge\n  [\
      \n    source {data[0]}\
      \n    target {data[1]}\
      \n    type {data[3]}\
      \n  ]'
    fOut.write(str)  

if __name__ == '__main__':

  scenSizes = ['Tiny', 'Small', 'Med', 'Real']
  # scenSizes = ['Tiny']

  for scenSize in scenSizes:
    step = 100
    GenerateScenario (scenSize)
    areas = GenerateVbss(scenSize, step)
    fig, ax = plt.subplots()
    xmin = 1e9
    xmax = 0
    ymin = 1e9
    ymax = 0
    for area in areas:
      ax.add_patch(Rectangle(area['anchor'], area['side'], area['side'], color='blue', alpha=0.2))
      # print (f'Area {area["anchor"]} with side {area["side"]}')
      str = f'[{area["macro"]}, {area["small"]}, {area["micro"]}]'
      if scenSize != 'Real':
        ax.text(area['anchor'][0]+5, area['anchor'][1]+area['side']-5,\
          str, fontsize=6, horizontalalignment='left', verticalalignment='top')
      xmin = xmin if area['anchor'][0] >= xmin else area['anchor'][0]
      ymin = ymin if area['anchor'][1] >= ymin else area['anchor'][1]
      xmax = xmax if area['anchor'][0]+area['side'] < xmax else area['anchor'][0]+area['side']
      ymax = ymax if area['anchor'][1]+area['side'] < ymax else area['anchor'][1]+area['side']
    fIn = open (f'rawInfo/pdus{scenSize}.dat','r')
    cols = ['id', 'X', 'Y', 'type']
    nodes = pd.DataFrame(columns=cols).set_index(['id'])
    for line in tqdm(fIn, desc='Loading DUs'):
      data = line.strip().split(',')
      nodes.loc[(float(data[0])), :] = [float(data[1]), float(data[2]), 2]
    fIn = open (f'rawInfo/pcus{scenSize}.dat','r')
    for line in tqdm(fIn, desc='Loading CUs'):
      data = line.strip().split(',')
      nodes.loc[(float(data[0])), :] = [float(data[1]), float(data[2]), 1]  
    print(nodes.index.max())
    print(nodes.index.min())
    fIn = open (f'rawInfo/plinks{scenSize}.dat','r')
    for line in tqdm(fIn, desc='Loading DUs'):
      data = line.strip().split(',')
      src = nodes.loc[float(data[0])].values
      dst = nodes.loc[float(data[1])].values
      if (src[2] == 1 & dst[2] == 1):
        ax.plot([src[0], dst[0]], [src[1], dst[1]], '-k', alpha=1, linewidth=1)  
      else   :
        ax.plot([src[0], dst[0]], [src[1], dst[1]], ':k', alpha=0.5, linewidth=1)  
    for idx, node in nodes.iterrows(): 
      if node['type'] == 2:
        ax.add_patch(plt.Circle((node['X'], node['Y']), 5, color='r', zorder=5))  
        if scenSize != 'Real':
          ax.text(node['X'], node['Y']-10, '($\eta=100$)', fontsize=6,horizontalalignment='center')
      else:   
        ax.add_patch(plt.Circle((node['X'], node['Y']), 5, color='b', zorder=5))  
      xmin = xmin if node['X'] >= xmin else node['X']-10
      ymin = ymin if node['Y'] >= xmin else node['Y']-10
      xmax = xmax if node['X'] < xmax else node['X']+10
      ymax = ymax if node['Y'] < ymax else node['Y']+10
    ax.set_xlim([xmin, xmax])  
    ax.set_ylim([ymin, ymax])  
    plt.savefig(f'./Scenario{scenSize}.pdf')
    plt.close()   
