import sly
from codigo.representation import *
import pprint

pp = pprint.PrettyPrinter(indent=4, width=80, underscore_numbers=False)


class FuncSplitLexer(sly.Lexer):
    tokens = {KEYWORD, NUMBER, STRING, GRAPH, NODE, EDGE, ID, TYPE, X, Y,
               OMEGA, ETA, SOURCE, TARGET}
    literals = {'(', ')', '[', ']'}
    _dictionary = {"graph": "GRAPH",
                   "node": "NODE",
                   "edge": "EDGE",
                   "id": "ID",
                   "type": "TYPE",
                   "x": "X",
                   "y": "Y",
                   "omega": "OMEGA",
                   "eta": "ETA",                   
                   "source": "SOURCE",
                   "target": "TARGET"}

    @_(r"[a-zA-Z]+")
    def KEYWORD(self, t):
        if t.value.lower() in self._dictionary:
            temp = t.value.lower()
            if temp in ("graph", "node", "edge"):
                t.type = temp.upper()
            else:
                t.type = 'KEYWORD'
            t.value = temp
            return t
        else:
            print(f'Unknown keyword {t.value}')


    @_(r'"(\w|\s)+"')
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




class FuncSplitParser(sly.Parser):
    debugfile = "physical.out"
    tokens = FuncSplitLexer.tokens
    shift = 1
    special = {'id', 'type', 'omega', 'x', 'y', 'omega', 'eta', 'source', 'target'}

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
                                   p.attrs["x"],
                                   p.attrs["y"],
                                   p.attrs["omega"],
                                   p.attrs["eta"])
        else:
            return CentralUnit(p.attrs["id"],
                                   p.attrs["x"],
                                   p.attrs["y"],
                                   p.attrs["omega"])

    @_('EDGE "[" attrs "]"')
    def edge(self, p):
        if "type" in p.attrs:
            return EdgePhysical(p.attrs["source"],
                                p.attrs["target"],
                                p.attrs["type"])
        else:
            EdgeVirtual(p.attrs["target"],
                         p.attrs["source"]) 

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
    f = open(f"{DIR}/madrid/madridTiny.gml", 'r')
    in_ = f.read()
    
    lexer, parser = FuncSplitLexer(), PhysicalParser()

    parser.shift = 10
    j = parser.parse(lexer.tokenize(in_))
    # print('*'*80)
    # pp.pprint (j.get_edges())
    # print('*'*80)
    # pp.pprint(j.get_nodes())
    
    # f = open(f"{DIR}/madrid/requestTiny.gml", 'r')
    # in_ = f.read()
    # lexer, parser = FuncSplitLexer(), RequestParser()
    # parser.shift = 10
    # j = parser.parse(lexer.tokenize(in_))
    # print('*'*80)
    # pp.pprint(j.get_edges())
    # print('*'*80)
    # pp.pprint(j.get_nodes())
