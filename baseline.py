# Baseline clustering using bag-of-words on ECB data

import os

from scipy.sparse import csr_matrix
from sklearn.metrics import adjusted_rand_score

from cluster import ClusterByUFS
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
    with open('baseline_feature_matrix', 'w') as f:
        for i in range(feature_matrix.shape[0]):
            f.write('%s ' % names[i])
            for b in feature_matrix.getrow(i).toarray()[0]:
                f.write('%d ' % b)
            f.write('\n')

    (best_same, best_diff, best_num, best_cluster) = ClusterByUFS(feature_matrix, names)
    print 'Best number of clusters: %d\tScore (same): %.5f\tScore (diff): %.5f' % (best_num, best_same, best_diff)

    with open(BASELINE_CLUSTER_OUTPUT, 'w') as f:
        f.write('Best number of clusters: %d\tScore (same): %.5f\tScore (diff): %.5f\n' % (best_num, best_same, best_diff))
        for (name, clust) in zip(names, best_cluster):
            f.write('%d\t%s\n' % (clust, name))

if __name__ == '__main__':
    main()
