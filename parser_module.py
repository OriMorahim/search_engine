import re
from document import Document
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

    def parse_sentence(self, text, do_stem: bool):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        text_tokens = self.remove_single_chars(text)                 # parse non relevant chars
        text_tokens = self.hyphen_fixer(text_tokens)                 # parse by hyphen "-","/","&"
        hashtag_tokenize = self.hash_tag_tokenizer(text_tokens)      # parse hashtags
        text_tokens = self.number_tokenizer(text_tokens)             # parse numbers
        url_tokenize = self.url_tokenizer(hashtag_tokenize)          # parse url
        text_tokens = word_tokenize(url_tokenize)                    # tokenization

        # if stemming is necessary
        if do_stem:
            text_tokens = self.stemmer(text_tokens)
           # print("after stemming:", text_tokens)

        text_tokens_without_stopwords = [w for w in text_tokens if w.lower() not in self.stop_words]

        self.capitals_counter.update(text_tokens_without_stopwords)

        return text_tokens_without_stopwords


    def parse_doc(self, doc_as_named_tuple, do_stem: bool = False):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_named_tuple.tweet_id
        tweet_date = doc_as_named_tuple.tweet_date #
        full_text = doc_as_named_tuple.full_text
        url = doc_as_named_tuple.urls #
        retweet_text = doc_as_named_tuple.retweet_text #
        retweet_url = doc_as_named_tuple.retweet_urls #
        quote_text = doc_as_named_tuple.quoted_text #
        #quote_url = doc_as_named_tuple.quote_urls #
        tokenized_text = self.parse_sentence(full_text, do_stem)
        #term_dict = Counter(tokenized_text)
        #doc_length = len(tokenized_text)  # after text operations.

        # the following dict will hold the words locations for a specific tweet
        tweet_words_locations = defaultdict(list)

        # add words to dict
        for location, term in enumerate(tokenized_text):
                self.dictionary[term].add(tweet_id)
                tweet_words_locations[term].append(location)

        # keep tweet words locations
        self.tweets_words_locations[tweet_id] = tweet_words_locations


    def parse_corpus(self, df):
        """
        :param df:
        :return:
        """
        # parse each tweet and insert result to a document
#        documnets = []
        for row in df.itertuples():
            document = self.parse_doc(row)
            #documnets.append(document)

        # fetch words with capital letter
        all_words = set(self.capitals_counter.keys())
        uppers_as_lowers = set([word for word in all_words if word[0].isupper()])
        self.words_dual_representation = set([word for word in uppers_as_lowers if word.lower() in all_words])
        self.words_capital_representation = uppers_as_lowers-self.words_dual_representation

        # for each word that appear only with capital change the word to be all capital
        for upper_as_lower in uppers_as_lowers:
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


    def hash_tag_tokenizer(self, tokens: str) -> str:
        string = ""
        for word in tokens.split():
            if word == "RT":
                continue
            if word.startswith("#"):
                word = word[1:]
                if "_" in word:
                    split_by_underscore = " ".join(word.split("_"))
                    string = string + split_by_underscore + " "
                else:
                    split_by_caps = " ".join([a for a in re.split('([A-Z][a-z]+)', word) if a])
                    string = string + split_by_caps + " "
                word = "".join(word.split("_"))
                string = string + "#" + word + " "
            else:
                string = string + word + " "
        return string

    def url_tokenizer(self, tokens: str) -> str:
        string = ""
        url = []
        for w in tokens.split():
            if len(w) < 2:
                continue
            if bool(re.search("http|https|www", w)):
                url = (re.split(r"\W+", w))
                url_to_string = ' '.join(url)
                string = string + url_to_string + " "
            else:
                string = string + w + " "
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

    def remove_single_chars(self, tokens: str) -> str:
        string = ""
        for w in tokens.split():
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
                string = string + w + " "

        return string

    def hyphen_fixer(self, tokens: str) -> str:
        string = ""
        dual_string = ""
        period = ""
        for w in tokens.split():
            if "-" in w:
                # dual_string = w
                string = string + " " + " ".join(w.split("-")) + " "
            elif "/" in w:
                # dual_string = w
                string = string + " " + " ".join(w.split("/")) + " "
            elif "&" in w:
                # dual_string = w
                string = string + " " + " ".join(w.split("&")) + " "
            else:
                string = string + w + " "
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