#!/usr/bin/python
# -*- coding: utf-8 -*-

import itertools
from abc import ABC, abstractmethod
from collections import Counter
from typing import Iterable, Iterator, List

from in3120.posting import Posting
from .dictionary import InMemoryDictionary
from .normalizer import Normalizer
from .tokenizer import Tokenizer
from .corpus import Corpus
from .posting import Posting
from .postinglist import CompressedInMemoryPostingList, InMemoryPostingList, PostingList


class InvertedIndex(ABC):
    """
    Abstract base class for a simple inverted index.
    """

    def __getitem__(self, term: str) -> Iterator[Posting]:
        return self.get_postings_iterator(term)

    def __contains__(self, term: str) -> bool:
        return self.get_document_frequency(term) > 0

    @abstractmethod
    def get_terms(self, buffer: str) -> Iterator[str]:
        """
        Processes the given text buffer and returns an iterator that yields normalized
        terms as they are indexed. Both query strings and documents need to be
        identically processed.
        """
        pass

    @abstractmethod
    def get_postings_iterator(self, term: str) -> Iterator[Posting]:
        """
        Returns an iterator that can be used to iterate over the term's associated
        posting list. For out-of-vocabulary terms we associate empty posting lists.
        """
        pass

    @abstractmethod
    def get_document_frequency(self, term: str) -> int:
        """
        Returns the number of documents in the indexed corpus that contains the given term.
        """
        pass


class InMemoryInvertedIndex(InvertedIndex):
    """
    A simple in-memory implementation of an inverted index, suitable for small corpora.

    In a serious application we'd have configuration to allow for field-specific NLP,
    scale beyond current memory constraints, have a positional index, and so on.

    If index compression is enabled, only the posting lists are compressed. Dictionary
    compression is currently not supported.
    """

    def __init__(self, corpus: Corpus, fields: Iterable[str], normalizer: Normalizer, tokenizer: Tokenizer, compressed: bool = False):
        self.__corpus = corpus
        self.__normalizer = normalizer
        self.__tokenizer = tokenizer
        self.__posting_lists : List[PostingList] = []
        self.__dictionary = InMemoryDictionary()
        self.__build_index(fields, compressed)

    def __repr__(self):
        return str({term: self.__posting_lists[term_id] for (term, term_id) in self.__dictionary})

    def __build_index(self, fields: Iterable[str], compressed: bool) -> None:
        frequency_counter = Counter()
        posting_lists = self.__posting_lists
        for docid, doc in enumerate(self.__corpus):
            for field in fields:
                text = doc.get_field(field, "")
                tokens = self.get_terms(text)
                for term in tokens:
                    termid = self.__dictionary.add_if_absent(term)
                    frequency_counter[termid] += 1
            for termid in frequency_counter:
                posting = Posting(docid, frequency_counter[termid])
                while len(self.__posting_lists) <= termid:
                    self.__posting_lists.append(InMemoryPostingList())
                posting_lists[termid].append_posting(posting)
            frequency_counter.clear()

    def get_terms(self, buffer: str) -> Iterator[str]:
        normalized_text = self.__normalizer.normalize(buffer)
        tokens = self.__tokenizer.strings(normalized_text)
        return tokens

    def get_postings_iterator(self, term: str) -> Iterator[Posting]:
        term_id = self.__dictionary.get_term_id(term)
        if term_id is None:
            return iter([])
        else:
            return self.__posting_lists[term_id].get_iterator()

    def get_document_frequency(self, term: str) -> int:
        term_id = self.__dictionary.get_term_id(term)
        if term_id is None:
            return 0
        else:
            return self.__posting_lists[term_id].get_length()
