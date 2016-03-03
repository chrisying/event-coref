# Adds DBpedia entities linked to graph, traverses the DBpedia graph for
# a few levels (specified in constants.py)
import networkx as nx

from node import Node
from constants import *

# Covert "YAGO:Entity" to URL that DBpedia expects
def convertYAGOToURL(yago):
    entity = yago.split(':')[1].decode('unicode-escape')
    return 'http://yago-knowledge.org/resource/%s' % entity

# Main process being called from main
def process_dbpedia(graph):
    mapping = {}
    for node in graph.nodes():
        if node.nodeType == 4:
            url = convertYAGOToURL(node.nodeValue)
            mapping[url] = node

    with open(YAGO_DBPEDIA, 'r') as f:
        for line in f.xreadlines():
            toks = line.split()
            url = toks[2][1:-1]
            if url in mapping:
                dnode = Node(DB_ENTITY, toks[0][1:-1])
                graph.add_node(dnode)
                graph.add_edge(mapping[url], dnode)
                # print "Mapped %s to %s" % (mapping[url].nodeValue, dnode.nodeValue)
