import argparse
import os
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Clustering-based functional split", add_help=True)
  parser.add_argument(
    '-pnet', 
    required =True,
    metavar = 'GML graph',
    help = 'Path/filename of the GML file with the physical graph'
  )
  parser.add_argument(
    '-rnet', 
    required =False,
    metavar = 'GML graph',
    help = 'Path/filename of the GML file with requested overlay network'
  )

  args = parser.parse_args()

  # Read GML file
  phyNet = nx.read_gml(args.pnet)

  

  # Print out all the nodes with their properties
  for label in phyNet.nodes:
    print(phyNet.nodes[label])

  for label in phyNet.edges:
    print(phyNet.edges[label])  


  nx.draw(phyNet, with_labels = True)
  plt.savefig("phyNet.png")

