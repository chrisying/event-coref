'''
Clusters the documents using the feature matrices previously generated in extract_features.py.

OLD code, see cluster_subevent.py for the code that clusters events.
'''

import networkx as nx

from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import pairwise_distances
import numpy as np

from constants import *
from node import Node
from cluster import ClusterByUFS

import logging

def deserializeFeatures():
    # BOW
    (names, bm) = makeMatrix(BOW_MATRIX)

    # YAGO
    (names, ym) = makeMatrix(YAGO_MATRIX)

    # DB
    (names, dm) = makeMatrix(DB_MATRIX)

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

def writeToFile(bss, bsd, bnc, bc, names, outfile):
    with open(outfile, 'w') as f:
        f.write('Best number of clusters: %d\tScore (same): %.5f\tScore (diff): %.5f\n' % (bnc, bss, bsd))
        for (name, clust) in zip(names, bc):
            f.write('%d\t%s\n' % (clust, name))

def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('Deserializing features')
    (names, bm, ym, dm) = deserializeFeatures()

    logging.debug('Computing PWD')
    pwdBOW = pairwise_distances(bm, metric="cosine")
    pwdYAGO = pairwise_distances(ym, metric="cosine")
    pwdDB = pairwise_distances(dm, metric="cosine")
    print pwdBOW

    # Baseline (BOW)
    logging.debug('Computing B clusters')
    (bss, bsd, bnc, bc) = ClusterByUFS(pwdBOW, names)
    writeToFile(bss, bsd, bnc, bc, names, BOW_CLUSTERS)

    # BOW + YAGO
    logging.debug('Computing BY clusters')
    pwdBY = np.add(np.multiply(pwdBOW, BOW_CST), np.multiply(pwdYAGO, YAGO_CST))
    (bss, bsd, bnc, bc) = ClusterByUFS(pwdBY, names)
    writeToFile(bss, bsd, bnc, bc, names, BOW_YAGO_CLUSTERS)

    # BOW + YAGO + DB
    logging.debug('Computing BYD clusters')
    pwdBYD = np.add(np.add(np.multiply(pwdBOW, BOW_CST), np.multiply(pwdYAGO, YAGO_CST)), np.multiply(pwdDB, DB_CST))
    (bss, bsd, bnc, bc) = ClusterByUFS(pwdBYD, names)
    writeToFile(bss, bsd, bnc, bc, names, BOW_YAGO_DB_CLUSTERS)


if __name__ == '__main__':
    main()
