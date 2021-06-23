import urllib.request
from bs4 import BeautifulSoup
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import re
from xlwt import Workbook


def get_crawl_url(max_loops, urls_to_be_fetched ):

    url_first = 'Website URL' #Replace with a news website URL
    url_core = 'Website core url URL' #Replace with a news website core URL


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
                if link is not None and link.startswith(url_first):
                    if link not in urls_already_checked:
                        urls_to_be_checked.add(link)
                    urls.add(link)
                    print(link)
                elif link is not None and link.startswith('/'):
                    link = url_first + link
                    if link not in urls_already_checked:
                        urls_to_be_checked.add(link)
                    urls.add(link)
                    print(link)

        except Exception as e:
            print("error")
            print(e)

        print(len(urls))
    return urls


def crawl_html(urls):
    count = 0
    wb = Workbook()
    sheet1 = wb.add_sheet('Sheet 1')

    for url in urls:
        print(count)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req).read().decode("utf-8")
            fact_claim = re.findall(r'Claim Review : &nbsp; </span><span class="value">(.+?)</span></div>', html)
            fact_check = re.findall(r'Fact Check : &nbsp;</span><span class="value">(.+?)</span></div>', html)
            if len(fact_claim) == 1 and len(fact_check) == 1:
                count = count + 1
                sheet1.write(count, 0, fact_claim[0])
                sheet1.write(count, 1, fact_check[0])
        except Exception as e:
            print(e)
            print("error")
    wb.save('Fake_news.xls')

if __name__ == "__main__":
    urls = get_crawl_url(2000, 5000)
    crawl_html(urls)


