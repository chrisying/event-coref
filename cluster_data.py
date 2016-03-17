# WARNING: this code uses eval, make sure you trust GRAPH_OUTPUT
import networkx as nx
import numpy as np
from sklearn import metrics

from constants import *
from node import Node
from cluster import Cluster

import logging

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
        logging.debug('Current number of clusters: %d' % numClusters)
        minPair = None
        minDist = -1
        for i in range(len(clusters)):
            for j in range(i+1, len(clusters)):
                c1 = clusters[i]
                c2 = clusters[j]
                dist = c1.distance(c2)
                if (dist < minDist or minDist == -1):
                    minDist = dist
                    minPair = (i, j)
        (i,j) = (minPair[0], minPair[1])
        clusters[i].combine(clusters[j])
        clusters = clusters[:j] + clusters[j+1:]
        numClusters -= 1

    return clusters

def clusterDictionary(eventNodes, clusters):
    eventClusters = {}
    for n in eventNodes:
        eventClusters[n.nodeValue] = 0

    c = 0
    for cl in clusters:
        for event in cl.getCluster():
            eventClusters[event] = c
        c += 1
    return eventClusters

def evaluateAccuracy(eventClusters):
    pred = []
    true = []
    for event in eventClusters:
        pred.append(eventClusters[event])
        true.append(int(event.split('_')[0]))

    score = metrics.adjusted_rand_score(true, pred)
    print 'Score: %d/1.0' % score
    return score

def writeToFile(eventClusters, score):
    with open(GRAPH_CLUSTER_OUTPUT, 'w') as f:
        f.write('Score: %f\n' % score)
        for event in eventClusters:
            f.write('%d\t%s\n' % (eventClusters[event], event))

def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('Deserializing graph')
    graph = deserializeGraph(GRAPH_OUTPUT)
    logging.debug('Getting event nodes')
    eventNodes = getEventNodes(graph)
    logging.debug('Computing dictionary')
    (dictionary, count) = computeDictionary(graph, eventNodes)
    logging.debug('Extracting features')
    eventFeatures = extractFeatures(graph, eventNodes, dictionary, count)
    logging.debug('Clustering')
    clusters = cluster(eventFeatures)
    print [str(c) for c in clusters]
    logging.debug('Computing cluster dictionary')
    eventClusters = clusterDictionary(eventNodes, clusters)
    logging.debug('Evaluating clusters')
    score = evaluateAccuracy(eventClusters)
    logging.debug('Writing clusters to file')
    writeToFile(eventClusters, score)

if __name__ == '__main__':
    main()
