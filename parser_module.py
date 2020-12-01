import re
import time
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from collections import Counter, defaultdict


class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english')
        self.dictionary = defaultdict(set)
        self.tweets_words_locations = dict()
        self.capitals_counter = Counter()
        self.words_dual_representation = []
        self.words_capital_representation = []
        self.seen_capital = set()

    def parse_sentence(self, text, do_stem: bool):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        text_tokens = self.percentage_tokenizer(text)  # parse percent
        if "percent" in text_tokens or "percentage" in text_tokens:
            text_tokens = self.number_tokenizer(text_tokens)  # parse numbers
        ans = ""
        string = ""
        for w in text_tokens.split():
            ans = self.remove_single_chars(w)
            if "http" in w or "https" in w or "www" in w:
                ans = self.url_tokenizer(ans)
            elif "-" in ans or "/" in ans or "&" in ans:
                ans = self.hyphen_fixer(ans)
            elif "#" in ans or "_" in ans:  # parse hashtags
                ans = self.hash_tag_tokenizer(ans)


            string = string + " " + ans

        text_tokens = word_tokenize(string)  # tokenization

        # if stemming is necessary
        if do_stem:
            text_tokens = self.stemmer(text_tokens)
           # print("after stemming:", text_tokens)

        text_tokens_without_stopwords = []#[w for w in text_tokens if w.lower() not in self.stop_words]
        for w in text_tokens:
            if w not in self.stop_words:
                text_tokens_without_stopwords.append(w)
                if w[0].isupper():
                    self.seen_capital.add(w)

        self.capitals_counter.update(text_tokens_without_stopwords)

        return text_tokens_without_stopwords


    def parse_doc(self, doc_as_named_tuple, do_stem: bool = False):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_named_tuple.tweet_id
        full_text = doc_as_named_tuple.full_text
        tokenized_text = self.parse_sentence(full_text, do_stem)

        # the following dict will hold the words locations for a specific tweet
        tweet_words_locations = defaultdict(list)

        # add words to dict
        for location, term in enumerate(tokenized_text):
                self.dictionary[term].add(tweet_id)
                tweet_words_locations[term].append(location)

        # keep tweet words locations
        self.tweets_words_locations[tweet_id] = tweet_words_locations


    def parse_batch_of_docs(self, df: pd.DataFrame):
        """

        :param df:
        :return:
        """
        # parse each tweet and insert result to a document
        for row in df.itertuples():
            self.parse_doc(row)



    def parse_corpus(self, dfs: list):
        """
        :param df:
        :return:
        """
        while dfs:
            df = dfs.pop()
            print(f"batch size to parse: {df.shape[0]} {time.ctime()}")
            self.parse_batch_of_docs(df)
            print(f'finish parse batch {time.ctime()}')

        # fetch words with capital letter
        #all_words = set(self.capitals_counter.keys()) # Avoid
        #uppers_as_lowers = set([word for word in all_words if word[0].isupper()]) # can be avoided
        self.words_dual_representation = set([word for word in self.seen_capital if word.lower() in self.capitals_counter.keys()])
        self.words_capital_representation = self.seen_capital-self.words_dual_representation

        # for each word that appear only with capital change the word to be all capital
        for upper_as_lower in self.seen_capital:
            if upper_as_lower in self.words_capital_representation:
                self.capitals_counter[upper_as_lower.upper()] = self.capitals_counter.pop(upper_as_lower)
            # if the word appear as capital and lower convert the capital to lower and fix Counter
            else:
                self.capitals_counter[upper_as_lower.lower()] = self.capitals_counter[upper_as_lower.lower()] + \
                                                        self.capitals_counter.pop(upper_as_lower)

        # change words to all capital
        for capital in self.words_capital_representation: # list of words need to be change appearnce to capital
            for tweet in self.dictionary[capital]: # set of tweets contain the capital
                self.tweets_words_locations[tweet][capital.upper()].extend(self.tweets_words_locations[tweet].pop(capital))
            self.dictionary[capital.upper()] = self.dictionary.pop(capital)

        # change words to all lower
        for capital in self.words_dual_representation:
            for tweet in self.dictionary[capital]:
                self.tweets_words_locations[tweet][capital.lower()].extend(self.tweets_words_locations[tweet].pop(capital))
            self.dictionary[capital.lower()].union(self.dictionary.pop(capital))


    def hash_tag_tokenizer(self, word: str) -> str:
        string = ""

        # if word == "RT":
        #     continue
        string = word
        word = word[1:]
        if "_" in word:
            split_by_underscore = " ".join(word.split("_"))
            string = string + " " + split_by_underscore
            return string
        else:
            split_by_caps = " ".join([a for a in re.split('([A-Z][a-z]+)', word) if a])
            string = string + " " + split_by_caps
            return string

        return word


    def url_tokenizer(self, w: str) -> str:
        string = ""
        url = []
        # if len(w) < 2:
        #     continue
        url = (re.split(r"\W+", w))
        url_to_string = ' '.join(url)
        string = url_to_string

        return string


    def stemmer(self, tokens: str) -> str:
        ps = PorterStemmer()
        string = ""
        for word in tokens.split():
            string = string + ps.stem(word) + " "

        return string


    def percentage_tokenizer(self, tokens: str) -> str:
        string = ""
        ans = False
        for w in tokens.split():
            if w == "RT":
                continue
            if ans:
                if w == "percent" or w == "percentage":
                    string = string + "%" + " "
                    ans = False
                    continue
                else:
                    string = string + " "
            try:
                if float(w):
                    string = string + w
                    ans = True
                    continue
            except ValueError:
                string = string + w + " "

        return string


    def number_tokenizer(self, tokens: str) -> str:
        string = ""
        kmb = ""
        number = False
        for w in tokens.split():
            if number:
                if w == "Thousand":
                    kmb = kmb + "K"
                    if kmb == "KK":
                        string = string[:-1] + "M"
                        kmb = ""
                        continue
                    elif kmb == "MK" or kmb == "KM":
                        string = string[:-1] + "B"
                        kmb = ""
                        continue
                    else:
                        string = string + "K"
                        continue
                elif w == "Million":
                    kmb = kmb + "M"
                    if kmb == "MK" or kmb == "KM":
                        string = string[:-1] + "B"
                        kmb = ""
                        continue
                    else:
                        string = string + "M"
                        continue
                elif w == "Billion":
                    string = string + "B"
                    continue
                else:
                    string = string + " "
                    number = False
            kmb = ""
            try:
                if float(w):
                    num = float(w)
                    if num < 1000:
                        number = True
                        string = string + w
                        continue
                    elif num < 1000000:
                        num = num / 1000
                        num = round(num, 3)
                        num = str(num)
                        if num.endswith(".0"):
                            num = num.replace(".0", "")
                        string = string + num + "K"
                        kmb = kmb + "K"
                        number = True
                        continue
                    elif num < 1000000000.00:
                        num = num / 1000000
                        num = round(num, 3)
                        num = str(num)
                        if num.endswith(".0"):
                            num = num.replace(".0", "")
                        string = string + num + "M"
                        kmb = kmb + "M"
                        number = True
                        continue
                    elif num >= 1000000000:
                        num = num / 1000000000.000
                        num = round(num, 3)
                        num = str(num)
                        if num.endswith(".0"):
                            num = num.replace(".0", "")
                        string = string + num + "B"
                        number = True
                        continue
            except:
                string = string + w + " "

        return string


    def remove_single_chars(self, w: str) -> str:
        string = ""
        w = w.replace("!", "").replace("?", "").replace(":", "").replace("’", "").replace("…", "").replace(";", "")
        w = w.replace('"', '').replace("”", "").replace("'", "").replace("*", "").replace("😂", "").replace("“", "")
        w = w.replace("❤", "").replace("😭", "").replace(",", "")
        if "." in w:
            try:
                if float(w):
                    []
            except:
                w = w.replace(".", "")
        if len(w) > 1 or w.isdigit():
            string = w

        return string


    def hyphen_fixer(self, w: str) -> str:
        string = ""

        if "-" in w:
            # dual_string = w
            string = " ".join(w.split("-")) + " "
        elif "/" in w:
            # dual_string = w
            string = " ".join(w.split("/")) + " "
        elif "&" in w:
            # dual_string = w
            string = " ".join(w.split("&")) + " "
        else:
            string = w
        return string

# from parser_module import Parse
# parse_ = Parse()
# from reader import ReadFile
# reader_ = ReadFile('C:/Users/orimo/Documents/study_bgu/information_retrival/Data')
# df = reader_.read_and_concat_all_parquet_in_dir_of_dirs(1)
# parse_.parse_corpus(df.head(200))
# from indexer import *
# ind = Indexer(parse_.dictionary, parse_.tweets_words_locations)
# ind.index_docs()

# import searcher
# search = searcher.Searcher()
# docs, idfs = search.relevant_docs_from_posting(['covid'])
# import ranker
# rank = ranker.Ranker()
# rank.tf_idf(docs, idfs, ['covid', 'never'])

