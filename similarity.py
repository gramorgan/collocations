#!/usr/bin/env python3

# use mutual information to identify colocations in a text corpus

import sys
import argparse
from textacy.corpus import Corpus
from textacy.cache import load_spacy_lang
from collections import defaultdict
from itertools import chain, combinations
from math import log

# set of dependancy types that we're interested in
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

htext=('if this argument is set, parse the input file into a dependency tree and save it to a .corp file.'
       'if this argument is not set, assume the input is a preparsed .corp file'
      )
parser.add_argument('-p', dest='parse_infile', action='store_true', help=htext)

htext='the minimum number of features required to consider a word. defaults to 5'
parser.add_argument('-f', dest='feat_thresh', type=int, default=5, help=htext)

htext='the number of similar words to print. defaults to 10'
parser.add_argument('-n', dest='num', type=int, default=10, help=htext)

def main():
    args = parser.parse_args()

    # if parsing input
    if args.parse_infile:
        with open(args.infile, 'r', encoding="utf8", errors='ignore') as f:
            pipeline = load_spacy_lang('en', disable=('tagger', 'ner', 'textcat'))
            corp = Corpus(pipeline)
            corp.add(f)
            corp.save(args.infile.rsplit('.', 1)[0] + '.corp')
    # if loading a preparsed corpus
    else:
        corp = Corpus.load('en', args.infile)

    # dictionary mapping dependency triples to their frequencies
    features = defaultdict(lambda: defaultdict(lambda: set()))

    # for every token in the corpus
    for tok in chain.from_iterable(corp.docs):
        if tok.is_alpha and tok.head.is_alpha and tok.dep_ in DEP_TYPES:
            feature = (tok.dep, tok.lemma)
            features[tok.head.pos][tok.head.lemma_.lower()].add(feature)

    top_similar = []
    for pos in features.keys():
        total_num = len(features[pos])
        global prob_cache
        prob_cache = {}
        for word_1, word_2 in combinations(features[pos].keys(), 2):
            sim = calc_similarity(features[pos], total_num, word_1, word_2, args.feat_thresh)
            if sim is None:
                continue

            if len(top_similar) < args.num:
                top_similar.append((sim, word_1, word_2))
            elif sim > top_similar[-1][0]:
                top_similar[-1] = (sim, word_1, word_2)
                top_similar.sort(reverse=True)

    print('{:>15} {:>15} {:>12}'.format('word 1', 'word 2', 'similarity'))
    for pair in top_similar:
        print('{0[1]:>15} {0[2]:>15} {0[0]:>12.3f}'.format(pair))
    print()

def calc_similarity(features, total_num, word_1, word_2, thresh):
    if len(features[word_1]) <= thresh or len(features[word_2]) <= thresh:
        return None
    word_1_minfo = calc_minfo_for_features(features, total_num, features[word_1])
    word_2_minfo = calc_minfo_for_features(features, total_num, features[word_2])
    intersect_set = features[word_1].intersection(features[word_2])
    intersect_minfo = calc_minfo_for_features(features, total_num, intersect_set)
    
    return (2 * intersect_minfo) / (word_1_minfo + word_2_minfo)

prob_cache = {}
def calc_minfo_for_features(features, total_num, feat_set):
    prob_list = []
    for feature in feat_set:
        if feature in prob_cache:
            prob = prob_cache[feature]
        else:
            count = count_num_with_feature(features, feature)
            prob = log(count / total_num, 2)
            prob_cache[feature] = prob
        prob_list.append(prob)
    return -sum(prob_list)

def count_num_with_feature(features, feature):
    count = 0
    for feat_set in features.values():
        if feature in feat_set:
            count += 1
    return count

if __name__ == '__main__':
    main()

