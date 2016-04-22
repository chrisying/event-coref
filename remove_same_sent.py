
import os
from constants import *

def do(doc):
    with open(doc) as f, open('temp.txt', 'w') as fo:
        for line in f.xreadlines():
            toks = line.split('\t')
            s1 = toks[0].split(',')[1]
            s2 = toks[2].split(',')[1]
            if s1 != s2:
                fo.write(line)

    os.system('mv temp.txt ' + doc)


def main():
    do('events/train_event_mentionpairs.txt')
    do('events/test_event_mentionpairs.txt')


if __name__ == '__main__':
    main()

