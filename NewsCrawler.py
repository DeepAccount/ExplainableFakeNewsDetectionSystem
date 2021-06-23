import urllib.request
from bs4 import BeautifulSoup
from newsplease import NewsPlease
from yake import KeywordExtractor
import pysolr
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

solr_url = 'Solr URL'  #Give a Solr URL
solr = pysolr.Solr(solr_url, always_commit=True)

def get_crawl_url(max_loops, urls_to_be_fetched ):
    url_first = 'news URL' #Url of news website to be crawled
    url_core = 'news core URL' # core Url of news website to be crawled

    urls_to_be_checked = set()
    urls_already_checked = set()
    urls = set()

    urls_to_be_checked.add(url_first)
    urls_to_be_checked.add(url_core)

    for i in range(max_loops):

        url_not_found = True
        while len(urls_to_be_checked) > 0 and url_not_found:
            url = urls_to_be_checked.pop()
            if url in urls_already_checked:
                url_not_found = True
            else:
                urls_already_checked.add(url)
                url_not_found = False

        if len(urls_to_be_checked) == 0 or len(urls) > urls_to_be_fetched:
            print('Done')
            break

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req).read()

            soup = BeautifulSoup(html, features="lxml")
            links = soup.find_all('a')

            for tag in links:
                link = tag.get('href',None)
                if link is not None and (link.startswith("/") or  link.startswith(url_core) ) and (not ( "/cdn-cgi/l/email-protection#" in link)):
                    if link not in urls_already_checked:
                        urls_to_be_checked.add(url_core + link)
                    urls.add(url_core + link)

        except Exception as e:
            print("error")
            print(e)

        print(len(urls))
    return urls

def crawl_persist_solr(urls):
    count = 0
    for url in urls:
        count = count + 1
        print(count)
        try:
            news = NewsPlease.from_url(url)
            content = news.maintext
            if len(content) > 50:
                index_len_5_count_10 = create_index_key(content, 5, 10)
                index_len_5_count_5 = create_index_key(content, 5, 5)
                index_len_5_count_3 = create_index_key(content, 5, 3)
                index_len_1_count_10 = create_index_key(content, 1, 10)
                index_len_1_count_8 = create_index_key(content, 1, 8)
                index_len_1_count_5 = create_index_key(content, 1, 5)

                solr.add([
                    {
                        "url": url,
                        "content": content,
                        "index_len_5_count_10": index_len_5_count_10,
                        "index_len_5_count_5": index_len_5_count_5,
                        "index_len_5_count_3": index_len_5_count_3,
                        "index_len_1_count_10": index_len_1_count_10,
                        "index_len_1_count_8": index_len_1_count_8,
                        "index_len_1_count_5": index_len_1_count_5
                    }])
        except:
            print("error")


def create_index_key(doc, keywords_length, keyword_count):
    kw_extractor = KeywordExtractor(lan="en", n=keywords_length, top=keyword_count)
    keywords = kw_extractor.extract_keywords(text=doc)
    keyword_list = []
    for keyword in keywords:
        keyword_list.append(keyword[1])
    sorted_keywords = sorted(keyword_list)

    key = ''
    combiner = '$$$$'
    for keyword in sorted_keywords:
        key = key + combiner + keyword

    return key

if __name__ == "__main__":
    urls = get_crawl_url(2000, 20000)
    crawl_persist_solr(urls)


