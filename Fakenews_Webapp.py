from bottle import route, run, post, request, static_file
import SolrRepo
import DocumentComparison_matrix
import SearchSolr
import time
import numpy as np
import text_entailment

@route('/')
def server_static(filepath="index.html"):
    print("req came")
    return static_file(filepath, root='/home/deepk/FakeNews/src/public/')

@post('/doform')
def process():
    start = time.time()
    content = request.forms.content
    documents_count = request.forms.documents_count
    documents_count = int(documents_count)
    sentence_similarity_percentage = request.forms.sentence_similarity_percentage
    match_condition = request.forms.match_condition
    print("documents_count ", documents_count)
    print("sentence_similarity_percentage ", sentence_similarity_percentage)
    print("match_condition ", match_condition)
    candidates = SearchSolr.get_candidates(content, documents_count)
    print("Time Consumed in Solr search")
    print("% s seconds" % (time.time() - start))

    if len(candidates) == 0:
        response = "<center><h1> FAKE </br> <br> </h1></center>  </br> <br> **This document or similar document is not in our database, Please check with other Authentic sources"
        return response

    html_candidate_table = 'Matching Candidate Documents </br>'
    show_count = 1
    for candidate in candidates:
        html_candidate_table = html_candidate_table + str(show_count) + ') <a href = "' + candidate[0][0] + '">' + candidate[0][0]  + '</a> </br>'
        show_count = show_count + 1
    html_candidate_table = html_candidate_table + '</br>'

    min_similar_sent_matched, test_doc_sent = DocumentComparison_matrix.get_min_similar_sent_matched(content, sentence_similarity_percentage)

    count = 0
    start = time.time()
    candidate_details = []
    candidate_count = 0
    for candidate in candidates:
        candidate_count = candidate_count + 1
        response, min_score_vect, match_sent_vect = DocumentComparison_matrix.compare_doc_similarity(content, candidate, .01, min_similar_sent_matched)

        if response == "MATCH":
            response = "<center><h1> NOT FAKE </br> <br> </h1></center>"
            response = response + " Link to exact Matching news :  " + '<a href = "' + candidate[0][0] + '" >' + candidate[0][0] + '</a> </br> <br>'

            html_table = '</br><table border = "true"><tr><th>Matching Doc Seq No.</th><th>Test document sentence</th><th>Matched document sentence</th></tr>'
            loop_count = 0
            for sent in test_doc_sent:
                html_table = html_table + "<tr><td>" + str(candidate_count) + "</td>"
                html_table = html_table + "<td>" + sent + "</td>"
                html_table = html_table + "<td>" + match_sent_vect[loop_count] + "</td></tr>"
                loop_count = loop_count + 1
            html_table = html_table + "</table>"

            response = response + html_candidate_table + html_table
            return response

        print("+++++++++++++++++++++++++++++")
        print(candidate[0])
        print(match_sent_vect)
        print(min_score_vect)
        candidate_details.append([candidate[0][0], min_score_vect, match_sent_vect])

    if match_condition == 'nearest':
        best_document = DocumentComparison_matrix.get_best_document(candidate_details, min_similar_sent_matched)
        print(best_document)

        best_candidate = candidate_details[0]
        candidate_count = 0
        for candidate in candidate_details:
            if candidate[0] == best_document:
                best_candidate = candidate
                candidate_count = candidate_count + 1

        print(best_candidate[0])
        sent_count = 0
        non_fake_sent_count = 0
        match_list = []
        for sent in test_doc_sent:
            fake_result = text_entailment.fake_entailment(best_candidate[2][sent_count], sent)
            if fake_result == 'NOT FAKE ':
                non_fake_sent_count = non_fake_sent_count + 1
                match_list.append("MATCH")
            else:
                match_list.append("MIS-MATCH")
            sent_count = sent_count + 1
            print(fake_result)


        if non_fake_sent_count >= min_similar_sent_matched:
            response = "<center><h1> NOT FAKE </br> <br> </h1></center>"
        else:
            response = "<center><h1> FAKE </br> <br> </h1></center>"

        html_table = '</br><table border = "true"><tr><th>Matching Doc Seq No.</th><th>Test document sentence</th><th>Matched document sentence</th><th>MATCH/MIS-MATCH</th></tr>'
        loop_count = 0
        for sent in test_doc_sent:
            html_table = html_table + "<tr><td>" + str(candidate_count) + "</td>"
            html_table = html_table + "<td>" + sent + "</td>"
            html_table = html_table + "<td>" + best_candidate[2][loop_count] + "</td>"
            html_table = html_table + "<td>" + match_list[loop_count] + "</td></tr>"
            loop_count = loop_count + 1
        html_table = html_table + "</table>"

        response = response + html_candidate_table + html_table
        return response

    if match_condition == 'averaged':
        non_fake_count_list = []
        html_table = '</br><table border = "true"><tr><th>Matching Doc Seq No.</th><th>Test document sentence</th><th>Matched document sentence</th><th>MATCH/MIS-MATCH</th></tr>'
        candidate_count = 0
        weight = len(candidate_details)
        weight_sum = 0
        for candidate in candidate_details:
            candidate_count = candidate_count + 1
            sent_count = 0
            non_fake_sent_count = 0
            match_list = []
            for sent in test_doc_sent:
                fake_result = text_entailment.fake_entailment(sent, candidate[2][sent_count])
                if fake_result == 'NOT FAKE ':
                    non_fake_sent_count = non_fake_sent_count + 1
                    match_list.append("MATCH")
                else:
                    match_list.append("MIS-MATCH")
                sent_count = sent_count + 1
                print(fake_result)

            loop_count = 0
            for sent in test_doc_sent:
                html_table = html_table + "<tr><td>" + str(candidate_count) + "</td>"
                html_table = html_table + "<td>" + sent + "</td>"
                html_table = html_table + "<td>" + candidate[2][loop_count] + "</td>"
                html_table = html_table + "<td>" + match_list[loop_count] + "</td></tr>"
                loop_count = loop_count + 1

            if non_fake_sent_count >= min_similar_sent_matched:
                non_fake_count_list.append(weight)
            else:
                non_fake_count_list.append(0)
            weight_sum = weight_sum + weight
            weight = weight - 1

        html_table = html_table + "</table>"

        #if sum(non_fake_count_list) >= len(non_fake_count_list)/2:
        if sum(non_fake_count_list) >= weight_sum / 2:
            response = "<center><h1> NOT FAKE </br> <br> </h1></center>"
        else:
            response = "<center><h1> FAKE </br> <br> </h1></center>"

        response = response + html_candidate_table + html_table
        return response


    return html_candidate_table


    '''
        similarity_score_matrix_list.append(doc_matrix_np)

        html_table = '<table border = "true"><tr><th>Input Doc Sentence</th><th>Matched Sentence</th><th>Cosine Distance</th></tr>'
        for result in similariry_score_list:
            html_table = html_table + "<tr><td>" + result[0] + "</td>"
            html_table = html_table + "<td>" + result[1] + "</td>"
            html_table = html_table + "<td>" + result[2] + "</td></tr>"
        html_table = html_table + "</table>"
        count = count + 1

        if response == "MATCH":
            #response, similariry_score_list = DocumentComparsion.compare_doc_similarity(content, candidate[1], .01, 0.9, True)
            link = candidate[0][0]
            response = " NOT FAKE </br> <br>"
            response = response + " Link to Matching news :  " + '<a href = "' + link + '" >' + link + '</a> </br> <br>'
            print("Time Consumed in Matching")
            print("% s seconds" % (time.time() - start))
            return response + html_table

        #if response == "MISMATCH":
            #response, similariry_score_list = DocumentComparsion.compare_doc_similarity(content, candidate[1], .01, 0.9, True)
            #link = candidate[0][0]
            #response = " FAKE </br> <br>"
            #return response + html_table

    threshold = 0.01 * 1.25
    loop_count = 20
    for i in range(loop_count):
        can_count = 0
        for similarity_score_matrix in similarity_score_matrix_list:
            min_score = np.nanmin(similarity_score_matrix)
            if min_score <= threshold:
                link = candidates[can_count][0][0]
                response = " Link to Matching news :  " + '<a href = "' + link + '" >' + link + '</a> </br> <br>'
                fake_result = text_entailment.fake_entailment(match_sent,content)
                return fake_result + "Similar Doc Iteration count "+ str(i) + response
            can_count = can_count + 1
        threshold = threshold * 1.25

    '''
    print("Time Consumed in Matching")
    print("% s seconds" % (time.time() - start))
    return " Fake </br> <br> **This document or similar document is not in our database, Please check with other Authentic sources"

def process_rake():

    content = request.forms.get('content')
    number = request.forms.get('number')
    results = SolrRepo.search_rake(content, number)

    for result in results:
        text_content_solr = result['content']
        print(content)
        print(text_content_solr)
        print(type(content))
        print(type(text_content_solr))
        response = DocumentComparison_matrix.compare_doc_similarity(content, text_content_solr, .001, 1 )
        if response == "MATCH":
            return 'NON_FAKE'

    return 'FAKE'



def process_result_table():

    content = request.forms.get('content')
    number = request.forms.get('number')
    results = SolrRepo.search_rake(content, number)

    html_response = '<table border = "true"><tr><th>Title</th><th>Link</th></tr>'
    for result in results:
        html_response = html_response + "<tr><td>" + result['title'][0] + "</td>"
        link = '<a href = "' + result['link'][0] + '" >' + result['link'][0] + '</a>'
        html_response = html_response + "<td>" + link + "</td>"
    html_response = html_response + "</table>"
    return html_response

run(host='XXX.XXX.XX.XX', reloader=True, port=80, debug=True) #give the hostname of system to be used