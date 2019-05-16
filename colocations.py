#!/usr/bin/env python3

import sys
import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab
from collections import defaultdict

nlp = spacy.load('en')
nlp.max_length = 1200000

DEP_TYPES = set([
    'nsubj',
    'amod',
    'nounmod',
    'advmod',
    'csubj',
    'ccomp',
])

def main():
    dep_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))

    doc = Doc(nlp.vocab).from_disk(sys.argv[1])
    for tok in doc:
        if tok.dep_ in DEP_TYPES:
            dep_counts[tok.dep_][tok.text][tok.head.text] += 1

    print (len(dep_counts))


if __name__ == '__main__':
    main()
