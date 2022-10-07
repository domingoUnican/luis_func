# coding: utf-8

from parser import *


def start(p, sol=None, c=0):
    finish = p.is_assigned()
    if finish:
        ct = p.cost()
        if ct > c:
            sol1 = p
    else:
        for ap in p.expand():
            sol1, ct = start(ap, sol, c)
            if c < ct:
                sol, c = sol1, ct
    return sol, c



if __name__ == '__main__':
    DIR = "../instances"
    f = open(f"{DIR}/networks/small/DU2CU1/Gn5e7.gml", 'r')
    in_ = f.read()
    lexer, parser = FuncSplitLexer(), PhysicalParser()
    parser.shift = 0
    j0 = parser.parse(lexer.tokenize(in_))
    f = open(f"{DIR}/requests/small/R1CUs2DUs5E5/little.gml", 'r')
    in_ = f.read()
    lexer, parser = FuncSplitLexer(), RequestParser()
    parser.shift = 0
    j1 = parser.parse(lexer.tokenize(in_))
    print(j1.get_edges())
    bb = BranchAndBound(j0, j1)
    print(start(bb))
