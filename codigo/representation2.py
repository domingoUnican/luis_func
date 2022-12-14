# coding: utf-8
from dataclasses import dataclass
from copy import deepcopy
from collections import defaultdict


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
class Common(Node):
    x: float
    y: float
    omega: int


# This represents both requests and physical CU
@dataclass(frozen=True)
class CentralUnit(Common):
    type: int = 2


# This represents both requests and physical DU
@dataclass(frozen=True)
class DistributedUnit(Common):
    eta: int
    type: int = 1


@dataclass(frozen=True)
class Edge:
    source: int
    target: int

    def __lt__(self, a):
        return (self.source < a.source or
                (self.source == a.source and self.target < a.target))

    def __eq__(self, a):
        return self.source == a.source and self.target == a.target


@dataclass(frozen=True)
class EdgePhysical(Edge):
    source: int
    target: int
    type: int

    def __lt__(self, a):
        return (self.source < a.source or
                (self.source == a.source and self.target < a.target))

    def __eq__(self, a):
        return self.source == a.source and self.target == a.target


@dataclass(frozen=True)
class EdgeVirtual(Edge):
    """ Documentation for edge virtual """

class Topology:
    """Documentation for Topology

    """

    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.dictionary["nodes"] = sorted(self.dictionary["nodes"])
        self.dictionary["edges"] = sorted(self.dictionary["edges"])

    def get_nodes(self):
        return self.dictionary["nodes"]

    def get_edges(self):
        return self.dictionary["edges"]

    def get_node_by_id(self, id):
        for i in self.get_nodes():
            if i.id == id:
                return i

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


class BranchAndBound:
    """Documentation for BranchAndBound

    """

    def __init__(self, physical, requests):
        self.node_correspondance = defaultdict(list)
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
        return ( len(self.node_correspondance.keys()) == len(self.requests.get_nodes())
                 and
                 len(self.edge_correspondance.keys()) == len(self.requests.get_edges())
                 )
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
        used_capacity = 0
        num_links = 0
        for link1, link2 in zip(sorted(self.original.get_edges()),
                                sorted(self.physical.get_edges())):
            num_links += 1
            # The formula is the capacity minus the remainder
            used_capacity += 1 - link2.bandwidth/link1.bandwidth
        return used_capacity / num_links

    def cost(self):
        return self.DoC() * (1 - self.UoC())

    def expand(self):
        for node in self.requests.get_nodes():
            if any(node.id <= i.id for i in self.node_correspondance):
                continue
            for target in self.physical.get_nodes():
                aux = deepcopy(self)
                if node.prc < target.prc:
                    if isinstance(node, DistributedUnit) and isinstance(target, DistributedUnit):
                        target_aux = DistributedUnit(target.id,
                                                         target.x,
                                                         target.y,
                                                         target.prc - node.prc,
                                                         target.prb - node.prb,
                                                         target.ant - node.ant,
                                                         target.theta)
                        aux.physical.modify_node_by_id(target_aux)
                        aux.node_correspondance[node] = target_aux
                        yield aux
                    elif isinstance(node, CentralUnit) and isinstance(target, CentralUnit):
                        target_aux = CentralUnit(target.id,
                                                 target.x,
                                                 target.y,
                                                 target.prc - node.prc)
                        aux.physical.modify_node_by_id(target_aux)
                        aux.node_correspondance[node] = target_aux
                        yield aux
        if len(self.node_correspondance.keys()) == len(self.requests.get_nodes()):
            link = self.first_link_unassigned()
            initial, destiny = 0, 0
            if link not in self.edge_correspondance:
                self.initialize_connect()
                a = link.source
                for temp1, temp2 in self.node_correspondance.items():
                    if temp1.id == a:
                        a = temp2
                        break
                else:
                    raise Exception("Not found end")
                initial = a.id
            else:
                initial = self.edge_correspondance[link][-1].target
            for temp in self.physical.get_edge_by_source(initial):
                if (not self.is_connected(initial, temp.target) and link.bandwidth < temp.bandwidth):
                    aux = deepcopy(self)
                    temp1 = EdgePhysical(temp.source,
                                         temp.target,
                                         temp.bandwidth - link.bandwidth,
                                         temp.distance,
                                         temp.type)
                    if link not in self.edge_correspondance:
                        aux.edge_correspondance[link] = [temp1]
                    else:
                        aux.edge_correspondance[link] += [temp1]
                    destiny = temp.target
                    aux.connect(initial, destiny)
                    aux.physical.modify_edge_by_id(temp1)
                    yield aux
