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

# Returns a matrix of features, one row per event
def extractFeatures(graph, eventNodes):
    indptr = [0]
    indices = []
    data = []
    vocabulary = {}
    names = []
    for node in eventNodes:
        names.append(node.nodeValue)
        desc = nx.descendants(graph, node)
        for d in desc:
            if d.nodeType == YAGO_ENTITY or d.nodeType == DB_ENTITY:
                index = vocabulary.setdefault(d.nodeValue, len(vocabulary))
                indices.append(index)
                data.append(1)
        indptr.append(len(indices))

    feature_matrix = csr_matrix((data, indices, indptr), dtype=int)
    return (feature_matrix, names)

# Does basic agglomerative clustering
def cluster(feature_matrix, names):
    clusters = []
    for row in xrange(feature_matrix.shape[0]):
        clusters.append(Cluster(names[row], feature_matrix.getrow(row)))

    # print [str(c) for c in clusters]
    numClusters = len(clusters)
    bestScoreDiff = -1   # Treats ecb and ecb plus different
    bestScoreSame = -1   # Treats ecb and ecb plus same
    bestNumClusters = -1
    bestClusters = []
    while numClusters > 1:
        minPair = None
        minDist = -1
        for i in xrange(numClusters):
            for j in xrange(i+1, numClusters):
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

        pred = []
        trueSame = []
        trueDiff = []
        cnum = 0
        names = []
        for c in clusters:
            pred += [cnum] * len(c.names)
            for name in c.names:
                names.append(name)
                trueSame.append(int(name.split('_')[0]))
                if name.endswith('plus.xml'):
                    trueDiff.append(-1 * int(name.split('_')[0]))
                else:
                    trueDiff.append(int(name.split('_')[0]))
            cnum += 1

        scoreSame = adjusted_rand_score(trueSame, pred)
        scoreDiff = adjusted_rand_score(trueDiff, pred)
        logging.debug('Num clusters: %d\t\tScore (same): %.5f\t\tScore (diff): %.5f' % (numClusters, scoreSame, scoreDiff))
        if  scoreDiff > bestScoreDiff:   # Uses different as the final metric
            bestScoreSame = scoreSame
            bestScoreDiff = scoreDiff
            bestNumClusters = numClusters
            bestClusters = zip(names, pred)
    return (bestScoreSame, bestScoreDiff, bestNumClusters, bestClusters)

def writeToFile(bnc, bss, bsd, bc):
    with open(GRAPH_CLUSTER_OUTPUT, 'w') as f:
        f.write('Best number of clusters: %d\tScore (same): %.5f\tScore (diff): %.5f\n' % (bnc, bss, bsd))
        for (name, clust) in bc:
            f.write('%d\t%s\n' % (clust, name))

def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('Deserializing graph')
    graph = deserializeGraph(GRAPH_OUTPUT)
    logging.debug('Getting event nodes')
    eventNodes = getEventNodes(graph)
    logging.debug('Extracting features')
    (feature_matrix, names) = extractFeatures(graph, eventNodes)
    logging.debug('Clustering')
    (bss, bsd, bnc, bc) = cluster(feature_matrix, names)
    logging.debug('Writing clusters to file')
    writeToFile(bss, bsd, bnc, bc)

if __name__ == '__main__':
    main()
