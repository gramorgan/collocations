#!/usr/bin/env python3

import sys
import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab
from collections import defaultdict
from math import log

nlp = spacy.load('en')
nlp.max_length = 6000000

DEP_TYPES = set([
    'nsubj',
    'amod',
    'nounmod',
    'advmod',
    'csubj',
    'ccomp',
    'dobj',
])

def main():
    dep_triples = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))

    doc = Doc(nlp.vocab).from_disk(sys.argv[1])
    for tok in doc:
        if tok.dep_ in DEP_TYPES:
            dep_triples[tok.dep_][tok.text.lower()][tok.head.text.lower()] += 1

    print(calc_minfo(dep_triples, 'amod', 'terrible', 'purpose'))

def calc_minfo(dep_triples, dep, mod, head):
    total_num        = sum_for(dep_triples)
    num_dep          = sum_for(dep_triples, dep=dep)
    num_dep_head     = sum_for(dep_triples, dep=dep, head=head)
    num_dep_mod      = sum_for(dep_triples, dep=dep,  mod=mod )
    num_dep_mod_head = sum_for(dep_triples, dep=dep,  mod=mod , head=head)

    print(num_dep_mod_head)

    p_abc  = (num_dep_mod_head - 0.95) / total_num
    p_b    = num_dep          / total_num
    p_a_gb = num_dep_head     / num_dep
    p_c_gb = num_dep_mod      / num_dep

    if p_b * p_a_gb * p_c_gb == 0:
        return 0

    return log(p_abc/(p_b * p_a_gb * p_c_gb), 2)

def sum_for(dep_triples, **kwargs):
    dep  = kwargs.get('dep',  None)
    mod  = kwargs.get('mod',  None)
    head = kwargs.get('head', None)

    deps  = [dep_triples[dep]]       if dep  else dep_triples.values()
    mods  = [d[mod]  for d in deps] if mod  else [m for d in deps for m in d.values()]
    heads = [m[head] for m in mods] if head else [h for m in mods for h in m.values()]

    return sum(heads)

if __name__ == '__main__':
    main()
