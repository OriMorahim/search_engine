from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document


class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english')

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        text_tokens = word_tokenize(text)
        text_tokens_without_stopwords = [w.lower() for w in text_tokens if w not in self.stop_words]
        return text_tokens_without_stopwords

    def parse_doc(self, doc_as_named_tuple):
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
        tokenized_text = self.parse_sentence(full_text)

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

        return documnets


