# Removes all features in the baseline pairwise clustering except head_match

import os
from constants import *

def do(doc):
    total = 0
    totalPos = 0
    posAndMatch = 0
    with open(doc) as f, open('temp.txt', 'w') as fo:
        for line in f.xreadlines():
            toks = line.split('\t')
            total += 1
            if toks[4] == '1':
                totalPos += 1
            if (toks[5].find('head_match') != -1):
                if toks[4] == '1':
                    posAndMatch += 1
            #    fo.write('\t'.join(toks[:5]) + '\thead_match:1 \n')
            #else:
            #    fo.write('\t'.join(toks[:5]) + '\t\n')

    #os.system('mv temp.txt ' + doc)
    print 'Total lines: %s\nTotal positives: %s\nTotal positives and match: %s' % (total, totalPos, posAndMatch)


def main():
    do('events/train_event_mentionpairs.txt')
    do('events/test_event_mentionpairs.txt')


if __name__ == '__main__':
    main()

