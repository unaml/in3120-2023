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
        haystack = self.__haystack
        suffixes = self.__suffixes

        for docid, doc in enumerate(self.__corpus):
            concatenated_text = ""  # Initialize concatenated_text for each document
            for field in fields:
                text = doc.get_field(field, "")
                concatenated_text += "".join(text)

            tokens = self.__tokenizer.strings(
                self.__normalize(concatenated_text))
            normalized_and_tokenized = " ".join(tokens)
            haystack.append((docid, normalized_and_tokenized))

        # Create suffixes for each word
        for docid, text in haystack:
            words = text.split()
            offset = 0
            for i, word in enumerate(words):
                suffixes.append((docid, offset))
                offset += len(word) + 1

        suffixes.sort(key=lambda x: self.__get_item(x))
        """ for i in haystack:
            print("haystack", haystack)
        print("suffixes", suffixes)
        for i in suffixes:
            print("suffixes", self.__get_item(i))"""

    """
        haystack = [
            [docid, self.__normalize(self.__tokenizer.tokens(" ".join([doc.get_field(field, "")
                                                                       for field in fields])))]
            for docid, doc in enumerate(self.__corpus)
        ]
        suffixes = sorted([(docid, i)
                          for docid, text in haystack for i in range(len(text))])

        # Store the suffix array in self.__suffixes
        self.__suffixes = suffixes
        hayindex,start = element
        doc, string = self.hsystdsck(hayindx)
        substring = string[start:]
        return substring
        """

    def __get_item(self, element: Tuple[int, int]) -> str:
        # Separate tuple into two variables
        hayindex, start = element

        # If hayindex is between 0 and the length of the haystack, find its respective string based on input
        if 0 <= hayindex < len(self.__haystack):
            _, string = self.__haystack[hayindex]
            substring = string[start:]
            return substring
        else:
            return ""

    def __normalize(self, buffer: str) -> str:
        """
        Produces a normalized version of the given string. Both queries and documents need to be
        identically processed for lookups to succeed.
        """
        # also canonicalize, but make sure you dont get double spacee, but join on spaces
        return self.__normalizer.canonicalize(self.__normalizer.normalize(buffer))

    def __binary_search(self, needle: str) -> int:
        low = 0
        high = len(self.__suffixes) - 1
        pos = -1

        # If given query is empty, return -1
        if needle == "":
            return pos

        # Finds first occurence instead of the typical binary search way, this makes it easier for while loop in evaluate
        while low <= high:
            mid = (low + high) // 2
            substring = self.__get_item(self.__suffixes[mid])
            if substring.startswith(needle):
                pos = mid
                high = mid - 1
            elif substring < needle:
                low = mid + 1
            else:
                high = mid - 1
        return pos

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
        dictionary = []

        normalized_query = self.__normalize(query)
        position = self.__binary_search(normalized_query)

        max_hit_count = options.get("hit_count", float("inf"))
        sieve = Sieve(max_hit_count)

        normalized_query = self.__normalize(query)
        position = self.__binary_search(normalized_query)
        while (position < len(self.__suffixes)):
            if self.__get_item(self.__suffixes[position]).startswith(normalized_query):
                the_suffix = self.__suffixes[position]
                docid, _ = self.__haystack[the_suffix[0]]
                doc_text = self.__haystack[the_suffix[0]][1]
                # Calculate the score for this specific document
                doc_score = doc_text.count(query)
                dictionary.append(
                    {"score": doc_score, "document": docid})
                sieve.sift(doc_score, docid)
                position += 1
                if position >= len(self.__suffixes):
                    break
            else:
                break

        dictionary.sort(key=lambda x: x["score"], reverse=True)

        for doc_score, document in sieve.winners():
            yield {"score": doc_score, "document": self.__corpus.get_document(document)}
