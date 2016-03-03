# Adds DBpedia entities linked to graph, traverses the DBpedia graph for
# a few levels (specified in constants.py)
import logging

import networkx as nx

from node import Node
from constants import *

# Covert "YAGO:Entity" to URL that DBpedia expects
def convertYAGOToURL(yago):
    entity = yago.split(':')[1].decode('unicode-escape')
    return 'http://yago-knowledge.org/resource/%s' % entity

def parseDBpediaLine(line):
    toks = line.split()
    src = toks[0][1:-1]
    dst = toks[2][1:-1]
    return (src, dst)

# Main process being called from main
def process_dbpedia(graph):
    logging.debug('Linking YAGO entities to DBpedia entities')
    mapping = {}
    for node in graph.nodes():
        if node.nodeType == YAGO_ENTITY:
            url = convertYAGOToURL(node.nodeValue)
            mapping[url] = node

    frontier = {}
    visited = set()
    with open(YAGO_DBPEDIA, 'r') as f:
        f.readline()    # First line is a comment
        for line in f.xreadlines():
            (src, dst) = parseDBpediaLine(line) # src is DBpedia URL
            if dst in mapping:
                dnode = Node(DB_ENTITY, src)  # May exist already
                graph.add_node(dnode)
                graph.add_edge(mapping[dst], dnode)
                frontier[src] = dnode
                visited.add(src)
                # print "Mapped %s to %s" % (mapping[src].nodeValue, dnode.nodeValue)

    newFrontier = {}
    for i in range(DEPTH): # Traverse DEPTH entities deep into DBpedia;w
        logging.debug('Starting traversal of DBpedia, level %d of %d' % (i+1, DEPTH))
        counter = 0
        with open(DBPEDIA, 'r') as f:   # Stream through DBpedia
            f.readline()    # First line is a comment
            for line in f.xreadlines():
                (src, dst) = parseDBpediaLine(line)
                # Treating (src, dst) as bidirectional
                if src in frontier:
                    dnode = Node(DB_ENTITY, dst)    # May exist already
                    graph.add_node(dnode)
                    graph.add_edge(frontier[src], dnode)
                    counter += 1
                    if dst not in visited:
                        visited.add(dst)
                        newFrontier[dst] = dnode

                if dst in frontier:
                    dnode = Node(DB_ENTITY, src)    # May exist already
                    graph.add_node(dnode)
                    graph.add_edge(frontier[dst], dnode)
                    counter += 1
                    if src not in visited:
                        visited.add(src)
                        newFrontier[src] = dnode

        # Ideally free old frontier here?
        frontier = newFrontier
        logging.debug('Finished level %d, added %d edges, frontier size: %d' % (i+1, counter, len(frontier)))
