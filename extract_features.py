import networkx as nx
from scipy.sparse import csr_matrix

import os
import logging

from constants import *
from node import Node

# Read graph from path
def deserializeGraph(path):
    logging.debug("Deserializing graph")
    graph = nx.DiGraph()
    with open(path) as f:
        numEdges = int(f.readline());
        for i in range(numEdges):
            line = f.readline().strip()
            (n1, n2) = eval(line)
            graph.add_edge(n1, n2)
    return graph

# Gets the nodes in the graph corresponding to high-level events (doc)
def getEventNodes():
    logging.debug("Creating event nodes")
    # Assumption: ecb/annotations contains exactly all the docs in the graph
    nodes = []
    for filename in os.listdir(ANNOTATION_DIR):
        nodes.append(Node(DOC, filename[:-4]))
    return nodes

# Extract BOW features
def extractBOWFeatures():
    logging.debug("Extraction BOW features")
    indptr = [0]
    indices = []
    data = []
    vocabulary = {}
    names = []
    for filename in os.listdir(ANNOTATION_DIR):
        print filename
        with open(ANNOTATION_DIR + filename) as f:
            fdata = eval(f.read())
            names.append(filename[:-8]) # Removes .xml.txt
            for word in fdata['words']:
                index = vocabulary.setdefault(word, len(vocabulary))
                indices.append(index)
                data.append(1)
            indptr.append(len(indices))

    # TODO: IDF & normalization
    feature_matrix = csr_matrix((data, indices, indptr), dtype=int)

    with open(BOW_MATRIX, 'w') as f:
        for i in range(feature_matrix.shape[0]):
            f.write('%s ' % names[i])
            for b in feature_matrix.getrow(i).toarray()[0]:
                f.write('%d ' % b)
            f.write('\n')

# Extract YAGO features
def extractYAGOFeatures(graph, eventNodes):
    logging.debug("Extracting YAGO features")
    indptr = [0]
    indices = []
    data = []
    vocabulary = {}
    names = []
    for node in eventNodes:
        names.append(node.nodeValue[:-4]) # Removes .xml
        desc = nx.descendants(graph, node)
        for d in desc:
            if d.nodeType == YAGO_ENTITY:
                index = vocabulary.setdefault(d.nodeValue, len(vocabulary))
                indices.append(index)
                data.append(1)
        indptr.append(len(indices))

    # TODO: weighting
    feature_matrix = csr_matrix((data, indices, indptr), dtype=int)
    with open(YAGO_MATRIX, 'w') as f:
        for i in range(feature_matrix.shape[0]):
            f.write('%s ' % names[i])
            for b in feature_matrix.getrow(i).toarray()[0]:
                f.write('%d ' % b)
            f.write('\n')

# Extract DB features
def extractDBFeatures(graph, eventNodes):
    logging.debug("Extracting DB features")
    indptr = [0]
    indices = []
    data = []
    vocabulary = {}
    names = []
    for node in eventNodes:
        names.append(node.nodeValue[:-4]) # Removes .xml
        desc = nx.descendants(graph, node)
        for d in desc:
            if d.nodeType == DB_ENTITY:
                index = vocabulary.setdefault(d.nodeValue, len(vocabulary))
                indices.append(index)
                data.append(1)
        indptr.append(len(indices))

    # TODO: weighting
    feature_matrix = csr_matrix((data, indices, indptr), dtype=int)
    with open(DB_MATRIX, 'w') as f:
        for i in range(feature_matrix.shape[0]):
            f.write('%s ' % names[i])
            for b in feature_matrix.getrow(i).toarray()[0]:
                f.write('%d ' % b)
            f.write('\n')

def main():
    logging.basicConfig(level=logging.DEBUG)
    graph = deserializeGraph(GRAPH_OUTPUT)
    events = getEventNodes()
    extractBOWFeatures()
    extractYAGOFeatures(graph, events)
    extractDBFeatures(graph, events)


if __name__ == '__main__':
    main()
