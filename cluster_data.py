# WARNING: this code uses eval, make sure you trust GRAPH_OUTPUT
import networkx as nx

from scipy.sparse import csr_matrix
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score
from sklearn.neighbors import kneighbors_graph

from constants import *
from node import Node
from cluster import ClusterByUFS

import logging

# Read graph from path
def deserializeGraph(path):
    graph = nx.DiGraph()
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
    vc = 0
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
    with open('feature_matrix', 'w') as f:
        for i in range(feature_matrix.shape[0]):
            f.write('%s ' % names[i])
            for b in feature_matrix.getrow(i).toarray()[0]:
                f.write('%d ' % b)
            f.write('\n')

    return (feature_matrix, names)

# Does basic agglomerative clustering
def cluster(feature_matrix, names):
    return ClusterByUFS(feature_matrix, names)

def writeToFile(bss, bsd, bnc, names, bc):
    with open(GRAPH_CLUSTER_OUTPUT, 'w') as f:
        f.write('Best number of clusters: %d\tScore (same): %.5f\tScore (diff): %.5f\n' % (bnc, bss, bsd))
        for (name, clust) in zip(names, bc):
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
    writeToFile(bss, bsd, bnc, names, bc)

if __name__ == '__main__':
    main()
