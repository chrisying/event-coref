# Clustering using min-linkage, implemented using Kruskal's algorithm

import copy

import numpy as np
from sklearn.metrics import adjusted_rand_score

def find(U, x):
    if U[x] != x:
        U[x] = find(U, U[x])
    return U[x]

# pwd is the pairwise distance array N x N
# names is array of N names, for each row
def ClusterByUFS(pwd, names, true_labels):
    #clusters = []
    #for row in xrange(feature_matrix.shape[0]):
    #    clusters.append(Cluster(names[row], feature_matrix.getrow(row)))

    num_rows = len(names)

    #pwd = pairwise_distances(feature_matrix, metric="cosine")
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
    best_score = -1.0
    best_num_clusters = 0
    best_cluster = None
    best_threshold = -1.0

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
        score = adjusted_rand_score(true_labels, clusters)
        print 'Number of clusters: %d\tScore: %.5f' % (num_clusters, score)

        if best_score < score:
            best_num_clusters = num_clusters
            best_cluster = copy.deepcopy(clusters)
            best_threshold = edge[2]
        best_score = max(best_score, score)

    return (best_score, best_num_clusters, best_cluster, best_threshold)
