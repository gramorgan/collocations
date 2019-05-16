#!/usr/bin/env python3

import sys
import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab
from collections import defaultdict
from math import log

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

def calc_minfo(dep_counts, dep, mod, head):
    total_num        = sum_for(dep_counts)
    num_dep          = sum_for(dep_counts, dep=dep)
    num_dep_head     = sum_for(dep_counts, dep=dep, head=head)
    num_dep_mod      = sum_for(dep_counts, dep=dep,  mod=mod )
    num_dep_mod_head = sum_for(dep_counts, dep=dep,  mod=mod , head=head)

    print(num_dep_mod_head)

    p_abc  = (num_dep_mod_head - 0.95) / total_num
    p_b    = num_dep          / total_num
    p_a_gb = num_dep_head     / num_dep
    p_c_gb = num_dep_mod      / num_dep

    if p_b * p_a_gb * p_c_gb == 0:
        return 0

    return log(p_abc/(p_b * p_a_gb * p_c_gb), 2)

def sum_for(dep_counts, **kwargs):
    dep  = kwargs.get('dep',  None)
    mod  = kwargs.get('mod',  None)
    head = kwargs.get('head', None)

    deps  = [dep_counts[dep]]       if dep  else dep_counts.values()
    mods  = [d[mod]  for d in deps] if mod  else [m for d in deps for m in d.values()]
    heads = [m[head] for m in mods] if head else [h for m in mods for h in m.values()]

    return sum(heads)

if __name__ == '__main__':
    main()
