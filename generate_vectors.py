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
    classes = set()
    for filename in os.listdir(ANNOTATION_DIR):
        name = filename[:-4]
        docClass = name.split('_')[0] + 'ecb'
        if name.endswith('plus.xml'):
            docClass += 'plus'
        classes.add(docClass)
    return classes

def sentToVec():
    sdict = {}
    with open(BOW_MATRIX) as f:
        for line in f.xreadlines():
            name = line.split(' ')[0]
            vec = map(float, line.strip().split(' ')[1:])
            sdict[name] = vec
    return sdict

def deserializeFeatures(className, sentToVec):
    if (className + '.mat') not in os.listdir(YAGO_MATRICES):
        print 'Skipping %s class' % className
        return ([], None, None, None)

    # YAGO
    (names, ym) = makeMatrix(YAGO_MATRICES + className + '.mat')

    # DB
    (names, dm) = makeMatrix(DB_MATRICES + className + '.mat')

    mat = []
    width = len(sentToVec[sentToVec.keys()[0]])
    for name in names:
        toks = name.split('#')
        sent = '%s-%s' % (toks[1], toks[0][:-4])
        if sent in sentToVec:
            mat.append(sentToVec[sent])
        else:
            mat.append([0] * width)
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
                b = float(toks[i+1])
                if b != 0.0:
                    indices.append(i)
                    data.append(b)
            indptr.append(len(indices))
    return (names, csr_matrix((data, indices, indptr), shape=(len(indptr)-1, len(toks)-1), dtype=float))

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

# Assumes pairsfile exists already, if not copy from events/...mentionpairs
def writePWD(pwd, names, cl, feature_name):
    # faster indexing
    namesToIndex = {}
    i = 0
    for n in names:
        n = '#'.join(n.split('#')[:-1])  # remove text
        if n.endswith('#'):
            n = n[:-1]
        namesToIndex[n] = i
        i += 1

    if int(cl.split('ecb')[0]) <= 25:
        pairs_file = 'output/train_pairs.out'
    else:
        pairs_file = 'output/test_pairs.out'

    with open(pairs_file) as f1, open('temp.out', 'w') as f2:
        for line in f1.xreadlines():
            toks = line.strip().split('\t')
            doc = toks[0].split(',')[0]
            tc = doc.split('_')[0] + 'ecb'
            if doc[:-4].endswith('plus'):
                tc += 'plus'
            if tc != cl:
                f2.write(line)
                continue
            found = True
            d1 = toks[0].split(',')
            key1 = '%s#%s#%s#%s' % (d1[0], d1[1], d1[2], d1[3])
            d2 = toks[2].split(',')
            key2 = '%s#%s#%s#%s' % (d2[0], d2[1], d2[2], d2[3])

            if key1 not in namesToIndex or key2 not in namesToIndex:
                print 'WARNING: %s or %s not in data' % (key1, key2)
                extra = '\n' # Don't write anything
            else:
                extra = '%s:%.5f \n' % (feature_name, 1.0-pwd[namesToIndex[key1], namesToIndex[key2]])
            f2.write(line[:-1] + extra)

    os.system('mv temp.out ' + pairs_file)

def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('Getting classes')
    classes = getClasses();
    labelDict = getTrueLabels()
    s2v = sentToVec()
    os.system('cp ' + TRAIN_PAIRS + ' output/train_pairs.out')
    os.system('cp ' + TEST_PAIRS + ' output/test_pairs.out')

    for c in classes:
        logging.debug('----ANALYZING %s----' % c)

        logging.debug('Deserializing features')
        (names, bm, ym, dm) = deserializeFeatures(c, s2v)
        if len(names) == 0:
            continue

        true_labels = []
        for name in names:
            true_labels.append(labelDict[name])

        logging.debug('Computing PWD')
        #pwdBOW = pairwise_distances(bm, metric="cosine")
        #writePWD(pwdBOW, names, c, 'entity_dist')
        pwdYAGO = pairwise_distances(ym, metric="cosine")
        writePWD(pwdYAGO, names, c, 'yago_dist')
        pwdDB = pairwise_distances(dm, metric="cosine")
        writePWD(pwdDB, names, c, 'db_dist')

        ## Baseline (BOW)
        #logging.debug('Computing B clusters')
        #(bs, bnc, bc, bt) = ClusterByUFS(pwdBOW, names, true_labels)
        #writeToFile(bs, bnc, bc, bt, names, BOW_CLUSTERS + c + '.out')

        ## BOW + YAGO
        #logging.debug('Computing BY clusters')
        #pwdBY = np.add(np.multiply(pwdBOW, BOW_CST), np.multiply(pwdYAGO, YAGO_CST))
        #(bs, bnc, bc, bt) = ClusterByUFS(pwdBY, names, true_labels)
        #writeToFile(bs, bnc, bc, bt, names, BOW_YAGO_CLUSTERS + c + '.out')

        ## BOW + YAGO + DB
        #logging.debug('Computing BYD clusters')
        #pwdBYD = np.add(np.add(np.multiply(pwdBOW, BOW_CST), np.multiply(pwdYAGO, YAGO_CST)), np.multiply(pwdDB, DB_CST))
        #(bs, bnc, bc, bt) = ClusterByUFS(pwdBYD, names, true_labels)
        #writeToFile(bs, bnc, bc, bt, names, BOW_YAGO_DB_CLUSTERS + c + '.out')


if __name__ == '__main__':
    main()
