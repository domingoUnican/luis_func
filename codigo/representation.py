# coding: utf-8
import csv
from dataclasses import dataclass, field
from copy import deepcopy
from collections import defaultdict
from typing import List
import os
HOME = os.environ["HOME"]
CONFDATA = f"{HOME}/Git_Repositories/luis_func/confData/linksParams.csv"
SPLITPAR = f"{HOME}/Git_Repositories/luis_func/confData/splitParams.csv"
SPLIT_WEIGHTS = {
    "SPLIT1": 100,
    "SPLIT4": 50,
    "SPLIT6": 25,
    "SLIT7_3": 1
    }


@dataclass
class Split:
    name: str = ''
    prb: int  = 0
    dr: float = 0.0
    delay: float = 0.0
    cu_cap: float = 0.0
    du_cap: float = 0.0

    def from_tuple(self, t):
        self.name = f"{t[0]}"
        self.prb = int(t[1])
        self.dr = float(t[2])
        self.delay = float(t[3])
        self.cu_cap = float(t[4])
        self.du_cap = float(t[5])


@dataclass
class ListSplit:
    possible: List[Split] = field(default_factory=list)

    def __post_init__(self):
        with open(SPLITPAR, 'r') as f:
            csv_data = csv.reader(f, delimiter='\t')
            next(csv_data)
            for line in csv_data:
                a = Split()
                a.from_tuple(line)
                self.possible.append(a)


@dataclass(frozen=True)
class Node:
    id: int

    def __lt__(self, a):
        return self.id < a.id

    def __le__(self, a):
        return self.id < a.id

    def __eq__(self, a):
        return self.id == a.id


@dataclass(frozen=True)
class PhysicalNode(Node):
    x: float
    y: float
    omega: int


# This represents both requests and physical CU
@dataclass(frozen=True)
class PhysicalCentralUnit(PhysicalNode):
    type: int = 2


# This represents both requests and physical DU
@dataclass(frozen=True)
class PhysicalDistributedUnit(PhysicalNode):
    eta: int
    type: int = 1



@dataclass(frozen=True)
class RequestCentralUnit(Node):
    type: int = 2


# This represents both requests and physical DU
@dataclass(frozen=True)
class RequestDistributedUnit(Node):
    x: float
    y: float
    eta: int
    rho: int
    type: int = 1




@dataclass
class Edge:
    source: int
    target: int

    def __lt__(self, a):
        return (self.source < a.source or
                (self.source == a.source and self.target < a.target))

    def __eq__(self, a):
        return self.source == a.source and self.target == a.target


@dataclass
class EdgePhysical(Edge):
    type: int
    name: str = "mmWave"
    delay: int = 200
    dr_min: int = 500
    dr_max: int = 2000

    def reversed(self):
        a = deepcopy(self)
        a.source, a.target = a.target, a.source
        return a

    def __post_init__(self):
        with open(f'{CONFDATA}', 'r') as f:
            csv_data = csv.reader(f, delimiter='\t')
            next(csv_data)
            for line in csv_data:
                if self.type == int(line[0]):
                    self.name = line[1]
                    self.delay = int(line[2])
                    self.dr_min = int(line[3])
                    self.dr_max = int(line[4])
                    break
            else:
                raise Warning("Type of Edge incorrectly declared")

    def bandwidth(self):
        return self.dr_min


@dataclass
class EdgeVirtual(Edge):
    """ Documentation for edge virtual """

    def reversed(self):
        return EdgeVirtual( self.target, self.source)

class Topology:
    """
    Documentation for Topology

    """

    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.adjacency = defaultdict(list)
        self.id_nodes = dict()
        for n in self.get_nodes():
            self.id_nodes[n.id] = n
        for e in self.get_edges():
            s, t = e.source, self.id_nodes[e.target]
            self.adjacency[s].append(t)


    def get_nodes(self):
        return self.dictionary["nodes"]

    def get_edges(self):
        return self.dictionary["edges"]

    def get_node_by_id(self, id):
        return self.id_nodes[id]

    def get_edge_by_source(self, source):
        for i in self.get_edges():
            if i.source == source:
                yield i

    def modify_edge_by_id(self, new_edge):
        for pos, i in enumerate(self.get_edges()):
            if i.source  == new_edge.source and i.target == new_edge.target:
                break
        else:
            raise Exception("Edge not found")
        self.dictionary["edges"][pos] = new_edge

    def modify_node_by_id(self, new_node):
        for pos, i in enumerate(self.get_nodes()):
            if i.id == new_node.id:
                break
        else:
            raise Exception("Node not found")
        self.dictionary["nodes"][pos] = new_node
        self.id_nodes[new_node.id] = new_node

    def all_paths(self, source, target, bandwidth, delay):
        if source == target:
            return []




class BranchAndBound:
    """Documentation for BranchAndBound

    """

    def __init__(self, physical, requests):
        self.node_correspondance = dict()
        self.edge_correspondance = dict()
        self.original = deepcopy(physical)
        self.physical = deepcopy(physical)  # This is going to be modified
        self.requests = deepcopy(requests)
        self.initialize_connect()

    def initialize_connect(self):
        self.connect_dict = dict()
        self.size = dict()
        for node in self.physical.get_nodes():
            self.connect_dict[node.id] = node.id
            self.size[node.id] = 1

    def root(self, id):
        temp = self.connect_dict[id]
        while temp != id:
            temp, id = self.connect_dict[temp], temp
        return temp

    def is_connected(self, id1, id2):
        return self.root(id1) == self.root(id2)

    def connect(self, id1, id2):
        root1 = self.root(id1)
        root2 = self.root(id2)
        if self.size[root1] > self.size[root2]:
            self.connect_dict[root2] = root1
            self.size[root1] += self.size[root2]
        else:
            self.connect_dict[root1] = root2
            self.size[root2] += self.size[root1]

    def first_node_unassigned(self):
        for node in self.requests.get_nodes():
            if node not in self.node_correspondance:
                return node
        else:
            return None

    def first_link_unassigned(self):
        for link in self.requests.get_edges():
            if link not in self.edge_correspondance:
                return link
            path = self.edge_correspondance[link]
            a, b = link.source, link.target
            for temp1, temp2 in self.node_correspondance.items():
                if temp1.id == a:
                    a = temp2.id
                    break
            for temp1, temp2 in self.node_correspondance.items():
                if temp1.id == b:
                    b = temp2.id
                    break
            if not path or path[0].source != a or path[-1].target != b:
                return link
        return None

    def is_assigned(self):
        return (self.first_link_unassigned() is None
                and self.first_link_unassigned() is None)

    def DoC(self):
        d = defaultdict(int)
        news, number = set(), 0
        for node_r, value in self.node_correspondance.items():
            node_p, level_split = value
            d[level_split] += 1
            if node_p not in news:
                news.add(node_p)
                number += 1
        result = 0.0
        for level in d:
            result += d[level] * SPLIT_WEIGHTS[level]
        return result / (number)

    def UoC(self):
        used_capacity = 0
        num_links = 0
        for link1, link2 in zip(sorted(self.original.get_edges()),
                                sorted(self.physical.get_edges())):
            num_links += 1
            # The formula is the capacity minus the remainder
            used_capacity += 1 - link2.bandwidth()/link1.bandwidth()
        return used_capacity / num_links

    def cost(self):
        return self.DoC() * (1 - self.UoC())

    def expand(self):
        for edge in self.requests.get_edges():
            node_cu = self.requests.get_node_by_id(edge.source)
            node_du = self.requests.get_node_by_id(edge.target)
            if isinstance(node_cu, RequestDistributedUnit):
                node_cu, node_du = node_du, node_cu
            
