# coding: utf-8
from dataclasses import dataclass, field
from copy import deepcopy
from collections import defaultdict

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
        self.node_correspondance = defaultdict(list)
        self.edge_correspondance = dict()
        self.original = deepcopy(physical)
        self.physical = deepcopy(physical) # This is going to modify
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

    def first_node_unassigned(self):
        for node in self.requests.get_nodes():
            if node not in self.node_correspondance:
                return node
        else:
            return None

    def first_link_unassigned(self):
        for link in self.requests.get_edges():
            path = self.edge_correspondance[link]
            a, b = link.source, link.target
            a, b = self.node_correspondance[a], self.node_correspondance[b]
            if not path or path[0].source != a or path[-1].target != b:
                return link
        return None

    def is_assigned(self):
        if self.first_node_unassigned() != None or self.first_node_unassigned() != None:
            return False
        return True

    def DoC(self):
        Agk = set()
        for link, path in self.edge_correspondance.items():
            Agk.update(set(path))
        Pools = 0
        for node in self.node_correspondance.values():
            if isinstance(node, CentralUnit):
                Pools += 1
        return len(Agk)/Pools

    def UoC(self):
        pass
    def cost(self):
        return self.DoC() * (1 - self.UoC())
