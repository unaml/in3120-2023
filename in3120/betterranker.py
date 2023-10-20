#!/usr/bin/python
# -*- coding: utf-8 -*-

from .ranker import Ranker
from .corpus import Corpus
from .posting import Posting
from .invertedindex import InvertedIndex
import math


class BetterRanker(Ranker):
    """
    A ranker that does traditional TF-IDF ranking, possibly combining it with
    a static document score (if present).

    The static document score is assumed accessible in a document field named
    "static_quality_score". If the field is missing or doesn't have a value, a
    default value of 0.0 is assumed for the static document score.

    See Section 7.1.4 in https://nlp.stanford.edu/IR-book/pdf/irbookonlinereading.pdf.
    """

    def __init__(self, corpus: Corpus, inverted_index: InvertedIndex):
        self._score = 0.0
        self._document_id = None
        self._corpus = corpus
        self._inverted_index = inverted_index
        self._dynamic_score_weight = 1.0
        self._static_score_weight = 1.0
        self._static_score_field_name = "static_quality_score"

    def reset(self, document_id: int) -> None:
        self._document_id = document_id
        self._score = 0.0

    def update(self, term: str, multiplicity: int, posting: Posting) -> None:
        assert self._document_id == posting.document_id
        # Calculate term-frequency
        term_frequency = posting.term_frequency
        # Calculate document frequency of term
        doc_frequency = self._inverted_index.get_document_frequency(term)
        # Calculate idf score, log of total docs / doc frequency
        idf_score = math.log(self._corpus.size() /
                             doc_frequency, 2.0) if doc_frequency > 0 else 0.0
        # Multiply term-frequency with idf score to get tf-idf score
        tf_idf = term_frequency * idf_score

        # If static_quality_score exists in document, get value, if not, set to 0.0
        if self._static_score_field_name in self._corpus.get_document(self._document_id).get_field(self._static_score_field_name, ""):
            static_quality_score = self._corpus.get_document(
                self._document_id).get_field(self._static_score_field_name, "")
        else:
            static_quality_score = 0.0

        self._score = tf_idf * self._dynamic_score_weight + \
            static_quality_score * self._static_score_weight

    def evaluate(self) -> float:
        return self._score
