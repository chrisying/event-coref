'''
Generates some basic metrics about the pairwise corefence methods. Should be run after generating all predicted data using different combinations of features.

This script was used to generate the final results showed in the poster.
'''

BASELINE_FILE = 'predicted_baseline.out'
BOW_FILE = 'predicted_bow.out'
YAGO_FILE = 'predicted_yago.out'
DB_FILE = 'predicted_db.out'
BY_FILE = 'predicted_by.out'
BYD_FILE = 'predicted_byd.out'
PAIRS_FILE = 'output/test_pairs.out'

def main():

    totalLines = 0
    totalPositives = 0
    falseNegatives = 0
    bCorrectFalseNegative = 0
    berr = 0
    yCorrectFalseNegative = 0
    yerr = 0
    dCorrectFalseNegative = 0
    derr = 0
    byCorrectFalseNegative = 0
    byerr = 0
    bydCorrectFalseNegative = 0
    byderr = 0
    intersect = 0
    interr = 0
    union = 0
    unerr = 0
    voted = 0
    voterr = 0
    with open(BASELINE_FILE) as base, open(BOW_FILE) as bow, open(YAGO_FILE) as yago, open(DB_FILE) as db, open(BY_FILE) as by, open(BYD_FILE) as byd, open(PAIRS_FILE) as pf:
        for line in base.xreadlines():
            btoks = map(int, bow.readline().strip().split('\t'))
            ytoks = map(int, yago.readline().strip().split('\t'))
            dtoks = map(int, db.readline().strip().split('\t'))
            bytoks = map(int, by.readline().strip().split('\t'))
            bydtoks = map(int, byd.readline().strip().split('\t'))
            pfline = pf.readline()

            totalLines += 1
            toks = map(int, line.strip().split('\t'))

            #if toks[0] == 1 and pfline.find('head_match') == -1 and bydtoks[1] == 1:
            #    print pfline
            #if toks[0] == 1 and btoks[1] == 0 and bydtoks[1] == 1:
            #    print pfline

            if toks[0] == 1 and toks[1] == 0 and bydtoks[1] == 1 and pfline.find('head_match') == -1 and bytoks[1] == 0:
                print pfline

            if toks[0] == 1:
                totalPositives += 1
                if toks[1] == 0:
                    falseNegatives += 1
                    bCorrectFalseNegative += btoks[1]
                    yCorrectFalseNegative += ytoks[1]
                    dCorrectFalseNegative += dtoks[1]
                    byCorrectFalseNegative += bytoks[1]
                    bydCorrectFalseNegative += bydtoks[1]
                    votes = btoks[1] + ytoks[1] + dtoks[1] + bytoks[1] + bydtoks[1]
                    if btoks[1] and ytoks[1] and dtoks[1] and bytoks[1] and bydtoks[1]:
                        intersect += 1
                    if btoks[1] or ytoks[1] or dtoks[1] or bytoks[1] or bydtoks[1]:
                        union += 1
                    if votes >= 3:
                        voted += 1

            if toks[0] == 1:
                if btoks[1] != 1:
                    berr += 1
                if ytoks[1] != 1:
                    yerr += 1
                if dtoks[1] != 1:
                    derr += 1
                if bytoks[1] != 1:
                    byerr += 1
                if bydtoks[1] != 1:
                    byderr += 1
                if btoks[1] != 1 and ytoks[1] != 1 and dtoks[1] != 1 and bytoks[1] != 1 and bydtoks[1] != 1:
                    unerr += 1
                if btoks[1] != 1 or ytoks[1] != 1 or dtoks[1] != 1 or bytoks[1] != 1 or bydtoks[1] != 1:
                    interr += 1
                votes = btoks[1] + ytoks[1] + dtoks[1] + bytoks[1] + bydtoks[1]
                if votes < 3:
                    voterr += 1



    print 'Total lines: %d' % totalLines
    print 'Total positives: %d' % totalPositives
    print 'False negatives: %d' % falseNegatives
    print 'B Corrected: %d'% bCorrectFalseNegative
    print 'B err: %d' % berr
    print 'Y Corrected: %d'% yCorrectFalseNegative
    print 'Y err: %d' % yerr
    print 'D Corrected: %d'% dCorrectFalseNegative
    print 'D err: %d' % derr
    print 'BY Corrected: %d'% byCorrectFalseNegative
    print 'BY err: %d' % byerr
    print 'BYD Corrected: %d'% bydCorrectFalseNegative
    print 'BYD err: %d' % byderr
    print 'Union: %d' % union
    print 'Union err: %d' % unerr
    print 'Intersection: %d' % intersect
    print 'Intersection err: %d' % interr
    print 'Voted: %d' % voted
    print 'Voted err: %d' % voterr



if __name__ == '__main__':
    main()
