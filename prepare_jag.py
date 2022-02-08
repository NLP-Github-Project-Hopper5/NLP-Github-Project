import unicodedata
import re
import json
import nltk
from nltk.tokenize.toktok import ToktokTokenizer
from nltk.corpus import stopwords
import pandas as pd
from time import strftime

############# BASIC CLEAN ###################


def basic_clean(corpus):
    '''
    Basic text cleaning function  that  takes a corpus of text; lowercases everything; normalizes unicode characters; and replaces anything that is not a letter, number, whitespace or a single quote.
    '''
    lower_corpus = corpus.lower()
    normal_corpus = unicodedata.normalize('NFKD', lower_corpus)\
        .encode('ascii', 'ignore')\
        .decode('utf-8', 'ignore')
    basic_clean_corpus = re.sub(r"[^a-z0-9'\s]", '', normal_corpus)
    return(basic_clean_corpus)

##################### TOKEIZER ####################


def tokenize(string):
    tokenizer = nltk.tokenize.ToktokTokenizer()
    return(tokenizer.tokenize(string, return_str=True))

####################### STEM #####################


def stem(text):
    '''
    Uses NLTK Porter stemmer object to return stems of words
    '''
    ps = nltk.porter.PorterStemmer()
    stems = [ps.stem(word) for word in text.split()]
    stemmed_text = ' '.join(stems)
    return stemmed_text

################ LEMMATIZE ################


def lemmatize(text):
    wnl = nltk.stem.WordNetLemmatizer()
    lemmas = [wnl.lemmatize(word) for word in text.split()]
    lemmatized_text = ' '.join(lemmas)
    return(lemmatized_text)

################ REMOVE STOPWORDS #################


def remove_stopwords(string, extra_words=[], exclude_words=[]):
    '''
    This function takes in a string, optional extra_words and exclude_words parameters
    with default empty lists and returns a string.
    '''
    # Create stopword_list.
    stopword_list = stopwords.words('english')

    # Remove 'exclude_words' from stopword_list to keep these in my text.
    stopword_list = set(stopword_list) - set(exclude_words)

    # Add in 'extra_words' to stopword_list.
    stopword_list = stopword_list.union(set(extra_words))

    # Split words in string.
    words = string.split()

    # Create a list of words from my string with stopwords removed and assign to variable.
    filtered_words = [word for word in words if word not in stopword_list]

    # Join words in the list back into strings and assign to a variable.
    string_without_stopwords = ' '.join(filtered_words)

    return string_without_stopwords

############### Column Lambdas###############


def categorise(row):
    if row['language'] == 'Swift':
        return 'swift'
    elif row['language'] == 'Python':
        return 'python'
    elif row['language'] == ('C++' or 'C'):
        return 'c'
    return 'other'

############### PREPARE ARTICLES ############


def prep_article_data(df, column, extra_words=[], exclude_words=[]):
    '''
    This function take in a df, the name for a text column with the option to pass lists for extra_words and exclude_words and returns a df with the text article title, original text, stemmed text,lemmatized text, cleaned, tokenized, & lemmatized text with stopwords removed.
    '''
    df['clean'] = df[column].apply(basic_clean)\
                            .apply(tokenize)\
                            .apply(remove_stopwords,
                                   extra_words=extra_words,
                                   exclude_words=exclude_words)

    df['stemmed'] = df[column].apply(basic_clean)\
        .apply(tokenize)\
        .apply(stem)\
        .apply(remove_stopwords,
               extra_words=extra_words,
               exclude_words=exclude_words)

    df['lemmatized'] = df[column].apply(basic_clean)\
        .apply(tokenize)\
        .apply(lemmatize)\
        .apply(remove_stopwords,
               extra_words=extra_words,
               exclude_words=exclude_words)
    # Add categoy column
    df['target'] = df.apply(lambda row: categorise(row), axis=1)

    return df[['repo', 'language', column, 'clean', 'stemmed', 'lemmatized']]
