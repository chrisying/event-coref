import numpy as np
import scipy.spatial.distance as ssd

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
        return 'Cluster(%s)' % str(self.cluster)

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

        # Euclidean distance
        # dif = self.centroid - other.centroid
        # Cosine distance
        dif = ssd.cosine(self.centroid, other.centroid)
        return dif

    def cluster(self):
        return self.cluster

