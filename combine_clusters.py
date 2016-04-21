

import os
from constants import *

def process_dir(d):
    eventToCluster = {}
    sumARI = 0.0
    sumThresh = 0.0
    numDocs = 0
    offset = 0
    maxClusterNum = 0
    for fname in os.listdir(d):
        numDocs += 1
        if fname == 'combined.out':
            continue
        with open(d + fname) as f:
            line = f.readline() # first line
            toks = line.strip().split('\t')
            sumARI += float(toks[1].split(':')[1])
            sumThresh += float(toks[2].split(':')[1])

            for line in f.xreadlines():
                toks = line.strip().split('\t')
                cluster = int(toks[0]) + offset
                maxClusterNum = max(cluster, maxClusterNum)
                toks1 = toks[1].split('#')
                eventToCluster[(toks1[0], toks1[1], toks1[2], toks1[3])] = cluster
        offset = maxClusterNum + 1

    with open(EVENTS) as f1, open(d + 'combined.out', 'w') as f2:
        f2.write('Average ARI: %.5f\tAverage threshold: %.5f\n' % (sumARI/numDocs, sumThresh/numDocs))
        for line in f1.xreadlines():
            toks = line.strip().split('\t')
            toks1 = toks[1].split(',')
            key = (toks[0], toks1[0], toks1[1], toks1[2])
            if key not in eventToCluster:
                print 'WARNING: %s not in cluster output' % key
                f2.write('%s\t%s\tEVENT\tNA\t%s\n' % (toks[0], toks[1], toks[4]))
            else:
                f2.write('%s\t%s\tEVENT\t%d\t%s\n' % (toks[0], toks[1], eventToCluster[key], toks[4]))

def main():
    process_dir(BOW_CLUSTERS)
    process_dir(BOW_YAGO_CLUSTERS)
    process_dir(BOW_YAGO_DB_CLUSTERS)

if __name__ == '__main__':
    main()
