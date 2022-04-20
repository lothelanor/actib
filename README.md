# The Annotated Corpora of Tibetan

!!!DISCLAIMER: WORK IN PROGRESS!!!

This repository will soon contain all scripts and links to the annotated corpora of Tibetan: ACTib and PACTib.

The PArsed Corpus of Tibetan is new resource is uniquein bringing together a large number of Tibetan texts (>5000) from the 11th century until the present day. The texts in this diachronic corpus are provided with metadatacontaining information on dates and patron-/authorship and linguistic annotation in theform of tokenisation, sentence segmentation, part-of-speech tags and syntactic phrasestructure. With over 166 million tokens across 11 centuries and a variety of genres, PACTib will open up a wide range of research opportunities for historical and comparativelinguistics and scholars in Tibetan Studies, which we illustrate with two short case studies.

Please cite the accompanying papers, which can be found here:

Meelen & Roux 2020, 'Meta-dating the PArsed Corpus of Tibetan (PACTib)' *Proceedings of the 19th International Workshop on Treebanks and Linguistic Theories*, pp. 31–42, DOI: https://www.aclweb.org/anthology/2020.tlt-1.3/

Meelen, Roux & Hill 2021, 'Optimisation of the Largest Annotated Tibetan Corpus Combining Rule-based, Memory-based, and Deep-learning Methods' *ACM Transactions on Asian and Low-Resource Language Information Processing* Volume 20:1, pp 1–11, DOI: https://dl.acm.org/doi/10.1145/3409488

## Tools & Dependencies

This repo currently presents tools to segment and POS tag Classical Tibetan specifically, focused on subsequent linguistic tasks (but useful for any downstream NLP tasks). It combines Esukhia's BOTOK tokeniser with a syllable-based classifier for optimal Classical Tibetan segmentation and uses the Memory-Based Tagger for POS tagging:

- [Botok tokeniser](https://github.com/Esukhia/botok)
- [Memory-Based Tagger](https://github.com/LanguageMachines/mbt/)

It also contains a preliminary sentence segmenter, which is currently only optimised for specific project purposes.

NOTE that for POS tagging, we also tested neural-network based approaches, but results are still worse for Classical Tibetan, which is why we keep using the MBT for now. Preliminary tests with improved word embeddings indicate accuracies for BiLSTM-RNN taggers are likely to improve as soon as better embeddings are implemented (see Meelen, Roux & Hill 2021).

## Word Segmentation & POS tagging

To segment words and POS tag texts run:

`python pos-directory.py <my_folder>`

## Sentence Segmentation

To run the sentence segmentation script:

`python SentSeg.py <my_text.txt>`

## Querying POS-tagged files

POS-tagged files can be queried with the dedicated queryPOS.py script, which allows for queries for 1-5 POS sequences as well as wildcards (using \*).

`python queryPOS.py <my_folder>`

It produces an output folder with one text file listing all exact matches as well as matches in context for each input text. Total number of hits per file and for the entire folder are also calculated.

## Available Corpora

The current version of the Annotated Corpus of Classical Tibetan (ACTIB) can be found on [Zenodo](https://zenodo.org/record/3951503#.Yh5VWsanxqs).
