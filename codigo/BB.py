# coding: utf-8

from parser import FuncSplitLexer, FuncSplitParser
import os
from itertools import product
from time import time

def start(p, sol=None, best_cost=0):
    finish = p.is_assigned()
    if finish:
        ct = p.cost()
        if ct > best_cost:
            sol, best_cost = p, ct
    else:
        for ap in p.expand():
            sol1, ct = start(ap, sol, best_cost)
            if ct > best_cost:
                sol, best_cost= sol1, ct
    return sol, best_cost



if __name__ == '__main__':
    DIR = "../instances"
    for net, req in product(os.walk(f"{DIR}/networks/small"), os.walk(f"{DIR}/requests/small")):
        root_net, dir_net, files_net = net
        root_req, dir_req, files_req = net
        files_req = [name for name in files_req if name.endswith((".gml",))]
        files_net = [name for name in files_net if name.endswith((".gml",))]
        for name_req, name_net in product(files_req, files_net):
            f = open(os.path.join(root_net, name_net), 'r')
            in_ = f.read()
            lexer, parser = FuncSplitLexer(), FuncSplitParser()
            parser.shift = 0
            j0 = parser.parse(lexer.tokenize(in_))
            f = open(os.path.join(root_req, name_req), 'r')
            in_ = f.read()
            lexer, parser = FuncSplitLexer(), FuncSplitParser()
            parser.shift = 0
            j1 = parser.parse(lexer.tokenize(in_))
            temp = time()
            bb = BranchAndBound(j0, j1)
            start(bb)
            print(f'|{name_req}|{name_net}|{time() - temp}|')
