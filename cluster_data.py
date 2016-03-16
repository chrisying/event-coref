# WARNING: this code uses eval, make sure you trust GRAPH_OUTPUT
import networkx as nx
import numpy as np

from constants import *
from node import Node
from cluster import Cluster

# Read graph from path
def deserializeGraph(path):
    graph = nx.Graph()
    with open(path) as f:
        numEdges = int(f.readline());
        for i in range(numEdges):
            line = f.readline().strip()
            (n1, n2) = eval(line)
            graph.add_edge(n1, n2)
    return graph

# Gets the nodes in the graph corresponding to high-level events (doc)
def getEventNodes(graph):
    nodes = []
    for node in graph.nodes():
        if node.nodeType == DOC:
            nodes.append(node)
    return nodes

# Computes feature (aka entity name) -> index dict
def computeDictionary(graph, eventNodes):
    dictionary = {}
    counter = 0
    for node in eventNodes:
        desc = nx.descendants(graph, node)
        for d in desc:
            if d.nodeType == YAGO_ENTITY or d.nodeType == DB_ENTITY:
                if d.nodeValue not in dictionary:
                    dictionary[d.nodeValue] = counter
                    counter += 1
    return (dictionary, counter)

# Returns list of vectors for each document
def extractFeatures(graph, eventNodes, dictionary, count):
    eventFeatures = []
    for node in eventNodes:
        vector = np.zeros(count)
        desc = nx.descendants(graph, node)
        name = node.nodeValue
        for d in desc:
            if d.nodeType == YAGO_ENTITY or d.nodeType == DB_ENTITY:
                vector[dictionary[d.nodeValue]] = 1
        eventFeatures.append((name, vector))

    return eventFeatures

# Does basic agglomerative clustering
def cluster(eventFeatures):
    clusters = [Cluster(name, vector) for (name, vector) in eventFeatures]
    numClusters = len(eventFeatures)

    while (numClusters > NUM_CLUSTERS):
        minPair = None
        minDist = -1
        for i in range(len(clusters)):
            for j in range(i+1, len(clusters)):
                c1 = clusters[i]
                c2 = clusters[j]
                dist = c1.distance(c2)
                if (dist < minDIct or minDist == -1):
                    minDist = dist
                    minPair = (i, j)
        (i,j) = (minPair[0], minPair[1])
        clusters[i].combine(clusters[j])
        clusters = clusters[:j] + clusters[j+1:]
        numClusters -= 1

    return clusters

def main():
    graph = deserializeGraph(GRAPH_OUTPUT)
    eventNodes = getEventNodes(graph)
    (dictionary, count) = computeDictionary(graph, eventNodes)
    eventFeatures = extractFeatures(graph, eventNodes, dictionary, count)
    clusters = cluster(eventFeatures)
    print [str(c) for c in clusters]

if __name__ == '__main__':
    main()
