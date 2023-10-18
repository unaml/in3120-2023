#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import Counter
from typing import Iterator, Dict, Any
from collections import Counter
from .sieve import Sieve
from .ranker import Ranker, SimpleRanker
from .corpus import Corpus
from .invertedindex import InvertedIndex
import sys


class SimpleSearchEngine:
    """
    Realizes a simple query evaluator that efficiently performs N-of-M matching over an inverted index.
    I.e., if the query contains M unique query terms, each document in the result set should contain at
    least N of these m terms. For example, 2-of-3 matching over the query 'orange apple banana' would be
    logically equivalent to the following predicate:

       (orange AND apple) OR (orange AND banana) OR (apple AND banana)

    Note that N-of-M matching can be viewed as a type of "soft AND" evaluation, where the degree of match
    can be smoothly controlled to mimic either an OR evaluation (1-of-M), or an AND evaluation (M-of-M),
    or something in between.

    The evaluator uses the client-supplied ratio T = N/M as a parameter as specified by the client on a
    per query basis. For example, for the query 'john paul george ringo' we have M = 4 and a specified
    threshold of T = 0.7 would imply that at least 3 of the 4 query terms have to be present in a matching
    document.
    """

    def __init__(self, corpus: Corpus, inverted_index: InvertedIndex):
        self.__corpus = corpus
        self.__inverted_index = inverted_index

    def evaluate(self, query: str, options: dict, ranker: Ranker) -> Iterator[Dict[str, Any]]:
        """
        Evaluates the given query, doing N-out-of-M ranked retrieval. I.e., for a supplied query having M
        unique terms, a document is considered to be a match if it contains at least N <= M of those terms.

        The matching documents, if any, are ranked by the supplied ranker, and only the "best" matches are yielded
        back to the client as dictionaries having the keys "score" (float) and "document" (Document).

        The client can supply a dictionary of options that controls the query evaluation process: The value of
        N is inferred from the query via the "match_threshold" (float) option, and the maximum number of documents
        to return to the client is controlled via the "hit_count" (int) option.
        """
        normalized_and_tokenized_query_terms = self.__inverted_index.get_terms(
            query)
        unique_terms = list(
            Counter(normalized_and_tokenized_query_terms).items())

        # Assign M
        m = len(unique_terms)
        # Assign N
        n = max(1, min(m, int(options['match_threshold']*m)))
        max_number_of_documents = options['hit_count']

        posting_list = []
        for term, _ in unique_terms:
            postings = self.__inverted_index[term]
            posting_list.append(postings)
        all_cursors = [next(p, None) for p in posting_list]
        active_cursors = [
            cursor for cursor in all_cursors if cursor is not None]
        sieve = Sieve(max_number_of_documents)
        # Set frontier to 0, which is the variable that keeps track of similar doc ids

        frontier = 0
        while len(active_cursors) >= n:
            lowest_id = sys.maxsize
            for cursor in active_cursors:
                if cursor.document_id < lowest_id:
                    lowest_id = cursor.document_id
                    frontier = 1
                elif cursor.document_id == lowest_id:
                    frontier += 1
            if frontier >= n:
                ranker.reset(lowest_id)
                for term, postings in zip(unique_terms, all_cursors):
                    current_term = term[0]
                    multiplicity = term[1]
                    if postings is not None and postings.document_id == lowest_id:
                        ranker.update(current_term, multiplicity, postings)
                score = ranker.evaluate()
                sieve.sift(score, lowest_id)

            cursor_indices = [i if (p is not None and p.document_id ==
                                    lowest_id) else -1 for i, p in enumerate(all_cursors)]

            for i, cursor in enumerate(all_cursors):
                if cursor_indices[i] != -1:
                    all_cursors[i] = next(posting_list[i], None)

            active_cursors = [
                cursor for cursor in all_cursors if cursor is not None]

        for doc_score, document in sieve.winners():
            yield {"score": doc_score, "document": self.__corpus.get_document(document)}
