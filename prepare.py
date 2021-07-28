import unicodedata
import re
import json

import nltk
from nltk.tokenize.toktok import ToktokTokenizer
from nltk.corpus import stopwords
from requests import get
from bs4 import BeautifulSoup


import pandas as pd



def basic_clean(string_value):
    #lowercase all letters in the text

    article = original.lower()

    # Normalizaton: Remove inconsistencies in unicode charater encoding.
    # encode the strings into ASCII byte-strings (ignore non-ASCII characters)
    # decode the byte-string back into a string

    unicodedata.normalize('NFKD', article)\
    .encode('ascii', 'ignore')\
    .decode('utf-8')
    # remove anything that is not a through z, a number, a single quote, or whitespace
    article = re.sub(r"[^a-z0-9\s]", '', article)
    
    return article



def tokenize(article):
    # Create the tokenizer
    tokenizer = nltk.tokenize.ToktokTokenizer()

    # Use the tokenizer
    article = tokenizer.tokenize(article, return_str= True)
    return article



def stem(article):
    # Create porter stemmer.
    ps = nltk.porter.PorterStemmer()
    # Check stemmer. It works.
    ps.stem('Calling')
    # Apply the stemmer to each word in our string.
    stems =[ps.stem(word) for word in article.split()]
    # Join our lists of words into a string again; assign to a variable to save changes
    article_stemmed = ' '.join(stems)
    return article_stemmed



def lemmatize(article):
    # Create the Lemmatizer.
    wnl = nltk.stem.WordNetLemmatizer()
    # Use the lemmatizer on each word in the list of words we created by using split.
    lemmas = [wnl.lemmatize(word) for word in article.split()]
    # Join our list of words into a string again; assign to a variable to save changes.
    article_lemmatized = ' '.join(lemmas)
    return article_lemmatized



def remove_stopwords(article_lemmatized, extra_words= [], exclude_words=[]):
    # standard English language stopwords list from nltk
    stopword_list = stopwords.words('english')
    # remove 'exlude_words' from stopword_list to keep these
    stopword_list= set(stopword_list) - set(exclude_words)
    #Add in 'extra_words' to stopword_list
    stopword_list= stopword_list.union(set(extra_words))
    #split words
    words= article_lemmatized.split()
    # Create a list of words from my string with stopwords removed and assign to variable.
    filtered_words = [word for word in words if word not in stopword_list]
    # Join words in the list back into strings; assign to a variable to keep changes.
    article_without_stopwords = ' '.join(filtered_words)
    return article_without_stopwords


def get_article(article, category):
    # Attribute selector
    title = article.select("[itemprop='headline']")[0].text
    
    # article body
    content = article.select("[itemprop='articleBody']")[0].text
    
    output = {}
    output["title"] = title
    output["content"] = content
    output["category"] = category
    
    return output



def get_articles(category, base ="https://inshorts.com/en/read/"):
    """
    This function takes in a category as a string. Category must be an available category in inshorts
    Returns a list of dictionaries where each dictionary represents a single inshort article
    """
    
    # We concatenate our base_url with the category
    url = base + category
    
    # Set the headers
    headers = {"User-Agent": "Mozilla/4.5 (compatible; HTTrack 3.0x; Windows 98)"}

    # Get the http response object from the server
    response = get(url, headers=headers)

    # Make soup out of the raw html
    soup = BeautifulSoup(response.text)
    
    # Ignore everything, focusing only on the news cards
    articles = soup.select(".news-card")
    
    output = []
    
    # Iterate through every article tag/soup 
    for article in articles:
        
        # Returns a dictionary of the article's title, body, and category
        article_data = get_article(article, category) 
        
        # Append the dictionary to the list
        output.append(article_data)
    
    # Return the list of dictionaries
    return output



def get_all_news_articles(categories):
    """
    Takes in a list of categories where the category is part of the URL pattern on inshorts
    Returns a dataframe of every article from every category listed
    Each row in the dataframe is a single article
    """
    all_inshorts = []

    for category in categories:
        all_category_articles = get_articles(category)
        all_inshorts = all_inshorts + all_category_articles

    df = pd.DataFrame(all_inshorts)
    return df



def get_codeup_blog(url):
    
    # Set the headers to show as Netscape Navigator on Windows 98, b/c I feel like creating an anomaly in the logs
    headers = {"User-Agent": "Mozilla/4.5 (compatible; HTTrack 3.0x; Windows 98)"}

    # Get the http response object from the server
    response = get(url, headers=headers)
    
    soup = BeautifulSoup(response.text)
    
    title = soup.find("h1").text
    published_date = soup.time.text
    
    if len(soup.select(".jupiterx-post-image")) > 0:
        blog_image = soup.select(".jupiterx-post-image")[0].picture.img["data-src"]
    else:
        blog_image = None
        
    content = soup.select(".jupiterx-post-content")[0].text
    
    output = {}
    output["title"] = title
    output["published_date"] = published_date
    output["blog_image"] = blog_image
    output["content"] = content
    
    return output



def get_blog_articles(urls):
    # List of dictionaries
    posts = [get_codeup_blog(url) for url in urls]
    
    return pd.DataFrame(posts)



def dataframes(df): 
    df.rename(columns={'content': 'original'}, inplace=True)
    df['clean']= df['original'].apply(basic_clean)
    df['clean']= df['original'].apply(tokenize)
    df['stemmed']= df['original'].apply(stem)
    df['lemmatized']= df['original'].apply(lemmatize)
    return df