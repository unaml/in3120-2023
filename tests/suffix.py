#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import Any, Dict, Iterator, Iterable, Tuple, List
from .corpus import Corpus
from .normalizer import Normalizer
from .tokenizer import Tokenizer
from .sieve import Sieve


class SuffixArray:
    """
    A simple suffix array implementation. Allows us to conduct efficient substring searches.
    The prefix of a suffix is an infix!

    In a serious application we'd make use of least common prefixes (LCPs), pay more attention
    to memory usage, and add more lookup/evaluation features.
    """

    def __init__(self, corpus: Corpus, fields: Iterable[str], normalizer: Normalizer, tokenizer: Tokenizer):
        self.__corpus = corpus
        self.__normalizer = normalizer
        self.__tokenizer = tokenizer
        # The (<document identifier>, <searchable content>) pairs.
        self.__haystack: List[Tuple[int, str]] = []
        # The sorted (<haystack index>, <start offset>) pairs.
        self.__suffixes: List[Tuple[int, int]] = []
        # Construct the haystack and the suffix array itself.
        self.__build_suffix_array(fields)

    def __build_suffix_array(self, fields: Iterable[str]) -> None:
        """
        Builds a simple suffix array from the set of named fields in the document collection.
        The suffix array allows us to search across all named fields in one go.

        Comments from assignment/lecturer:
        A naive construction of the suffix array is fine. By naive is meant building up an array
        that represents the possible suffixes, and then simply sorting this using a built-in sort.

        - List comprehensions are your friend when it comes to succinctly building the suffix array! Building the suffix
         array can be done in three lines of code: Two list comprehensions and a call to List.sort.
        - Consider writing a one-liner utility method for mapping from indices to strings. You'll use it for sorting, as part
        of the binary search, and for making sense of any matches.
        """
        for doc in self.__corpus:
            for field in fields:
                tokens = list(self.__tokenizer.strings(
                    self.__normalize(doc[field])))
                self.__haystack.append((doc.document_id, " ".join(tokens)))
                for i in range(len(tokens)):
                    self.__suffixes.append((doc.document_id, i))
        self.__suffixes.sort(
            key=lambda x: self.__get_corresponding_string_from_suffix_tuple(x))

    def __normalize(self, buffer: str) -> str:
        """
        Produces a normalized version of the given string. Both queries and documents need to be
        identically processed for lookups to succeed.
        """
        return " ".join(self.__tokenizer.strings(self.__normalizer.normalize(self.__normalizer.canonicalize(buffer))))

    def __binary_search(self, needle: str) -> int:
        """
        Does a binary search for a given normalized query (the needle) in the suffix array (the haystack).
        Returns the position in the suffix array where the normalized query is either found, or, if not found,
        should have been inserted.

        Kind of silly to roll our own binary search instead of using the bisect module, but seems needed
        prior to Python 3.10 due to how we represent the suffixes via (index, offset) tuples. Version 3.10
        added support for specifying a key.
        """
        # NOTE: Implementation is based on the iterative approach in this article, but rewritten to find the first
        # index that starts with the needle: https://www.geeksforgeeks.org/python-program-for-binary-search/
        low = 0
        high = len(self.__suffixes) - 1
        result = -1

        if needle == "":
            return result

        while low <= high:

            mid = (high + low) // 2

            current_string = self.__get_corresponding_string_from_suffix_tuple(
                self.__suffixes[mid])

            if current_string.startswith(needle):
                result = mid
                high = mid - 1

            elif current_string < needle:
                low = mid + 1

            else:
                high = mid - 1

        return result

    def evaluate(self, query: str, options: dict) -> Iterator[Dict[str, Any]]:
        """
        Evaluates the given query, doing a "phrase prefix search".  E.g., for a supplied query phrase like
        "to the be", we return documents that contain phrases like "to the bearnaise", "to the best",
        "to the behemoth", and so on. I.e., we require that the query phrase starts on a token boundary in the
        document, but it doesn't necessarily have to end on one.

        The matching documents are ranked according to how many times the query substring occurs in the document,
        and only the "best" matches are yielded back to the client. Ties are resolved arbitrarily.

        The client can supply a dictionary of options that controls this query evaluation process: The maximum
        number of documents to return to the client is controlled via the "hit_count" (int) option.

        The results yielded back to the client are dictionaries having the keys "score" (int) and
        "document" (Document).
        """
        query = self.__normalize(query)

        start_position = self.__binary_search(query)
        if start_position == -1:
            return iter([])

        doc_count = {}
        i = start_position
        while i < len(self.__suffixes):
            doc_id, offset = self.__suffixes[i]
            current_string_in_haystack = self.__get_corresponding_string_from_suffix_tuple(
                self.__suffixes[i])
            if not current_string_in_haystack.startswith(query):
                break
            if doc_id in doc_count:
                doc_count[doc_id] += 1
            else:
                doc_count[doc_id] = 1
            i += 1

        max_docs = min(options.get("hit_count", len(
            doc_count.items())), len(doc_count.items()))
        sieve = Sieve(size=max_docs)

        for doc_id, count in doc_count.items():
            sieve.sift(count, doc_id)
        winners = sieve.winners()
        for score, doc_id in winners:
            yield {"score": score, "document": self.__corpus.get_document(doc_id)}

    def __get_corresponding_string_from_suffix_tuple(self, suffix_tuple: Tuple[int, int]) -> str:
        haystack_index, start_offset = suffix_tuple
        _, content = self.__haystack[haystack_index]
        return_string = ' '.join(content.split()[start_offset:])
        return return_string
