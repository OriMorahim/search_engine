import io
import math

class Indexer:

    def __init__(self, parser_dictionary, parser_tweets_words_locations):#, config):
        self.max_tweets_in_file = 10000
        self.max_terms_in_file = 1500
        self.parser_dictionary = parser_dictionary
        self.parser_tweets_words_locations = parser_tweets_words_locations
        self.docs_locations = dict()
        self.indexer = dict()
        #self.config = config

    def index_docs(self):
        """
        :return:
        """
        file_name = "data/docs/docs_data_{}.txt"
        for counter, tweet in enumerate(self.parser_tweets_words_locations.items()):
            temp_file_name = file_name.format(math.floor(counter / self.max_tweets_in_file))
            tweet_id = tweet[0]
            tweet_data = tweet[1]

            # append line to file
            with io.open(temp_file_name, "a", encoding="utf-8") as f:
                f.write(f"{[(word, len(freq)) for word, freq in tweet_data.items()]},\n")
            f.close()

            # replace tweet data to tweet location in the original dict
            self.docs_locations[tweet_id] = (
                file_name,
                counter - math.floor(counter / self.max_tweets_in_file) * self.max_tweets_in_file
            )


    def index_terms_and_docs(self):
        """
        :return:
        """
        file_name = "data/terms_pointers/term_docs_{}.txt"
        for counter, term_docs in enumerate(self.parser_dictionary.items()):
            temp_file_name = file_name.format(math.floor(counter / self.max_terms_in_file))
            term = term_docs[0]
            docs = term_docs[1]

            # append line to file
            temp_docs_locaions = [(doc, self.docs_locations[doc]) for doc in docs]

            with io.open(temp_file_name, "a", encoding="utf-8") as f:
                f.write(f"{(len(docs), temp_docs_locaions)},\n")
            f.close()

            self.indexer[term] = (
                temp_file_name,
                counter - math.floor(counter / self.max_terms_in_file) * self.max_terms_in_file
            )






    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        for term in document_dictionary.keys():
            try:
                # Update inverted index and posting
                if term not in self.inverted_idx.keys():
                    self.inverted_idx[term] = 1
                    self.postingDict[term] = []
                else:
                    self.inverted_idx[term] += 1

                self.postingDict[term].append((document.tweet_id, document_dictionary[term]))

            except:
                print('problem with the following key {}'.format(term[0]))