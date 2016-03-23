# Baseline clustering using bag-of-words on ECB data

import os

from scipy.sparse import csr_matrix
from sklearn.metrics import adjusted_rand_score

from cluster import Cluster
from constants import *

def main():

    indptr = [0]
    indices = []
    data = []
    vocabulary = {}
    names = []
    for filename in os.listdir(ANNOTATION_DIR):
        with open(ANNOTATION_DIR + filename) as f:
            fdata = eval(f.read())
            names.append(filename)
            for annotation in fdata['annotations']:
                entity = annotation['enUrl']
                index = vocabulary.setdefault(entity, len(vocabulary))
                indices.append(index)
                data.append(1)
            indptr.append(len(indices))

    feature_matrix = csr_matrix((data, indices, indptr), dtype=int)

    clusters = []
    for row in xrange(feature_matrix.shape[0]):
        clusters.append(Cluster(names[row], feature_matrix.getrow(row)))

    # print [str(c) for c in clusters]
    numClusters = len(clusters)
    bestScore = -1
    bestNumClusters = -1
    bestClusters = []
    while numClusters > 1:
        print 'Current number of clusters: %d' % (numClusters)
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
        true = []
        cnum = 0
        names = []
        for c in clusters:
            pred += [cnum] * len(c.names)
            for name in c.names:
                names.append(name)
                if name.endswith('plus.xml.txt'):
                    true.append(-1 * int(name.split('_')[0]))
                else:
                    true.append(int(name.split('_')[0]))
            cnum += 1

        score = adjusted_rand_score(true, pred)
        print 'Score: %.5f' % score
        if score > bestScore:
            bestScore = score
            bestNumClusters = numClusters
            bestClusters = zip(names, pred)

    with open(BASELINE_CLUSTER_OUTPUT, 'w') as f:
        f.write('Best number of clusters: %d\t\tScore: %f\n' % (bestNumClusters, bestScore))
        for (name, clust) in bestClusters:
            f.write('%d\t%s\n' % (clust, name))

if __name__ == '__main__':
    main()
