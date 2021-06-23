from scipy import spatial
from sent2vec.vectorizer import Vectorizer
from nltk.tokenize import sent_tokenize
import math
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import spacy
import numpy as np
# Load the spacy model that you have installed
nlp = spacy.load('en_core_web_md')
from fastdist import fastdist
import time

def compare_doc_similarity(test_doc, archived_news_doc, sent_level_similariry_threshold, min_similar_sent_matched):

    #print(archived_news_doc[0])
    #start = time.time()
    orignal_test_doc = sent_tokenize(test_doc)
    orignal_archived_news_doc = sent_tokenize(archived_news_doc[1][0])

    test_doc_sent = sent_tokenize(test_doc)
    archived_news_doc_sent = sent_tokenize(archived_news_doc[1][0])

    test_doc_sent_normalised = []
    archived_news_doc_sent_normalised = []
    for doc in test_doc_sent:
        sent = normalise_sent(doc)
        test_doc_sent_normalised.append(sent)

    for doc in archived_news_doc_sent:
        sent = normalise_sent(doc)
        archived_news_doc_sent_normalised.append(sent)

    #print("Time Consumed in Preparation")
    #print("% s seconds" % (time.time() - start))


    #similar_sent = 0
    #nb_sent_test_doc = len(test_doc_sent)
    #min_similar_sent_matched = math.ceil(nb_sent_test_doc * len(sentence_similarity_percentage)/100)
    print("min_similar_sent_matched ",min_similar_sent_matched)

    sent_count = -1
    doc_matrix = []
    match_sent_vect = []
    min_score_vect = []
    for sent in test_doc_sent_normalised:
        sent_count = sent_count + 1
        archived_news_sent_count = -1

        doc1 = nlp(sent)
        test_doc_embedding = doc1.vector
        sent_vector = []
        for archived_news_sent in archived_news_doc_sent_normalised:
            archived_news_sent_count = archived_news_sent_count + 1

            doc2 = nlp(archived_news_sent)
            archived_news_embedding = doc2.vector

            cosine_distance = spatial.distance.cosine(test_doc_embedding, archived_news_embedding)
            sent_vector.append(cosine_distance)

        sent_vector_np = np.array(sent_vector)
        min_score = np.nanmin(sent_vector_np)
        index = np.where(sent_vector == min_score)
        #print(index)
        #print(index[0])
        #print(index[0][0])
        match_sent_val = archived_news_doc_sent[index[0][0]]
        match_sent_vect.append(match_sent_val)
        min_score_vect.append(min_score)



    #print("---------------------------")
    #doc_matrix_np = np.array(doc_matrix)
    #min_score = np.nanmin(doc_matrix_np)
    #print(doc_matrix_np)
    #print(min_score)
    #index = np.where(doc_matrix_np == min_score)
    #match_sent = archived_news_doc_sent[index[1][0]]

    nb_match_sent = 0
    for score in min_score_vect:
        if score <= sent_level_similariry_threshold:
            nb_match_sent = nb_match_sent + 1

    if nb_match_sent >= min_similar_sent_matched :
        return "MATCH", min_score_vect, match_sent_vect
    else:
        return "MISMATCH", min_score_vect, match_sent_vect


def normalise_sent(input):
    #remove extra lines
    sents = sent_tokenize(input)
    input = ''
    for sent in sents:
        input = input + ' ' + sent


    input = input.lower()

    pattern = re.compile(r'\b(' + r'|'.join(stopwords.words('english')) + r')\b\s*')
    without_stopwords = pattern.sub('', input)

    without_special_char = re.sub('[^A-Za-z0-9]+', ' ', without_stopwords)

    stemmer = PorterStemmer()
    stemmed_sent = ''
    words_to_stem = word_tokenize(without_special_char)
    for w in words_to_stem:
        stemmed_sent = stemmed_sent + " " + stemmer.stem(w)

    '''
    text_tokens = word_tokenize(input)
    word_list = [word for word in text_tokens if not word in stopwords.words()]
    without_stopwords = ''
    for w in word_list:
        without_stopwords = without_stopwords + " " + w

    without_special_char = re.sub('[^A-Za-z0-9]+', ' ', without_stopwords)

    stemmer = PorterStemmer()
    stemmed_sent = ''
    words_to_stem = word_tokenize(without_special_char)
    for w in words_to_stem:
        stemmed_sent = stemmed_sent + " " + stemmer.stem(w)
    '''
    return stemmed_sent.strip()

def get_min_similar_sent_matched(test_doc, sentence_similarity_percentage):
    test_doc_sent = sent_tokenize(test_doc)

    nb_sent_test_doc = len(test_doc_sent)
    min_similar_sent_matched = math.ceil(nb_sent_test_doc * int(sentence_similarity_percentage) / 100)
    return min_similar_sent_matched, test_doc_sent

def get_best_document(candidate_details, min_similar_sent_matched):
    min_score = min_similar_sent_matched
    best_document = candidate_details[0][0]
    for candidate in candidate_details:
        print(candidate[0])
        sorted_list = sorted(candidate[1])
        total_distance_sum = sum(sorted_list[0:min_similar_sent_matched])
        print(sorted_list[0:min_similar_sent_matched])
        print(total_distance_sum)
        if total_distance_sum < min_score:
            min_score = total_distance_sum
            best_document = candidate[0]
    return best_document




