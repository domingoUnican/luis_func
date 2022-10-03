# coding: utf-8
from dataclasses import dataclass, field
from copy import deepcopy

@dataclass(frozen=True)
class Node:
    id: int
    label: str


@dataclass(frozen=True)
class Common(Node): 
    x: float
    y: float
    prc: int

#This represents both requests and physical CU
@dataclass(frozen=True)
class CentralUnit(Common):
    type: int = 2


#This represents both requests and physical DU
@dataclass(frozen=True)
class DistributedUnit(Common):
    prb: int
    ant: int
    theta: int # If is a request, make this to 0
    type: int = 1


@dataclass(frozen=True)
class Edge:
    source: int
    target: int
    bandwith: int


@dataclass(frozen=True)
class EdgePhysical(Edge):
    distance: float
    type: int


@dataclass(frozen=True)
class EdgeVirtual(Edge):
    delay: int


class Topology:
    """Documentation for Topology

    """

    def __init__(self, dictionary):
        self.dictionary = dictionary

    def get_nodes(self):
        return self.dictionary["nodes"]

    def get_edges(self):
        return self.dictionary["edges"]

    def get_node_by_id(self, id):
        for i in self.get_nodes():
            if i.get_id() == id:
                return i

    def get_edge_by_id(self, id):
        for i in self.get_edges():
            if i.get_id() == id:
                return i

class BranchAndBound:
    """Documentation for BranchAndBound

    """
    def __init__(self, physical, requests):
        self.node_correspondance = dict()
        self.edge_correspondance = dict()
        self.physical = deepcopy(physical)
        self.requests = deepcopy(requests)
        self.connect = dict()
        self.size = dict()
        for node in requests.get_nodes():
            self.connect[node.id] = self.connect[node.id]
            self.size[node.id] = 1

    def root(self, id):
        temp = self.connect[id]
        while temp != id:
            temp, id = self.connect[temp], temp
        return temp

    def is_connected(self, id1, id2):
        return self.root(id1) == self.root(id2)

    def connect(self, id1, id2):
        root1 = self.root(id1)
        root2 = self.root(id2)
        if self.size[root1] > self.size[root2]:
            self.connect[root2] = root1
            self.size[root1] += self.size[root2]
        else:
            self.connect[root1] = root2
            self.size[root2] += self.size[root1]

    def completa(self):
        for link in self.requests.get_nodes():
            source, target = link.source, link.target
            if not self.connect(source, target):
                return False
        return True
