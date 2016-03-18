# Baseline clustering using bag-of-words on ECB data

import os

from scipy.sparse import csr_matrix
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score
from sklearn.neighbors import kneighbors_graph

from cluster import Cluster
from constants import *

def main():

    indptr = [0]
    indices = []
    data = []
    vocabulary = {}
    true_labels = []
    for filename in os.listdir(ANNOTATION_DIR):
        with open(ANNOTATION_DIR + filename) as f:
            fdata = eval(f.read())
            if (filename.endswith('plus.xml.txt')):
                true_labels.append(-1 * int(filename.split('_')[0]))
            else:
                true_labels.append(int(filename.split('_')[0]))
            for annotation in fdata['annotations']:
                entity = annotation['enUrl']
                index = vocabulary.setdefault(entity, len(vocabulary))
                indices.append(index)
                data.append(1)
            indptr.append(len(indices))

    feature_matrix = csr_matrix((data, indices, indptr), dtype=int)
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

    '''
    events = []
    dictionary = {}
    counter = 0
    eventCluster = {}
    # First pass to get term dictionary and docs
    for filename in os.listdir(ANNOTATION_DIR):
        eventCluster[filename] = 0
        with open(ANNOTATION_DIR + filename) as f:
            data = eval(f.read())
            for annotation in data['annotations']:
                name = annotation['enUrl']
                if name not in dictionary:
                    dictionary[name] = counter
                    counter += 1


    # Second pass to create vectors
    for filename in os.listdir(ANNOTATION_DIR):
        vector = np.zeros(counter)
        with open(ANNOTATION_DIR + filename) as f:
            data = eval(f.read())
            for annotation in data['annotations']:
                name = annotation['enUrl']
                vector[dictionary[name]] = 1

        events.append((filename, vector))

    clusters = [Cluster(filename, vector) for (filename, vector) in events]
    # print [str(c) for c in clusters]
    numClusters = len(events)
    while (numClusters > NUM_CLUSTERS):
        print 'Current number of clusters: %d' % (numClusters)
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

    print [str(c) for c in clusters]

    c = 0
    for cl in clusters:
        for event in cl.getCluster():
            eventCluster[event] = c
        c += 1

    print eventCluster

    pred = []
    true = []
    for event in eventCluster:
        pred.append(eventCluster[event])
        true.append(int(event.split('_')[0]))

    score = adjusted_rand_score(true, pred)
    print 'Score: %d/1.0' % score
    '''

    with open(BASELINE_CLUSTER_OUTPUT, 'w') as f:
        f.write('Best number of clusters: %d\t\tScore: %f\n' % (best_nc, best_acc))
        i = 0
        for filename in os.listdir(ANNOTATION_DIR):
            f.write('%d\t%s\n' % (best_labels[i], filename))
            i += 1
        #for event in eventCluster:
        #    f.write('%d\t%s\n' % (eventCluster[event], event))

if __name__ == '__main__':
    main()
