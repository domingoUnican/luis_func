import sly
from codigo.representation import EdgePhysical, EdgeVirtual
from codigo.representation import RequestDistributedUnit, RequestCentralUnit
from codigo.representation import PhysicalDistributedUnit, PhysicalCentralUnit
from codigo.representation import Topology, defaultdict
import pprint


pp = pprint.PrettyPrinter(indent=4, width=80, underscore_numbers=False)


class FuncSplitLexer(sly.Lexer):
    tokens = {KEYWORD, NUMBER, STRING, GRAPH,
              NODE, EDGE, ID, TYPE, X, Y,
              OMEGA, ETA, RHO, SOURCE, TARGET}
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
                   "target": "TARGET",
                   "rho" : "RHO"
        }

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
    special = {'id', 'type', 'omega', 'x', 'y',
               'omega', 'eta', 'source', 'target', "rho"}

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
        p.elements['edges'].append(p.edge.reversed())
        return p.elements


    @_('NODE "[" attrs "]"')
    def node(self, p):
        Constructor, args = None, None
        print(f"args={p.attrs}")
        if p.attrs["type"] == 1:
            if "rho" in p.attrs:
                Constructor = RequestDistributedUnit
                args = [p.attrs[j] for j in ("id", "x", "y", "eta", "rho", "type")]
            else:
                Constructor = PhysicalDistributedUnit
                args = [p.attrs[j] for j in ("id", "x", "y", "omega", "eta", "type")]
        else:
            if "omega" in p.attrs:
                Constructor = PhysicalCentralUnit
                args = [p.attrs[j] for j in ("id", "x", "y", "omega", "type")]
            else:
                Constructor = RequestCentralUnit
                args = [p.attrs[j] for j in ("id", "type")]
        return Constructor(*args)

    @_('EDGE "[" attrs "]"')
    def edge(self, p):
        if "type" in p.attrs:
                                p.attrs["target"],
            return EdgePhysical(p.attrs["source"],
                                p.attrs["type"])
        else:
            return EdgeVirtual(p.attrs["target"],
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

        print(f"Error: {p}")
    def error(self, p):
        print(p)

if True:
    DIR = '/Users/krauser/Git_Repositories/luis_func/instances/'
    f = open(f"{DIR}madrid/madridRequestTiny.gml", 'r')
    in_ = f.read()
    lexer, parser = FuncSplitLexer(), FuncSplitParser()
    lexer2 = FuncSplitLexer()
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
