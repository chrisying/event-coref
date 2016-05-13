# Extracts a set of feature vectors for every single doc class (ex: 1_*ecb.xml)

import networkx as nx
from scipy.sparse import csr_matrix
import numpy as np

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
# Returns dictionary of doc class => list of doc nodes
def getEventNodes(graph):
    logging.debug("Creating event nodes")
    # Assumption: ecb/annotations contains exactly all the docs in the graph
    nodes = {}
    for filename in os.listdir(ANNOTATION_DIR):
        name = filename[:-4]
        docClass = name.split('_')[0] + 'ecb'
        if name.endswith('plus.xml'):
            docClass += 'plus'
        docNode = Node(DOC, name)
        try:
            eventNodes = graph.neighbors(docNode)
        except nx.NetworkXError:
            print '%s document is not in graph' % name
            continue
        if len(eventNodes) == 0:
            print 'WARNING: no events for doc %s' % name
        if docClass not in nodes:
            nodes[docClass] = []
        nodes[docClass] += (eventNodes)
    return nodes

# Extract BOW features
#def extractBOWFeatures():
#    logging.debug("Extraction BOW features")
#    indptr = [0]
#    indices = []
#    data = []
#    vocabulary = {}
#    names = []
#    for filename in os.listdir(ANNOTATION_DIR):
#        with open(ANNOTATION_DIR + filename) as f:
#            docName = filename[:-8] # Removes .xml.txt
#            fdata = eval(f.read())
#            breaks = fdata['spaces'] # Hopefully 1 space per word!
#            breakptr = 1
#            sentnum = 0
#            if docName.endswith('plus'):
#                sentnum += 1 # Offset by the URL in ECBplus docs
#
#            # TODO: there is a bug, ECBPLUS is 1-index, ECB is 0-indexed!
#            for word in fdata['normWords']:
#                #print 'Sentence %d, Word: %s' % (sentnum, word)
#                index = vocabulary.setdefault(word, len(vocabulary))
#                indices.append(index)
#                data.append(1)
#                if breaks[breakptr].find('\n') != -1: # last sentence also ends with \n
#                    names.append(str(sentnum) + '-' + docName)
#                    indptr.append(len(indices))
#                    sentnum += 1
#                breakptr += 1
#
#    # TODO: IDF & normalization
#    feature_matrix = csr_matrix((data, indices, indptr), dtype=int)
#
#    with open(BOW_MATRIX, 'w') as f:
#        for i in range(feature_matrix.shape[0]):
#            f.write('%s ' % names[i])
#            for b in feature_matrix.getrow(i).toarray()[0]:
#                f.write('%d ' % b)
#            f.write('\n')

def extractBOWFeatures():
    logging.debug("Extracting BOW features")
    indptr = [0]
    indices = []
    data = []
    vocabulary = {}
    names = []
    with open(ENTITIES) as f:
        for line in f.xreadlines():
            toks = line.strip().split('\t')
            name = '%s-%s' % (toks[1].split(',')[0], toks[0][:-4])
            if len(names) == 0:
                names.append(name)
            elif name != names[-1]:
                names.append(name)
                indptr.append(len(indices))
            for word in toks[3].split(' '):
                word = word.lower()
                index = vocabulary.setdefault(word, len(vocabulary))
                indices.append(index)
                data.append(1)
        indptr.append(len(indices))

    feature_matrix = csr_matrix((data, indices, indptr), dtype=int)

    # IDF
    #df = [0] * len(vocabulary)
    rows = feature_matrix.shape[0]
    #for row in range(rows):
    #    for idx in feature_matrix.getrow(row).nonzero()[1]:
    #        df[idx] += 1

    with open(BOW_MATRIX, 'w') as f:
        for i in range(rows):
            f.write('%s ' % names[i])
            for b in feature_matrix.getrow(i).toarray()[0]:
                #score = b * np.log((float(rows) + 1.0) / df[idx])
                #f.write('%.5f ' % score)
                f.write('%d ' % b)
            f.write('\n')

# Extract YAGO features
def extractYAGOFeatures(graph, eventNodes, docClass):
    logging.debug("Extracting YAGO features for " + docClass)
    indptr = [0]
    indices = []
    data = []
    vocabulary = {}
    names = []
    for node in eventNodes:
        names.append("%s#%d#%d#%d#%s" % (node.nodeValue[0], node.nodeValue[1][0][0], node.nodeValue[1][0][1], node.nodeValue[1][0][2], node.nodeValue[1][1]))
        desc = nx.descendants(graph, node)
        for d in desc:
            if d.nodeType == YAGO_ENTITY:

                # TFIDF-like effect
                tf = 0 # number of times it shows up in THIS docClass (i.e. num events in this class)
                df = 0 # number of times it shows up in ANY docClass (i.e. num events in any class)
                anc = nx.ancestors(graph, d)
                for a in anc:
                    if a.nodeType == EVENT:
                        df += 1
                        aName = a.nodeValue[0][:-4]
                        aClass = aName.split('_')[0] + 'ecb'
                        if aName.endswith('plus'):
                            aClass += 'plus'

                        if aClass == docClass:
                            tf += 1
                #score = float(tf) * np.log(float(NUM_EVENTS) / df)
                score = np.log(float(NUM_EVENTS) / df)

                index = vocabulary.setdefault(d.nodeValue, len(vocabulary))
                indices.append(index)
                data.append(score)
        indptr.append(len(indices))

    feature_matrix = csr_matrix((data, indices, indptr), dtype=float)

    # IDF
    #df = [0] * len(vocabulary)
    rows = feature_matrix.shape[0]
    #for row in range(rows):
    #    for idx in feature_matrix.getrow(row).nonzero()[1]:
    #        df[idx] += 1

    with open(YAGO_MATRICES + docClass + '.mat', 'w') as f:
        for i in range(rows):
            f.write('%s ' % names[i])
            for b in feature_matrix.getrow(i).toarray()[0]:
                #score = b * np.log((float(rows) + 1.0) / df[idx])
                #f.write('%.5f ' % score)
                f.write('%.5f ' % b)
            f.write('\n')

# Extract DB features
def extractDBFeatures(graph, eventNodes, docClass):
    logging.debug("Extracting DB features for " + docClass)
    indptr = [0]
    indices = []
    data = []
    vocabulary = {}
    names = []
    for node in eventNodes:
        names.append("%s#%d#%d#%d#%s" % (node.nodeValue[0], node.nodeValue[1][0][0], node.nodeValue[1][0][1], node.nodeValue[1][0][2], node.nodeValue[1][1]))
        desc = nx.descendants(graph, node)
        for d in desc:
            if d.nodeType == DB_ENTITY:
                # TFIDF-like effect
                tf = 0 # number of times it shows up in THIS docClass (i.e. num events in this class)
                df = 0 # number of times it shows up in ANY docClass (i.e. num events in any class)
                anc = nx.ancestors(graph, d)
                for a in anc:
                    if a.nodeType == EVENT:
                        df += 1
                        aName = a.nodeValue[0][:-4]
                        aClass = aName.split('_')[0] + 'ecb'
                        if aName.endswith('plus'):
                            aClass += 'plus'

                        if aClass == docClass:
                            tf += 1
                #score = float(tf) * np.log(float(NUM_EVENTS) / df)
                score = np.log(float(NUM_EVENTS) / df) # IDF only
                index = vocabulary.setdefault(d.nodeValue, len(vocabulary))
                indices.append(index)
                data.append(score)
        indptr.append(len(indices))

    feature_matrix = csr_matrix((data, indices, indptr), dtype=float)

    # IDF
    #df = [0] * len(vocabulary)
    rows = feature_matrix.shape[0]
    #for row in range(rows):
    #    for idx in feature_matrix.getrow(row).nonzero()[1]:
    #        df[idx] += 1

    with open(DB_MATRICES + docClass + '.mat', 'w') as f:
        for i in range(rows):
            f.write('%s ' % names[i])
            for b in feature_matrix.getrow(i).toarray()[0]:
                #score = b * np.log((float(rows) + 1.0) / df[idx])
                #f.write('%.5f ' % score)
                f.write('%.5f ' % b)
            f.write('\n')

def main():
    logging.basicConfig(level=logging.DEBUG)
    graph = deserializeGraph(GRAPH_OUTPUT)
    events = getEventNodes(graph)
    extractBOWFeatures()
    for docClass in events:
        extractYAGOFeatures(graph, events[docClass], docClass)
        extractDBFeatures(graph, events[docClass], docClass)


if __name__ == '__main__':
    main()
