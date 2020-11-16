import re
from document import Document
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize


WORDS_COUNTER = Counter()

class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english')

    def parse_sentence(self, text, do_stem: bool):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        hashtag_tokenize = self.hash_tag_tokenizer(text)             # parse hashtags
        url_tokenize = self.url_tokenizer(hashtag_tokenize)          # parse url
        text_tokens = word_tokenize(url_tokenize)                    # tokenization

        # if stemming is necessary
        if do_stem:
            text_tokens = self.stemmer(text_tokens)
            print("after stemming:", text_tokens)

        text_tokens_without_stopwords = [w for w in text_tokens if w.lower() not in self.stop_words]

        WORDS_COUNTER.update(text_tokens_without_stopwords)

        return text_tokens_without_stopwords

    def parse_doc(self, doc_as_named_tuple, do_stem: bool = True):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_named_tuple.tweet_id
        tweet_date = doc_as_named_tuple.tweet_date
        full_text = doc_as_named_tuple.full_text
        url = doc_as_named_tuple.urls
        retweet_text = doc_as_named_tuple.retweet_text
        retweet_url = doc_as_named_tuple.retweet_urls
        quote_text = doc_as_named_tuple.quoted_text
        quote_url = doc_as_named_tuple.quote_urls
        term_dict = {}
        tokenized_text = self.parse_sentence(full_text, do_stem)

        doc_length = len(tokenized_text)  # after text operations.

        for term in tokenized_text:
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)
        return document

    def parse_corpus(self, df):
        """

        :param df:
        :return:
        """
        documnets = []
        for row in df.itertuples():
            document = self.parse_doc(row)
            documnets.append(document)

        # fetch words with capital letter
        all_words = set(WORDS_COUNTER.keys())
        uppers_as_lowers = set([word for word in all_words if word[0].isupper()])
        words_appear_as_upper_and_lower = set([word for word in uppers_as_lowers if word.lower() in all_words])
        words_appear_as_upper_only = uppers_as_lowers-words_appear_as_upper_and_lower

        # for each word that appear only with capital change the word to be all capital
        for upper_as_lower in uppers_as_lowers:
            if upper_as_lower in words_appear_as_upper_only:
                WORDS_COUNTER[upper_as_lower.upper()] = WORDS_COUNTER.pop(upper_as_lower)
            # if the word appear as capital and lower convert the capital to lower and fix Counter
            else:
                WORDS_COUNTER[upper_as_lower.lower()] = WORDS_COUNTER[upper_as_lower.lower()] + \
                                                        WORDS_COUNTER.pop(upper_as_lower)

        return documnets

    def hash_tag_tokenizer(self, tokens: str)->str:
        string = ""
        for word in tokens.split():
            if word[0] == "#":
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
        return string #.lower()

    def url_tokenizer(self, tokens:str)->str:
       string = ""
       url = []
       for w in tokens.split():

           if bool(re.search("http|https|www", w)):
                url = (re.split(r"\W+", w))
                url_to_string = ' '.join(url)
                string = string + url_to_string + " "
           else:
               string = string + w + " "
       return string

    def stemmer(self, tokens: list)->list:

        ps = PorterStemmer()
        dfs = []
        for word in tokens:
                dfs.append(ps.stem(word))
        return dfs