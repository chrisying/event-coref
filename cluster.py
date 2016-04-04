import copy

import numpy as np
from sklearn.metrics import adjusted_rand_score

def find(U, x):
    if U[x] != x:
        U[x] = find(U, U[x])
    return U[x]

# pwd is the pairwise distance array N x N
# names is array of N names, for each row
def ClusterByUFS(pwd, names):
    #clusters = []
    #for row in xrange(feature_matrix.shape[0]):
    #    clusters.append(Cluster(names[row], feature_matrix.getrow(row)))

    num_rows = len(names)
    true_labels_same = []
    true_labels_diff = []
    for name in names:
        n = int(name.split('_')[0])
        true_labels_same.append(n)
        if name.endswith('plus'):
            true_labels_diff.append(-1 * n)
        else:
            true_labels_diff.append(n)

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
