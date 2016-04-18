import networkx as nx

from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import pairwise_distances
import numpy as np

from constants import *
from node import Node
from cluster import ClusterByUFS

import logging
import os

# Get the names of the classes from the annotation dir
def getClasses():
    classes = []
    for filename in os.listdir(ANNOTATION_DIR):
        name = filename[:-4]
        docClass = name.split('_')[0] + 'ecb'
        if name.endswith('plus.xml'):
            docClass += 'plus'
        classes.append(docClass)
    return classes

def sentToVec():
    sdict = {}
    with open(BOW_MATRIX) as f:
        for line in f.xreadlines():
            name = line.split(' ')[0]
            vec = map(int, line.strip().split(' ')[1:])
            sdict[name] = vec
    return sdict

def deserializeFeatures(className, sentToVec):
    print 'deserializeFeatures(%s)' % className

    # YAGO
    (names, ym) = makeMatrix(YAGO_MATRICES + className + '.mat')

    # DB
    (names, dm) = makeMatrix(DB_MATRICES + className + '.mat')

    mat = []
    for name in names:
        toks = name.split('#')
        sent = '%s-%s' % (toks[1], toks[0][:-4])
        mat.append(sentToVec[sent])
    bm = np.array(mat)

    # bm is a dense matrix
    return (names, bm, ym, dm)

def makeMatrix(filename):
    with open(filename) as f:
        indptr = [0]
        indices = []
        data = []
        names = []
        for line in f.xreadlines():
            toks = line.split()
            names.append(toks[0])
            for i in range(len(toks)-1):
                b = toks[i+1]
                if b != 0:
                    indices.append(i)
                    data.append(b)
            indptr.append(len(indices))
    return (names, csr_matrix((data, indices, indptr), dtype=int))

def getTrueLabels():
    # names in form of 'doc.xml#sent#start#end#word'
    labelDict = {}

    with open(EVENTS) as f:
        for line in f.xreadlines():
            toks = line.strip().split('\t')
            locs = toks[1].split(',')
            nstr = '%s#%s#%s#%s#%s' % (toks[0], locs[0], locs[1], locs[2], toks[4])
            labelDict[nstr] = int(toks[3])

    return labelDict

def writeToFile(bs, bnc, bc, bt, names, outfile):
    with open(outfile, 'w') as f:
        f.write('Best number of clusters: %d\tScore: %.5f\tBest threshold: %.5f\n' % (bnc, bs, bt))
        for (name, clust) in zip(names, bc):
            f.write('%d\t%s\n' % (clust, name))

def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('Getting classes')
    classes = getClasses();
    labelDict = getTrueLabels()
    s2v = sentToVec()

    for c in classes:
        logging.debug('----ANALYZING %s----' % c)

        logging.debug('Deserializing features')
        (names, bm, ym, dm) = deserializeFeatures(c, s2v)
        true_labels = []
        for name in names:
            true_labels.append(labelDict[name])

        logging.debug('Computing PWD')
        pwdBOW = pairwise_distances(bm, metric="cosine")
        pwdYAGO = pairwise_distances(ym, metric="cosine")
        pwdDB = pairwise_distances(dm, metric="cosine")

        # Baseline (BOW)
        logging.debug('Computing B clusters')
        (bs, bnc, bc, bt) = ClusterByUFS(pwdBOW, names, true_labels)
        writeToFile(bs, bnc, bc, bt, names, BOW_CLUSTERS + c + '.out')

        # BOW + YAGO
        logging.debug('Computing BY clusters')
        pwdBY = np.add(np.multiply(pwdBOW, BOW_CST), np.multiply(pwdYAGO, YAGO_CST))
        (bs, bnc, bc, bt) = ClusterByUFS(pwdBY, names, true_labels)
        writeToFile(bs, bnc, bc, bt, names, BOW_YAGO_CLUSTERS + c + '.out')

        # BOW + YAGO + DB
        logging.debug('Computing BYD clusters')
        pwdBYD = np.add(np.add(np.multiply(pwdBOW, BOW_CST), np.multiply(pwdYAGO, YAGO_CST)), np.multiply(pwdDB, DB_CST))
        (bs, bnc, bc, bt) = ClusterByUFS(pwdBYD, names, true_labels)
        writeToFile(bs, bnc, bc, bt, names, BOW_YAGO_DB_CLUSTERS + c + '.out')


if __name__ == '__main__':
    main()
