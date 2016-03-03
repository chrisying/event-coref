# This code is deprecated (leaving for deserialize code for now)
import networkx as nx

from node import Node

INPUT = 'output/ecb_graph'
DBPEDIA = 'dbpedia/yago_links.nt'

DOC = 1
EVENT = 2
ENTITY = 3
YAGO_ENTITY = 4
DB_ENTITY = 5

def deserializeNode(nstr):
    toks = nstr.split('\t')
    nodeType = int(toks[0])
    if nodeType == DOC:
        return Node(nodeType, toks[1].strip())
    elif nodeType == EVENT or nodeType == ENTITY:
        nodeValue = eval(toks[1].strip())
        return Node(nodeType, nodeValue)
    elif nodeType == YAGO_ENTITY:
        return Node(nodeType, toks[1].strip())
    else:
        print 'Warning: unsupported node type %d' % nodeType
        return

    node = Node(int(toks[0]), toks[1].strip())

def deserializeEdge(estr):
    toks = estr.split('\t')
    node1 = deserializeNode('\t'.join([toks[0], toks[1]]))
    node2 = deserializeNode('\t'.join([toks[2], toks[3]]))
    return (node1, node2)

# Modifies the graph
def deserializeGraph(graph):
    with open(INPUT, 'r') as f:
        [n, e] = map(int, f.readline().split('\t'))
        for i in range(n):
            node = deserializeNode(f.readline())
            graph.add_node(node)

        for i in range(e):
            (node1, node2) = deserializeEdge(f.readline())
            graph.add_edge(node1, node2)

def convertToURL(yago):
    entity = yago.split(":")[1].decode('unicode-escape')
    return 'http://yago-knowledge.org/resource/%s' % entity

def main():

    graph = nx.DiGraph()
    deserializeGraph(graph)

    # TODO: I could just move this all into parse_ecb.py and ignore all
    # parsing issues (might be a better option)
    mapping = {}
    with open(INPUT, 'r') as f:
        for line in f.xreadlines():
            toks = line.split('\t')
            if toks[0] == '4':
                url = convertToURL(toks[1].strip())
                mapping[url] = []

    with open(DBPEDIA, 'r') as f:
        for line in f.xreadlines():
            toks = line.split()
            if toks[2][1:-1] in mapping:
                mapping[toks[2][1:-1]].append(toks[0][1:-1])

    print mapping

if __name__ == '__main__':
    main()
