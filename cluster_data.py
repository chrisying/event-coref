# WARNING: this code uses eval, make sure you trust GRAPH_OUTPUT
import networkx as nx

from scipy.sparse import csr_matrix
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score
from sklearn.neighbors import kneighbors_graph

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

# Returns a matrix of features, one row per event
def extractFeatures(graph, eventNodes):
    indptr = [0]
    indices = []
    data = []
    vocabulary = {}
    true_labels = []
    for node in eventNodes:
        if (node.nodeValue.endswith('plus.xml.txt')):
            true_labels.append(-1 * int(node.nodeValue.split('_')[0]))
        else:
            true_labels.append(int(node.nodeValue.split('_')[0]))

        desc = nx.descendants(graph, node)
        for d in desc:
            if d.nodeType == YAGO_ENTITY or d.nodeType == DB_ENTITY:
                index = vocabulary.setdefault(d.nodeValue, len(vocabulary))
                indices.append(index)
                data.append(1)
        indptr.append(len(indices))

    feature_matrix = csr_matrix((data, indices, indptr), dtype=int)
    return feature_matrix

# Does basic agglomerative clustering
def cluster(feature_matrix):
    connectivity = kneighbors_graph(feature_matrix, n_neighbors=10, include_self=False)
    connectivity = 0.5 * (connectivity + connectivity.T)

    best_nc = -1
    best_acc = -1
    best_labels = None

    for nc in range(45, 300):
        algo = AgglomerativeClustering(n_clusters=nc, linkage='ward', connectivity=connectivity)
        pred_labels = algo.fit_predict(feature_matrix.toarray())
        accuracy = adjusted_rand_score(true_labels, pred_labels)
        print 'Num clusters: %d\t\tScore: %.5f' % (nc, accuracy)
        if accuracy > best_acc:
            best_nc = nc
            best_acc = accuracy
            best_labels = pred_labels

    return (best_nc, best_acc, best_labels)

    '''
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
    '''

'''
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
'''

def writeToFile(nc, acc, labels, eventNodes):
    with open(GRAPH_CLUSTER_OUTPUT, 'w') as f:
        f.write('Best number of clusters: %d\t\tScore: %f\n' % (nc, acc))
        i = 0
        for node in eventNodes:
            f.write('%d\t%s\n' % (labels[i], node.nodeValue))
            i += 1

def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('Deserializing graph')
    graph = deserializeGraph(GRAPH_OUTPUT)
    logging.debug('Getting event nodes')
    eventNodes = getEventNodes(graph)
    #logging.debug('Computing dictionary')
    #(dictionary, count) = computeDictionary(graph, eventNodes)
    logging.debug('Extracting features')
    feature_matrix = extractFeatures(graph, eventNodes)
    logging.debug('Clustering')
    (nc, acc, labels) = cluster(feature_matrix)

    #logging.debug('Computing cluster dictionary')
    #eventClusters = clusterDictionary(eventNodes, clusters)
    #logging.debug('Evaluating clusters')
    #score = evaluateAccuracy(eventClusters)
    logging.debug('Writing clusters to file')
    writeToFile(nc, acc, labels, eventNodes)

if __name__ == '__main__':
    main()
