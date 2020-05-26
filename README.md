# collocations
Collocation extraction using mutual information

This repo contains my term project for CS 250, completed with my partner Zhengqi Liu. It implements two different applications of mutual information to collocation extraction. collocations.py extracts the set of collocations for some fixed head and dependency. similarity.py extracts the most similar head words from a given text corpus. View the help output for these scripts with `./collocations.py -h` and `./similarity.py -h`.

Both of these scripts are based on algorithms outlined in [Extracting Collocations from Text Corpora](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.488.1007&rep=rep1&type=pdf) by Dekang Lin.

These scripts require Python 3 and textacy/spacy.
