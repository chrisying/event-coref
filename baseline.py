# Baseline clustering using bag-of-words on ECB data

import os

import numpy as np

from cluster import Cluster
from constants import *

def main():
    events = []
    dictionary = {}
    counter = 0
    # First pass to get term dictionary
    for filename in os.listdir(ANNOTATION_DIR):
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
    print [str(c) for c in clusters]
    numClusters = len(events)
    while (numClusters > NUM_CLUSTERS):
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


if __name__ == '__main__':
    main()
