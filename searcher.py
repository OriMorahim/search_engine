import pickle
import linecache
from ranker import Ranker
from collections import Counter
from parser_module import Parse


class Searcher:

    def __init__(self):#, inverted_index):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.parser = Parse()
        self.ranker = Ranker()
        #self.inverted_index = inverted_index

        with open('dictionary.pickle', 'rb') as handle:
            self.indexer = pickle.load(handle)


    def relevant_docs_from_posting(self, query: list):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        docs_pointers = []
        for token in query:
            if token in self.indexer.keys():
                pointer_to_docs = self.indexer[token]
                line = linecache.getline(pointer_to_docs[0], pointer_to_docs[1])
                line_data = line.split(sep=', [')
                docs = line_data[1][:-3].replace('),', ') |').split(" | ")
                docs_pointers.extend(docs)

        # if there are docs that contains the query tokens then read docs
        if len(docs_pointers)>0:
            docs = []
            docs_pointers = set(docs_pointers)
            for doc_pointer in docs_pointers:
                pointer = eval(doc_pointer)[1]
                line = linecache.getline(pointer[0], pointer[1])
                docs.append(eval(line))

            terms_doc_freq = Counter()
            for tweet_id, doc in docs:
                terms_doc_freq.update([term for term, freq in doc])

            return docs, terms_doc_freq

        # if all query tokens do not appear in the dictionary
        else:
            print("No relevant docs as been found")
            return ([], [])