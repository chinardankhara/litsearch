from diophila import OpenAlex
import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import arxiv
import requests
import json 

def get_connection(email = None):
    return OpenAlex(email)

def convert_to_display_format(record):
        sub_key_list = set(["title", "doi", "publication_date", "host_venue", "open_access", "authorships"])
        record = {k:v for (k,v) in record.items() if k in sub_key_list}

        record["issn"] = record["host_venue"]["issn"]
        record["location"] = record["host_venue"]["display_name"]
        record["publisher"] = record["host_venue"]["publisher"]
        del record["host_venue"]

        #extract oa_url from open_access and add it to the dict
        record["oa_url"] = record["open_access"]["oa_url"]
        del record["open_access"]

        #process authors
        record["authors"] = [i["author"]["display_name"] for i in record["authorships"]]
        #if there are more than 5 authors, only show the first 5 and add "et al."
        if len(record["authors"]) > 5:
            record["authors"] = record["authors"][:5] + ["et al."]
        del record["authorships"]
    
        return record

def get_results_from_id(id = None, result_type = "referenced_works", id_type = None):
    if not id: return None

    

    try:
        #handling the arxiv case
        if id_type == "Arxiv":
            id = arxiv_to_doi(id)

        #getting openalex connection
        oa = get_connection('chinardankhara@gmail.com') #TODO: this will need parameterization

        #replace Refereced Works with referenced_works and Related Works with related_works
        result_type = result_type.replace(" ", "_").lower()
        original_result = oa.get_single_work(id, "doi")
        id_list = original_result[result_type]

        original_result = pd.DataFrame.from_records([convert_to_display_format(original_result)])
        original_result = original_result[['title', 'publication_date', 'doi', 'authors', 'issn', 'location', 'publisher', 'oa_url']]
        rel_list = []
        for i in id_list:
            temp = convert_to_display_format(oa.get_single_work(i, "openalex"))
            rel_list.append(temp)
        
        del oa
        rel_list = pd.DataFrame.from_records(rel_list)
        rel_list = rel_list[['title', 'publication_date', 'doi', 'authors', 'issn', 'location', 'publisher', 'oa_url']]
        
        return original_result, rel_list
    except:
        raise Exception("")   

def get_recommended_results(search_text, exact_match = False):
    if not search_text: return None
    #replace spaces with %20
    search_text = search_text.replace(" ", "%20")
    if exact_match:
        #enclose the search text in %22
        search_text = "%22" + search_text + "%22"
    
    response = json.loads(requests.get('https://api.openalex.org/works?search=' + search_text,
     params = {'mailto': 'chinardankhara@gmail.com'}).text)['results']
    response = pd.DataFrame.from_records([convert_to_display_format(i) for i in response])
    response = response[['title', 'publication_date', 'doi', 'authors', 'issn', 'location', 'publisher', 'oa_url']]
    return response

def arxiv_to_doi(arxiv_id):
    #if the id is a link, extract the id
    if "arxiv.org" in arxiv_id:
        arxiv_id = arxiv_id.split("/")[-1]
    return next(arxiv.Search(id_list = [arxiv_id]).results()).doi
