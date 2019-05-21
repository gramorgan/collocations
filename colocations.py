#!/usr/bin/env python3

import sys
from textacy.corpus import Corpus
from textacy.preprocess import normalize_whitespace
from textacy.cache import load_spacy_lang
from collections import defaultdict
from math import log

DEP_TYPES = set([
#    'nsubj',
#    'amod',
#    'nounmod',
#    'advmod',
#    'csubj',
#    'ccomp',
    'dobj',
])

def main():
    dep_triples = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))

    #with open(sys.argv[1]) as infile:
    #    pipeline = load_spacy_lang('en', disable=('tagger', 'ner', 'textcat'))
    #    corp = Corpus(pipeline)
    #    corp.add(infile)
    #    corp.save(sys.argv[1].rsplit('.', 1)[0] + '.corp')
    #return

    corp = Corpus.load('en', sys.argv[1])

    for doc in corp.docs:
        for tok in doc:
            if tok.dep_ in DEP_TYPES:
                dep_triples[tok.dep_][tok.text.lower()][tok.head.text.lower()] += 1

    #calc_minfo(dep_triples, 'dobj', 'paul', 'have')
    #return

    #for d in dep_triples:
    #    for m in dep_triples[d]:
    #        for h in dep_triples[d][m]:
    #            print(m, d, h)

    objects = [k for k,v in dep_triples['dobj'].items() if v['have']>0]
    obj_with_minfo = []
    for obj in objects:
        obj_with_minfo.append((calc_minfo(dep_triples, 'dobj', obj, 'have'), obj))

    for x in sorted(obj_with_minfo):
        print(x)

def calc_minfo(dep_triples, dep, mod, head):
    total_num        = sum_for(dep_triples)
    num_dep          = sum_for(dep_triples, dep=dep)
    num_dep_head     = sum_for(dep_triples, dep=dep, head=head)
    num_dep_mod      = sum_for(dep_triples, dep=dep,  mod=mod )
    num_dep_mod_head = sum_for(dep_triples, dep=dep,  mod=mod , head=head)

    p_abc  = (num_dep_mod_head - 0) / total_num
    p_b    = num_dep          / total_num
    p_a_gb = num_dep_head     / num_dep
    p_c_gb = num_dep_mod      / num_dep

    print(p_abc, p_b, p_a_gb, p_c_gb)

    return log(p_abc/(p_b * p_a_gb * p_c_gb), 2)

def sum_for(dep_triples, **kwargs):
    dep  = kwargs.get('dep',  None)
    mod  = kwargs.get('mod',  None)
    head = kwargs.get('head', None)

    deps  = [dep_triples[dep]]      if dep  else dep_triples.values()
    mods  = [d[mod]  for d in deps] if mod  else [m for d in deps for m in d.values()]
    heads = [m[head] for m in mods] if head else [h for m in mods for h in m.values()]

    return sum(heads)

if __name__ == '__main__':
    main()
