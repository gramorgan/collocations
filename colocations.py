#!/usr/bin/env python3

import sys
import argparse
from textacy.corpus import Corpus
from textacy.cache import load_spacy_lang
from collections import defaultdict
from math import log

DEP_TYPES = set([
    'nsubj',
    'amod',
    'nounmod',
    'advmod',
    'csubj',
    'ccomp',
    'dobj',
])

parser = argparse.ArgumentParser(description='Retrieve colocations from a text corpus')

htext='the input file to be processed'
parser.add_argument('infile', help=htext)

htext='the head word to calculate mutual information for'
parser.add_argument('head', help=htext)

htext='the dependency to calculate mutual information for. defaults to direct object'
parser.add_argument('--dep', '-d', dest='dep', default='dobj', help=htext)

htext='the constant used to bias mutual information calculation. defaults to 0.95'
parser.add_argument('-c', dest='const', type=float, default=0.95, help=htext)

htext=('if this argument is set, parse the input file into a dependancy tree and save it to a .corp file.'
       'if this argument is not set, assume the input is a preparsed .corp file'
      )
parser.add_argument('-p', dest='parse_infile', action='store_true', help=htext)

def main():
    args = parser.parse_args()

    if args.parse_infile:
        with open(args.infile, 'r') as f:
            pipeline = load_spacy_lang('en', disable=('tagger', 'ner', 'textcat'))
            corp = Corpus(pipeline)
            corp.add(f)
            corp.save(args.infile.rsplit('.', 1)[0] + '.corp')
    else:
        corp = Corpus.load('en', args.infile)

    dep_triples = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))

    for doc in corp.docs:
        for tok in doc:
            if tok.dep_ in DEP_TYPES:
                dep_triples[tok.dep_][tok.lemma_.lower()][tok.head.lemma_.lower()] += 1

    print('mutual info for words with relationship {} to "{}" using constant {}:'.format(args.dep, args.head, args.const))
    print()
    print('{:>12} {:>15} {:>5}'.format('mutual info', 'word', 'freq'))

    mods_with_minfo = calc_minfo_for_set(dep_triples, args.dep, args.head, args.const)   
    for result in mods_with_minfo:
        print('{0[0]:>12.5} {0[1]:>15} {0[2]:>5}'.format(result))


def calc_minfo_for_set(dep_triples, dep, head, const):
    total_num        = sum_for(dep_triples)
    num_dep          = sum_for(dep_triples, dep=dep)
    num_dep_head     = sum_for(dep_triples, dep=dep, head=head)

    if (total_num == 0 or num_dep == 0 or num_dep_head == 0):
        print('not enough info to calculate mutual information')
        return

    mods = [k for k,v in dep_triples[dep].items() if v[head]>0]
    mods_with_minfo = []
    for mod in mods:
        num_dep_mod      = sum_for(dep_triples, dep=dep,  mod=mod )
        num_dep_mod_head = sum_for(dep_triples, dep=dep,  mod=mod , head=head)

        p_abc  = (num_dep_mod_head - const) / total_num
        p_b    = num_dep          / total_num
        p_a_gb = num_dep_head     / num_dep
        p_c_gb = num_dep_mod      / num_dep
        
        minfo = log(p_abc/(p_b * p_a_gb * p_c_gb), 2)
        mods_with_minfo.append( (minfo, mod, num_dep_mod_head) )

    return sorted(mods_with_minfo, reverse=True)

def calc_minfo(dep_triples, dep, mod, head):
    total_num        = sum_for(dep_triples)
    num_dep          = sum_for(dep_triples, dep=dep)
    num_dep_head     = sum_for(dep_triples, dep=dep, head=head)
    num_dep_mod      = sum_for(dep_triples, dep=dep,  mod=mod )
    num_dep_mod_head = sum_for(dep_triples, dep=dep,  mod=mod , head=head)

    p_abc  = (num_dep_mod_head - 0.95) / total_num
    p_b    = num_dep          / total_num
    p_a_gb = num_dep_head     / num_dep
    p_c_gb = num_dep_mod      / num_dep

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
