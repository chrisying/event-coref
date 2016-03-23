import numpy as np

class Cluster:
    def __init__(self, name, vector):
        # Vector is a csr_matrix (1 x n)
        self.names = [name]
        self.vectors = [vector]

    def __str__(self):
        return 'Cluster(%s)' % str(self.names)

    def combine(self, other):
        self.names += other.names
        self.vectors += other.vectors

    def distance(self, other):
        # Cosine distance of min link
        mindist = -1
        for v1 in self.vectors:
            for v2 in other.vectors:
                dt = v1.dot(v2.transpose())
                n1 = v1.dot(v1.transpose())
                n2 = v2.dot(v2.transpose())
                dif = 1.0 - dt.data[0] / (np.sqrt(n1) * np.sqrt(n2)).data[0]
                if dif < mindist or mindist == -1:
                    mindist = dif

        return mindist

    def getCluster(self):
        return self.names

