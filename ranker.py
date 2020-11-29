import math
from collections import defaultdict


class Ranker:
    def __init__(self):
        self.final_results = dict()
        pass

    @staticmethod
    def rank_relevant_doc(relevant_doc):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param relevant_doc: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        return sorted(relevant_doc.items(), key=lambda item: item[1], reverse=True)

    @staticmethod
    def retrieve_top_k(sorted_relevant_doc, k=1):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """

        return sorted_relevant_doc[:k]

    def tf_idf(self, documents, query, max_docs: int = 2000):
        N = len(documents)
        q = len(query)
        for location, doc in enumerate(documents):
            sim = 0
            cosin_sim = 0
            denominator = 0
            for term in doc:
                dfi = 0
                for doc_ in documents:
                    for do_c in doc_:
                        if term[0] in do_c[0]:
                            dfi += 1
                tf = term[1]
                max_count = max(doc, key=lambda item:item[1])
                tf = tf / max_count[1]
                idf = math.log(N/dfi, 2)
                if term[0] in query:
                    sim = sim + tf * idf
                denominator = denominator + math.pow(tf*idf, 2)
            if denominator == 0:
                cosin_sim = 0
            else:
                cosin_sim = sim/(math.sqrt(q*denominator))
            self.final_results[location] = cosin_sim
        self.final_results = sorted(self.final_results.items(), key=lambda x: x[1], reverse=True)




