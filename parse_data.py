# Main code for parsing all the event tagger, YAGO, DBpedia data into a
# single networkx graph

import json
import logging

import networkx as nx
import matplotlib.pylab as plt

from node import Node
from constants import *
from process_events import process_events
from process_dbpedia import process_dbpedia

# Visualizes grpah with matplotlib
def drawGraph(graph):
    logging.debug('Drawing graph')
    labs = {}
    pos = {}
    SPACE = 1
    dc = 0
    evc = 0
    enc = 0
    yc = 0
    dbc = 0
    for n in graph.nodes():
        labs[n] = n.nodeValue
        if n.nodeType == DOC:
            pos[n] = (dc, 0)
            if dc < 0:
                dc -= SPACE
            else:
                dc += SPACE
            dc *= -1
        elif n.nodeType == EVENT:
            pos[n] = (evc, 1)
            if evc < 0:
                evc -= SPACE
            else:
                evc += SPACE
            evc *= -1
        elif n.nodeType == ENTITY:
            pos[n] = (enc, 2)
            if enc < 0:
                enc -= SPACE
            else:
                enc += SPACE
            enc *= -1
        elif n.nodeType == YAGO_ENTITY:
            pos[n] = (yc, 3)
            if yc < 0:
                yc -= SPACE
            else:
                yc += SPACE
            yc *= -1
        elif n.nodeType == DB_ENTITY:
            pos[n] = (dbc, 4)
            if dbc < 0:
                dbc -= SPACE
            else:
                dbc += SPACE
            dbc *= -1

    nx.draw_networkx_labels(graph, pos=pos, labels=labs)
    nx.draw_networkx_edges(graph, pos=pos, arrows=False)
    plt.show()

# Writes graph to file as an edge list
def serializeGraph(graph):
    logging.debug('Serializing graph')
    #nodes = map(lambda n:"%s\t%s\n" % (n.nodeType, n.nodeValue), graph.nodes())
    #edges = map(lambda (n1, n2):"%s\t%s\t%s\t%s\n" % (n1.nodeType, n1.nodeValue, n2.nodeType, n2.nodeValue), graph.edges())
    edges = map(lambda e:'%s\n' % repr(e), graph.edges())
    with open(GRAPH_OUTPUT, 'w') as f:
        #f.write('%d\t%d\n' % (len(nodes), len(edges)))
        f.write('%d\n' % len(edges))
        #f.writelines(nodes)
        f.writelines(edges)

def main():
    logging.basicConfig(level=logging.DEBUG)
    graph = nx.DiGraph()
    process_events(graph)
    process_dbpedia(graph)
    # drawGraph(graph)
    serializeGraph(graph)

if __name__ == '__main__':
    main()
