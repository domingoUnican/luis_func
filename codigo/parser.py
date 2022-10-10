import sly
from representation import *
import pprint

pp = pprint.PrettyPrinter(indent=4, width=80, underscore_numbers=False)


class FuncSplitLexer(sly.Lexer):
    tokens = {KEYWORD, GRAPH, NODE, ID, LABEL, X, Y,
              PRC, ANT, PRB, THETA, SOURCE,
              TARGET, DISTANCE, BANDWITH, TYPE,
              EDGE, NUMBER, STRING, DELAY}
    literals = {'(', ')', '[', ']'}
    _dictionary = {"graph": "GRAPH",
                   "node": "NODE",
                   "id": "ID",
                   "label": "LABEL",
                   "x": "X",
                   "y": "Y",
                   "prc": "PRC",
                   "ant": "ANT",
                   "prb": "PRB",
                   "theta": "THETA",
                   "source": "SOURCE",
                   "target": "TARGET",
                   "distance": "DISTANCE",
                   "bandwith": "BANDWITH",
                   "type": "TYPE",
                   "edge": "EDGE",
                   "delay": "DELAY"}

    @_(r"[a-zA-Z]+")
    def KEYWORD(self, t):
        if t.value.lower() in self._dictionary:
            temp = t.value.lower()
            if temp in ("graph", "node", "edge", "node"):
                t.type = temp.upper()
            else:
                t.type = 'KEYWORD'
            t.value = temp
            return t
        else:
            print(f'Unknown keyword {t.value} in line {t.lineno}')


    @_(r'"\w+"')
    def STRING(self, t):
        t.value = t.value[1:-1]
        return t


    @_(r"[0-9]+(\.[0-9]+)*")
    def NUMBER(self, t):
        t.value = float(t.value) if '.' in t.value else int(t.value)
        return t

    @_(r'\s+')
    def ignore_newline(self, t):
        self.lineno += (t.value.count('\n'))



class RequestParser(sly.Parser):
    debugfile = "requests.out"
    tokens = FuncSplitLexer.tokens
    shift = 1
    special = {'x', 'y', 'prb', 'prc', 'ant', 'theta',
               'bandwith', 'distance', 'type', 'delay'}

    @_('GRAPH "[" elements "]"')
    def net(self, p):
        return Topology(p.elements)

    @_('')
    def elements(self, p):
        return defaultdict(list)

    @_('elements node')
    def elements(self, p):
        p.elements['nodes'].append(p.node)
        return p.elements

    @_('elements edge')
    def elements(self, p):
        p.elements['edges'].append(p.edge)
        return p.elements

    @_('NODE "[" attrs "]"')
    def node(self, p):
        if p.attrs["type"] == 1:
            return DistributedUnit(p.attrs["id"],
                                   p.attrs["label"],
                                   p.attrs["x"],
                                   p.attrs["y"],
                                   p.attrs["prc"],
                                   p.attrs["prb"],
                                   p.attrs["ant"],
                                   p.attrs["theta"])
        elif p.attrs["type"] == 3:
            return CentralUnit(p.attrs["id"],
                               p.attrs["label"],
                               p.attrs["x"],
                               p.attrs["y"],
                               0)
        else:
            return CentralUnit(p.attrs["id"],
                                   p.attrs["label"],
                                   p.attrs["x"],
                                   p.attrs["y"],
                                   p.attrs["prc"])
    @_('EDGE "[" attrs "]"')
    def edge(self, p):
        return EdgeVirtual(p.attrs["source"],
                           p.attrs["target"],
                           p.attrs["bandwith"],
                            p.attrs["delay"])


    @_('')
    def attrs(self, p):
        return defaultdict(int)



    @_('attrs KEYWORD NUMBER')
    def attrs(self, p):
        p.attrs[p.KEYWORD] = p.NUMBER
        if p.KEYWORD not in self.special:
            p.attrs[p.KEYWORD] += self.shift
        return p.attrs

    @_('attrs KEYWORD STRING')
    def attrs(self, p):
        p.attrs["label"] = p.STRING + str(self.shift)
        return p.attrs




class PhysicalParser(sly.Parser):
    debugfile = "physical.out"
    tokens = FuncSplitLexer.tokens
    shift = 1
    special = {'x', 'y', 'prb', 'prc', 'ant', 'theta',
               'bandwith', 'distance', 'type', 'delay'}


    @_('GRAPH "[" elements "]"')
    def net(self, p):
        return Topology(p.elements)

    @_('')
    def elements(self, p):
        return defaultdict(list)

    @_('elements node')
    def elements(self, p):
        p.elements['nodes'].append(p.node)
        return p.elements


    @_('elements edge')
    def elements(self, p):
        p.elements['edges'].append(p.edge[0])
        p.elements['edges'].append(p.edge[1])
        return p.elements


    @_('NODE "[" attrs "]"')
    def node(self, p):
        if p.attrs["type"] == 1:
            return DistributedUnit(p.attrs["id"],
                                   p.attrs["label"],
                                   p.attrs["x"],
                                   p.attrs["y"],
                                   p.attrs["prc"],
                                   p.attrs["prb"],
                                   p.attrs["ant"],
                                   p.attrs["theta"])
        else:
            return CentralUnit(p.attrs["id"],
                                   p.attrs["label"],
                                   p.attrs["x"],
                                   p.attrs["y"],
                                   p.attrs["prc"])

    @_('EDGE "[" attrs "]"')
    def edge(self, p):
        return (EdgePhysical(p.attrs["source"],
                            p.attrs["target"],
                            p.attrs["bandwith"],
                            p.attrs["distance"],
                             p.attrs["type"]),
                EdgePhysical(p.attrs["target"],
                            p.attrs["source"],
                            p.attrs["bandwith"],
                            p.attrs["distance"],
                            p.attrs["type"]))


    @_('')
    def attrs(self, p):
        return defaultdict(int)


    @_('attrs KEYWORD NUMBER')
    def attrs(self, p):
        p.attrs[p.KEYWORD] = p.NUMBER
        if p.KEYWORD not in self.special:
            p.attrs[p.KEYWORD] += self.shift
        return p.attrs


    @_('attrs KEYWORD STRING')
    def attrs(self, p):
        p.attrs["label"] = f'{self.shift}_{p.STRING }'
        return p.attrs


if __name__ == '__main__':
    DIR = "../instances"
    f = open(f"{DIR}/networks/small/DU2CU1/Gn3e2.gml", 'r')
    in_ = f.read()
    lexer, parser = FuncSplitLexer(), PhysicalParser()
    parser.shift = 10
    j = parser.parse(lexer.tokenize(in_))
    print(j.get_edges())
    print('*'*1000)
    print(j.get_nodes())
    print('*'*1000)
    f = open(f"{DIR}/requests/small/R1CUs2DUs5E5/R1n7e5.gml", 'r')
    in_ = f.read()
    lexer, parser = FuncSplitLexer(), RequestParser()
    parser.shift = 10
    j = parser.parse(lexer.tokenize(in_))
    print(j.get_edges())
    print('*'*1000)
    print(j.get_nodes())
    print('*'*1000)
