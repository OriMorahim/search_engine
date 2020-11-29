from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import ranker
import utils


def run_engine(files_to_read: int = 100):
    """

    :return:
    """
    number_of_documents = 0

    config = ConfigClass()
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse()

    # read and parse data
    dfs = r.read_and_concat_all_parquet_in_dir_of_dirs()
    p.parse_corpus(dfs)

    # indexing the data
    indexer = Indexer(p.dictionary, p.tweets_words_locations)
    indexer.indexing()
    print('Finished parsing and indexing. files were exported')


def load_index():
    print('Load inverted index')
    inverted_index = utils.load_obj("dictionary")
    return inverted_index


def search_and_rank_query(query, inverted_index, k):
    p = Parse()
    query_as_list = p.parse_sentence(query)
    searcher = Searcher()
    docs, words_occ = searcher.relevant_docs_from_posting(query_as_list)
    ranked_docs = ranker.tf_idf(docs, query_as_list)
    return searcher.ranker.retrieve_top_k(ranked_docs, k)


def main():
    run_engine()
    query = input("Please enter a query: ")
    k = int(input("Please enter number of docs to retrieve: "))
    inverted_index = load_index()
    for doc_tuple in search_and_rank_query(query, inverted_index, k):
        print('tweet id: {}, score (TF-IDF): {}'.format(doc_tuple[0], doc_tuple[1]))
