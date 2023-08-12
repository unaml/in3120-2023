#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
from typing import Callable, Any
from context import in3120


# The colorama module is not part of the Python standard library.
# For self-containment reasons, make it optional and have output
# colorization reduce to a NOP if it's not installed.
try:
    from colorama import Fore, Style
except ImportError:
    print("Colorization disabled, 'pip install colorama' to enable.")
    class Fore:
        GREEN = ""
        RED = ""
        LIGHTYELLOW_EX = ""
        LIGHTBLUE_EX = ""
    class Style:
        RESET_ALL = ""


def data_path(filename: str):
    here = os.path.dirname(__file__)
    data = os.path.join(here, "..", "data")
    full = os.path.abspath(os.path.join(data, filename))
    return full


def simple_repl(prompt: str, evaluator: Callable[[str], Any]):
    from timeit import default_timer as timer
    import pprint
    printer = pprint.PrettyPrinter()
    print(f"{Fore.LIGHTYELLOW_EX}Ctrl-C to exit.{Style.RESET_ALL}")
    try:
        while True:
            print(f"{Fore.GREEN}{prompt}>{Fore.RED}", end="")
            query = input()
            start = timer()
            matches = evaluator(query)
            end = timer()
            print(Fore.LIGHTBLUE_EX, end="")
            printer.pprint(matches)
            print(f"{Fore.LIGHTYELLOW_EX}Evaluation took {end - start} seconds.{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"{Fore.LIGHTYELLOW_EX}\nBye!{Style.RESET_ALL}")


def repl_a_1():
    print("Building inverted index from Cranfield corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("cran.xml"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    print("Enter one or more index terms and inspect their posting lists.")
    simple_repl("terms", lambda ts: {t: list(index.get_postings_iterator(t)) for t in index.get_terms(ts)})


def repl_b_1():
    print("Building suffix array from Cranfield corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("cran.xml"))
    engine = in3120.SuffixArray(corpus, ["body"], normalizer, tokenizer)
    options = {"debug": False, "hit_count": 5}
    print("Enter a prefix phrase query and find matching documents.")
    print(f"Lookup options are {options}.")
    print("Returned scores are occurrence counts.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options)))


def repl_b_2():
    print("Building trie from MeSH corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("mesh.txt"))
    dictionary = in3120.Trie()
    dictionary.add((normalizer.normalize(normalizer.canonicalize(d["body"])) for d in corpus), tokenizer)
    engine = in3120.StringFinder(dictionary, tokenizer)
    print("Enter some text and locate words and phrases that are MeSH terms.")
    simple_repl("text", lambda t: list(engine.scan(normalizer.normalize(normalizer.canonicalize(t)))))


def repl_b_3():
    print("Building suffix array from airport corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    filter = lambda d: d if d.get_field("type", "") != "closed" else None
    pipeline = in3120.DocumentPipeline([filter])
    corpus = in3120.InMemoryCorpus(data_path("airports.csv"), pipeline)
    engine = in3120.SuffixArray(corpus, ["id", "type", "name", "iata_code"], normalizer, tokenizer)
    options = {"debug": False, "hit_count": 5}
    print("Enter a prefix phrase query and find matching (non-closed) airports.")
    print(f"Lookup options are {options}.")
    print("Returned scores are occurrence counts.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options)))


def repl_c_1():
    print("Indexing English news corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("en.txt"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    ranker = in3120.SimpleRanker()
    engine = in3120.SimpleSearchEngine(corpus, index)
    options = {"debug": False, "hit_count": 5, "match_threshold": 0.5}
    print("Enter a query and find matching documents.")
    print(f"Lookup options are {options}.")
    print(f"Tokenizer is {tokenizer.__class__.__name__}.")
    print(f"Ranker is {ranker.__class__.__name__}.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options, ranker)))


def repl_d_1():
    print("Indexing MeSH corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.ShingleGenerator(3)
    corpus = in3120.InMemoryCorpus(data_path("mesh.txt"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    ranker = in3120.SimpleRanker()
    engine = in3120.SimpleSearchEngine(corpus, index)
    options = {"debug": False, "hit_count": 5, "match_threshold": 0.5}
    print("Enter a query and find matching documents.")
    print(f"Lookup options are {options}.")
    print(f"Normalizer is {normalizer.__class__.__name__}.")
    print(f"Tokenizer is {tokenizer.__class__.__name__}.")
    print(f"Ranker is {ranker.__class__.__name__}.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options, ranker)))


def repl_d_2():
    print("Indexing English news corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("en.txt"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    ranker = in3120.BetterRanker(corpus, index)
    engine = in3120.SimpleSearchEngine(corpus, index)
    options = {"debug": False, "hit_count": 5, "match_threshold": 0.5}
    print("Enter a query and find matching documents.")
    print(f"Lookup options are {options}.")
    print(f"Normalizer is {normalizer.__class__.__name__}.")
    print(f"Tokenizer is {tokenizer.__class__.__name__}.")
    print(f"Ranker is {ranker.__class__.__name__}.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options, ranker)))


def repl_d_3():
    print("Indexing English news corpus...")
    normalizer = in3120.PorterNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("en.txt"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    ranker = in3120.BetterRanker(corpus, index)
    engine = in3120.SimpleSearchEngine(corpus, index)
    options = {"debug": False, "hit_count": 5, "match_threshold": 0.5}
    print("Enter a query and find matching documents.")
    print(f"Lookup options are {options}.")
    print(f"Normalizer is {normalizer.__class__.__name__}.")
    print(f"Tokenizer is {tokenizer.__class__.__name__}.")
    print(f"Ranker is {ranker.__class__.__name__}.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options, ranker)))


def repl_d_4():
    print("Indexing randomly generated English names...")
    normalizer = in3120.SoundexNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("names.txt"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    ranker = in3120.BetterRanker(corpus, index)
    engine = in3120.SimpleSearchEngine(corpus, index)
    options = {"debug": False, "hit_count": 5, "match_threshold": 0.2}
    print("Enter a name and find phonetically similar names.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options, ranker)))


def repl_d_5():
    print("Indexing the set of airports in the world...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("airports.csv"))
    index = in3120.InMemoryInvertedIndex(corpus, ["id", "type", "name", "iata_code"], normalizer, tokenizer)
    ranker = in3120.BetterRanker(corpus, index)
    engine = in3120.SimpleSearchEngine(corpus, index)
    options = {"debug": False, "hit_count": 5, "match_threshold": 0.5}
    print("Enter a query and find matching airports.")
    print(f"Lookup options are {options}.")
    print(f"Normalizer is {normalizer.__class__.__name__}.")
    print(f"Tokenizer is {tokenizer.__class__.__name__}.")
    print(f"Ranker is {ranker.__class__.__name__}.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options, ranker)))


def repl_e_1():
    print("Initializing naive Bayes classifier from news corpora...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    languages = ["en", "no", "da", "de"]
    training_set = {language: in3120.InMemoryCorpus(data_path(f"{language}.txt")) for language in languages}
    classifier = in3120.NaiveBayesClassifier(training_set, ["body"], normalizer, tokenizer)
    print(f"Enter some text and classify it into {languages}.")
    print(f"Returned scores are log-probabilities.")
    simple_repl("text", lambda t: list(classifier.classify(t)))


def repl_x_1():
    normalizer = in3120.SimpleNormalizer()
    extractor = in3120.ShallowCaseExtractor()
    print(f"Enter some text and see what gets extracted based on simple case heuristics.")
    simple_repl("text", lambda t: list(extractor.extract(normalizer.canonicalize(t))))


def repl_x_2():
    normalizer = in3120.SoundexNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    print(f"Enter some text and see the Soundex codes.")
    simple_repl("text", lambda t: [normalizer.normalize(token) for token in tokenizer.strings(normalizer.canonicalize(t))])


def repl_x_3():
    normalizer = in3120.PorterNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    print(f"Enter some text and see the stemmed terms.")
    simple_repl("text", lambda t: [normalizer.normalize(token) for token in tokenizer.strings(normalizer.canonicalize(t))])


def repl_x_4():
    print("Indexing English news corpus using an ANN index...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("en.txt"))
    engine = in3120.SimilaritySearchEngine(corpus, ["body"], normalizer, tokenizer)
    options = {"hit_count": 5}
    print(f"Enter a query and find matching documents.")
    print(f"Lookup options are {options}.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options)))


def main():
    repls = {
        "a-1": repl_a_1,
        "b-1": repl_b_1,
        "b-2": repl_b_2,
        "b-3": repl_b_3,
        "c-1": repl_c_1,
        "d-1": repl_d_1,
        "d-2": repl_d_2,
        "d-3": repl_d_3,
        "d-4": repl_d_4,
        "d-5": repl_d_5,
        "e-1": repl_e_1,
        "x-1": repl_x_1,
        "x-2": repl_x_2,
        "x-3": repl_x_3,
        "x-4": repl_x_4,
    }  # The first letter of each key aligns with an obligatory assignment.
    targets = sys.argv[1:]
    if not targets:
        print(f"{sys.argv[0]} [{'|'.join(key for key in repls.keys())}]")
    else:
        for target in targets:
            if target in repls:
                repls[target.lower()]()


if __name__ == "__main__":
    main()
