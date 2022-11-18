from diophila import OpenAlex
import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import arxiv

def get_connection(email = None):
    return OpenAlex(email)

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
        temp = oa.get_single_work(id, "doi")[result_type]

        cite_list = []
        sub_key_list = set(["title", "doi", "publication_date", "host_venue", "open_access", "authorships"])
        
        for i in temp:

            temp2 = oa.get_single_work(i, "openalex")
            temp2 = {k:v for (k,v) in temp2.items() if k in sub_key_list}

            temp2["issn"] = temp2["host_venue"]["issn"]
            temp2["location"] = temp2["host_venue"]["display_name"]
            temp2["publisher"] = temp2["host_venue"]["publisher"]
            del temp2["host_venue"]

            #extract oa_url from open_access and add it to the dict
            temp2["oa_url"] = temp2["open_access"]["oa_url"]
            del temp2["open_access"]

            #process authors
            temp2["authors"] = [i["author"]["display_name"] for i in temp2["authorships"]]
            #if there are more than 5 authors, only show the first 5 and add "et al."
            if len(temp2["authors"]) > 5:
                temp2["authors"] = temp2["authors"][:5] + ["et al."]
            del temp2["authorships"]

            cite_list.append(temp2)
        #make a dataframe with sub_key_list as columns
        cite_list = pd.DataFrame.from_records(cite_list)
        cite_list = cite_list[['title', 'publication_date', 'doi', 'authors', 'issn', 'location', 'publisher', 'oa_url']]

        return cite_list
    except:
        raise Exception("")   

def arxiv_to_doi(arxiv_id):
    #if the id is a link, extract the id
    if "arxiv.org" in arxiv_id:
        arxiv_id = arxiv_id.split("/")[-1]
    return next(arxiv.Search(id_list = [arxiv_id]).results()).doi
# def get_author_info(name, key = "Profile"):
#     if not name: return None
#     oa = get_connection('chinardankhara@gmail.com') #TODO: this will need parameterization
#     try:
#         oa.get_single_author(name)
#     except:
#         raise Exception("")
