import io
import time
import math
import pickle
from collections import defaultdict

class Indexer:

    def __init__(self, parser_dictionary, parser_tweets_words_locations):
        self.max_tweets_in_file = 100000
        self.max_terms_in_file = 50000
        self.parser_dictionary = parser_dictionary
        self.parser_tweets_words_locations = parser_tweets_words_locations
        self.docs_locations = dict()
        self.indexer = dict()
        #self.config = config

    def index_docs(self):
        """
        :return:
        """
        start = time.time()
        file_name = "data/docs/docs_data_{}.txt"
        batch_writing = ""
        for counter, tweet in enumerate(self.parser_tweets_words_locations.items()):
            temp_file_name = file_name.format(math.floor(counter / self.max_tweets_in_file))
            tweet_id = tweet[0]
            tweet_data = tweet[1]
            batch_writing = batch_writing+f"{(tweet_id, [(word, len(freq)) for word, freq in tweet_data.items()])}\n"

            if (counter%5000==0) | (counter % self.max_tweets_in_file == self.max_tweets_in_file-1):
                with io.open(temp_file_name, "a", encoding="utf-8") as f:
                    f.write(batch_writing)
                batch_writing = ""
                print("Done writing batch of docs")

            # replace tweet data to tweet location in the original dict
            self.docs_locations[tweet_id] = (
                temp_file_name,
                (counter - math.floor(counter / self.max_tweets_in_file) * self.max_tweets_in_file)+1
            )

        with io.open(temp_file_name, "a", encoding="utf-8") as f:
            f.write(batch_writing)
            print("writing last batch", counter, f"\nTime: {(time.time()-start)/60}")


    def index_terms_and_docs(self):
        """
        :return:
        """
        file_name = "data/terms_pointers/term_docs_{}.txt"
        files_batches = {
            'counters': defaultdict(int),
            'pointers': defaultdict(str)
        }
        for counter, term_docs in enumerate(self.parser_dictionary.items()):
            temp_file_name = file_name.format(math.floor(counter / self.max_terms_in_file))
            term = term_docs[0]
            docs = term_docs[1]

            # append line to file
            temp_docs_locaions = [(doc, self.docs_locations[doc]) for doc in docs]
            files_batches['counters'][temp_file_name] += 1
            #print('Counter for', temp_file_name, files_batches['counters'][temp_file_name])
            files_batches['pointers'][temp_file_name] += f"{(len(docs), temp_docs_locaions)}\n"

            # batch writing to a file
            if files_batches['counters'][temp_file_name] % 500 == 0:
                with io.open(temp_file_name, "a", encoding="utf-8") as f:
                    f.write(files_batches['pointers'][temp_file_name])
                files_batches['pointers'][temp_file_name] = ""
                print(f'Batch of terms to pointers as been done {temp_file_name}')

            self.indexer[term] = (
                temp_file_name,
                (counter - math.floor(counter / self.max_terms_in_file) * self.max_terms_in_file)+1
            )

        # write all remainings
        for temp_file_name, remain_content in files_batches['pointers'].items():
            if len(remain_content)>0:
                with io.open(temp_file_name, "a", encoding="utf-8") as f:
                    f.write(remain_content)
                print(f"last batch {temp_file_name}")


    def indexing(self):
        """

        :return:
        """
        # indexing docs
        self.index_docs()
        del self.parser_tweets_words_locations

        # indexing terms
        self.index_terms_and_docs()
        del self.docs_locations

        # save dictionary as pickle
        with open('dictionary.pickle', 'wb') as handle:
            pickle.dump(self.indexer, handle, protocol=pickle.HIGHEST_PROTOCOL)
