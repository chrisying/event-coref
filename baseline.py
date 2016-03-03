# Baseline clustering using bag-of-words on ECB data

import os

import numpy as np

DIR = 'ecb/txt/'
CLUSTERS = 1

class Cluster:
    def __init__(self, name, vector):
        self.cluster = [name]
        self.centroid = vector
        self.dirty = False      # true after a combine but before an update
        self.sumv = vector
        self.numv = 1

    def __str__(self):
        if self.dirty:
            self.update()
        return '(Cluster: %s; Centroid: %s)' % (str(self.cluster), str(self.centroid))

    def combine(self, other):
        self.cluster += other.cluster
        self.dirty = True
        self.sumv += other.sumv
        self.numv += other.numv

    def update(self):
        self.centroid = self.sumv / self.numv
        self.dirty = False

    def distance(self, other):
        if self.dirty:
            self.update()

        # Currently Euclidean distance
        dif = self.centroid - other.centroid
        return np.dot(dif, dif)

def main():
    events = []
    dictionary = {}
    counter = 0
    # First pass to get term dictionary
    for filename in os.listdir(DIR):
        with open(DIR + filename) as f:
            for line in f.xreadlines():
                for word in line.split():
                    if word not in dictionary:
                        dictionary[word] = counter
                        counter += 1


    # Second pass to create vectors
    for filename in os.listdir(DIR):
        vector = np.zeros(counter)
        with open(DIR + filename) as f:
            for line in f.xreadlines():
                for word in line.split():
                    vector[dictionary[word]] = 1

        events.append((filename, vector))

    clusters = [Cluster(filename, vector) for (filename, vector) in events]
    numClusters = len(events)
    while (numClusters > CLUSTERS):
        minPair = None
        minDist = 2**31 - 1     # A large number
        for i in range(len(clusters)):
            for j in range(i+1, len(clusters)):
                c1 = clusters[i]
                c2 = clusters[j]
                dist = c1.distance(c2)
                if dist < minDist:
                    minDist = dist
                    minPair = (i, j)

        (i,j) = (minPair[0], minPair[1])
        clusters[i].combine(clusters[j])
        clusters = clusters[:j] + clusters[j+1:]
        numClusters -= 1


if __name__ == '__main__':
    main()
