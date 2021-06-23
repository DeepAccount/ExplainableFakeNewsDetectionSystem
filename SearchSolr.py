import NewsCrawler
import pysolr
from yake import KeywordExtractor
import itertools

solr_url = 'Solr URL' #Solr URL
solr = pysolr.Solr(solr_url, always_commit=True)

#candidate_count = 10

def remove_dups(input_list):
    input_list.sort()
    output_list = list(input_list for input_list, _ in itertools.groupby(input_list))
    return output_list


def get_candidates(input_text, candidate_count):

    index_len_5_count_10 = NewsCrawler.create_index_key(input_text, 5, 10)
    index_len_5_count_5 = NewsCrawler.create_index_key(input_text, 5, 5)
    index_len_5_count_3 = NewsCrawler.create_index_key(input_text, 5, 3)
    index_len_1_count_10 = NewsCrawler.create_index_key(input_text, 1, 10)
    index_len_1_count_8 = NewsCrawler.create_index_key(input_text, 1, 8)
    index_len_1_count_5 = NewsCrawler.create_index_key(input_text, 1, 5)

    index_len_5_count_10 = 'index_len_5_count_10:' + '"' + index_len_5_count_10 + '"'
    index_len_5_count_5 = 'index_len_5_count_5:' + '"' + index_len_5_count_5 + '"'
    index_len_5_count_3 = 'index_len_5_count_3:' + '"' + index_len_5_count_3 + '"'
    index_len_1_count_10 = 'index_len_1_count_10:' + '"' + index_len_1_count_10 + '"'
    index_len_1_count_8 = 'index_len_1_count_8:' + '"' + index_len_1_count_8 + '"'
    index_len_1_count_5 = 'index_len_1_count_5:' + '"' + index_len_1_count_5 + '"'

    candidates = []

    results = solr.search(index_len_5_count_10)
    for result in results:
        candidates.append([result['url'], result['content']])
    candidates = remove_dups(candidates)

    if len(candidates) < candidate_count:
        results = solr.search(index_len_5_count_5)
        for result in results:
            candidates.append([result['url'], result['content']])
        candidates = remove_dups(candidates)

    if len(candidates) < candidate_count:
        results = solr.search(index_len_5_count_3)
        for result in results:
            candidates.append([result['url'], result['content']])
        candidates = remove_dups(candidates)

    if len(candidates) < candidate_count:
        results = solr.search(index_len_1_count_10)
        for result in results:
            candidates.append([result['url'], result['content']])
        candidates = remove_dups(candidates)

    if len(candidates) < candidate_count:
        results = solr.search(index_len_1_count_8)
        for result in results:
            candidates.append([result['url'], result['content']])
        candidates = remove_dups(candidates)

    if len(candidates) < candidate_count:
        results = solr.search(index_len_1_count_5)
        for result in results:
            candidates.append([result['url'], result['content']])
        candidates = remove_dups(candidates)

    if len(candidates) < candidate_count:
        kw_extractor = KeywordExtractor(lan="en", n=50, top=50)
        keywords = kw_extractor.extract_keywords(text=input_text)
        keyword_list = []
        for keyword in keywords:
            keyword_list.append(keyword[1])

        first_word = keyword_list.pop()
        first_word = 'content:' + first_word

        filter_queries = []
        for word in keyword_list:
            filter_queries.append('content:' + word)

        results = solr.search(first_word, fq=filter_queries)
        #res_count = 0
        for result in results:
            candidates.append([result['url'], result['content']])
            #res_count = res_count + 1
            if len(remove_dups(candidates)) > candidate_count:
                break
        candidates = remove_dups(candidates)
        print(len(candidates))

    candidates = candidates[::-1]
    #ordered_candidates = candidates.reverse()
    for candidate in candidates:
        print(candidate[0])

    return candidates
