import copy

import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.metrics import adjusted_rand_score

#class Cluster:
#    def __init__(self, name, vector):
#        # Vector is a csr_matrix (1 x n)
#        self.names = [name]
#        self.vectors = [vector]
#
#    def __str__(self):
#        return 'Cluster(%s)' % str(self.names)
#
#    def combine(self, other):
#        self.names += other.names
#        self.vectors += other.vectors
#
#    def distance(self, other):
#        # Cosine distance of min link
#        mindist = -1
#        for v1 in self.vectors:
#            for v2 in other.vectors:
#                dt = v1.dot(v2.transpose())
#                n1 = v1.dot(v1.transpose())
#                n2 = v2.dot(v2.transpose())
#                dif = 1.0 - dt.data[0] / (np.sqrt(n1) * np.sqrt(n2)).data[0]
#                if dif < mindist or mindist == -1:
#                    mindist = dif
#
#        return mindist
#
#    def getCluster(self):
#        return self.names

def find(U, x):
    if U[x] != x:
        U[x] = find(U, U[x])
    return U[x]

# feature_matrix is a sparse N x M matrix,
# names is array of N names, for each row
def ClusterByUFS(feature_matrix, names):
    #clusters = []
    #for row in xrange(feature_matrix.shape[0]):
    #    clusters.append(Cluster(names[row], feature_matrix.getrow(row)))

    num_rows = feature_matrix.shape[0]
    true_labels_same = []
    true_labels_diff = []
    for name in names:
        n = int(name.split('_')[0])
        true_labels_same.append(n)
        if name.endswith('plus.xml'):
            true_labels_diff.append(-1 * n)
        else:
            true_labels_diff.append(n)

    pwd = pairwise_distances(feature_matrix, metric="cosine")
    edge_distances = []
    for i in xrange(num_rows):
        for j in xrange(i+1, num_rows):
            edge_distances.append((i,j,pwd[i,j]))
    dtype = [('src', int), ('dst', int), ('dist', float)]
    sorted_distances = np.sort(np.array(edge_distances, dtype=dtype), order='dist')

    # UFS structure (initially all point to self)
    num_clusters = num_rows
    clusters = range(num_rows)
    rank = [0] * num_rows
    best_score_same = -1.0
    best_score_diff = -1.0
    best_num_clusters = 0
    best_cluster = None

    for i in xrange(sorted_distances.shape[0]):
        edge = sorted_distances[i]
        v1 = edge[0]
        v2 = edge[1]

        root1 = find(clusters, v1)
        root2 = find(clusters, v2)

        if root1 == root2:
            continue

        # Union
        if rank[root1] < rank[root2]:
            clusters[root1] = root2
        elif rank[root1] > rank[root2]:
            clusters[root2] = root1
        else:
            clusters[root2] = root1
            rank[root1] += 1

        num_clusters -= 1
        score_same = adjusted_rand_score(true_labels_same, clusters)
        score_diff = adjusted_rand_score(true_labels_diff, clusters)
        print 'Number of clusters: %d\tScore (same): %.5f\tScore (diff): %.5f' % (num_clusters, score_same, score_diff)

        if best_score_diff < score_diff:
            best_num_clusters = num_clusters
            best_cluster = copy.deepcopy(clusters)
        best_score_same = max(best_score_same, score_same)
        best_score_diff = max(best_score_diff, score_diff)

    return (best_score_same, best_score_diff, best_num_clusters, best_cluster)
