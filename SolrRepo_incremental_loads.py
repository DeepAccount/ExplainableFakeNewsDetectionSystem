import pysolr
import requests
import xml.etree.ElementTree as ET
from newsplease import NewsPlease
import nltk
#nltk.download('stopwords')
from rake_nltk import Rake
from nltk.corpus import stopwords


solr_url = '' #update solr url
news_url = '' #update news url
news_xpath = './channel/item'

solr = pysolr.Solr(solr_url, always_commit=True)

def load_data():
    id = 1

    resp = requests.get(news_url, verify=False)
    feed = resp.content
    root = ET.fromstring(feed)
    for item in root.findall('./channel/item'):
        for child in item:
            if child.tag == '{http://purl.org/rss/1.0/modules/content/}encoded':
                content = child.text.encode('utf8')
            elif child.tag == 'title':
                title = child.text.encode('utf8')
            elif child.tag == 'link':
                link = child.text.encode('utf8')
        print("content", content)
        print("title", title)
        print("link", link)
        solr.add([
            {
                "id": "doc" + str(id),
                "title": str(title, encoding='UTF-8'),
                "content": str(content, encoding='UTF-8'),
                "link": str(link, encoding='UTF-8')
            }])
        id = id + 1

def load_data(solr_url, news_url, news_xpath):

    id = 1

    resp = requests.get(news_url, verify=False)
    feed = resp.content
    root = ET.fromstring(feed)
    for item in root.findall(news_xpath):
        for child in item:
            if child.tag == 'title':
                title = child.text.encode('utf8')
            elif child.tag == 'link':
                link = child.text
                news = NewsPlease.from_url(link)
                content = news.maintext

        print("content", content)
        print("title", title)
        print("link", link)

        solr = pysolr.Solr(solr_url, always_commit=True)
        solr.add([
            {
                "id": "doc" + str(id),
                "title": str(title, encoding='UTF-8'),
                "content": content,
                "link": link
            }])
        id = id + 1


def search_words(word_list):

    first_word = word_list.pop()
    first_word = 'content:' + first_word

    filter_queries = []
    for word in word_list:
        filter_queries.append('content:' + word)

    results = solr.search(first_word, fq=filter_queries)
    print("Number of records found ", len(results))

    for result in results:
        print("The title is '{0}'.".format(result['title']))
        print("The link is '{0}'.".format(result['link']))


def search_rake(content, nb):

    nb = int(nb)
    r = Rake(stopwords=stopwords.words('english'), max_length=5)

    r.extract_keywords_from_text(content)
    print(r.get_ranked_phrases())

    word_list = r.get_ranked_phrases()[:nb]
    print(word_list)

    first_word = word_list.pop()
    first_word = 'content:' + first_word

    filter_queries = []
    for word in word_list:
        filter_queries.append('content:' + word)

    results = solr.search(first_word, fq=filter_queries)
    print("Number of records found ", len(results))

    for result in results:
        print("The title is '{0}'.".format(result['title']))
        print("The link is '{0}'.".format(result['link']))

    return results


if __name__ == "__main__":
    print('Main method')
    #load_data()
    #word_list = ['Hathras','Rahul']
    #search_words(word_list)

    solr_url = '' #update Solr URL
    news_url = '' #update News url
    news_xpath = './channel/item'
    load_data(solr_url, news_url, news_xpath)

    #search_rake()