from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
from nltk.corpus import lin_thesaurus as thes
import ranker
import utils
import time
import os


def run_engine():
    """

    :return:
    """
    number_of_documents = 0

    config = ConfigClass()
    r = ReadFile(config.get__corpusPath())
    p = Parse()

    # read and parse data
    print("Start read data")
    start = time.time()
    dfs = r.read_and_concat_all_parquet_in_dir_of_dirs()
    print(f"Data reading done, time since process start: {(time.time()-start)/60} min")
    p.parse_corpus(dfs)
    print(f"Data parsing done, time since process start: {(time.time()-start)/60} min")

    # indexing the data
    if not os.path.exists('data'):
        os.mkdir('data')
        os.mkdir('data/docs')
        os.mkdir('data/terms_pointers')

    indexer = Indexer(p.dictionary, p.tweets_words_locations)
    indexer.indexing()
    print(f"Data indexing done, time since process start: {(time.time()-start)/60}")


def load_index():
    print('Load inverted index')
    inverted_index = utils.load_obj("dictionary")
    return inverted_index


def search_and_rank_query(query, inverted_index, k):
    p = Parse()
    Ranker = ranker.Ranker()
    query_as_list = p.parse_sentence(query,False)
    searcher = Searcher()
    docs, terms_doc_freq = searcher.relevant_docs_from_posting(query_as_list)
    ranked_docs = Ranker.tf_idf(docs, terms_doc_freq, query_as_list)
    return Ranker.fetch_top(ranked_docs, k)


def main():
    run_engine()
    query = input("Please enter a query: ")
    option = input("run a thesaurus? (this will take a much longer time) y / n ")
    if option == "y" or option == "Y":
        query = thesaurus(query)
    k = int(input("Please enter number of docs to retrieve: "))
    inverted_index = load_index()
    for doc_tuple in search_and_rank_query(query, inverted_index, k):
        print('tweet id: {}, score (TF-IDF): {}'.format(doc_tuple[0], doc_tuple[1]))

def thesaurus(query):
    string = query
    count = 0
    for term in query.split(" "):
        ans = thes.synonyms(term, fileid="simN.lsp")
        for word in ans:
            string = string + " " + word
            count += 1
            if count == 7:
                return string

    return string