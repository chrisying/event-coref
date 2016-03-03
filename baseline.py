# Baseline clustering using bag-of-words on ECB data

import os

import numpy as np

DIR = 'ecb/txt/'

def main():
    events = []
    dictionary = {}
    counter = 0
    # First pass to get term dictionary
    for filename in os.listdir(DIR):
        with open(DIR + filename) as f:
            for line in f.xreadlines():
                for word in line.split():
                    if word not in dictionary:
                        dictionary[word] = counter
                        counter += 1


    # Second pass to create vectors
    for filename in os.listdir(DIR):
        vector = np.zeros(counter)
        with open(DIR + filename) as f:
            for line in f.xreadlines():
                for word in line.split():
                    vector[dictionary[word]] = 1

        events.append((filename, vector))

    print events



if __name__ == '__main__':
    main()
