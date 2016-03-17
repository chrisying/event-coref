# Baseline clustering using bag-of-words on ECB data

import os

import numpy as np
from sklearn import metrics

from cluster import Cluster
from constants import *

def main():
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

    score = metrics.adjusted_rand_score(true, pred)
    print 'Score: %d/1.0' % score

    with open(BASELINE_CLUSTER_OUTPUT, 'w') as f:
        f.write('Score: %f\n' % score)
        for event in eventCluster:
            f.write('%d\t%s\n' % (eventCluster[event], event))

if __name__ == '__main__':
    main()
