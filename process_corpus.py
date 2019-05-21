#!/usr/bin/env python3
from textacy.corpus import Corpus
import sys

def main():
    with open(sys.argv[1]) as infile:
        corp = Corpus('en')
        corp.add(infile)
        corp.save(sys.argv[1].rsplit('.', 1)[0] + '.corpus')

if __name__ == '__main__':
    main()

