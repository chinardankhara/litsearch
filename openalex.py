from diophila import OpenAlex
import streamlit as st
import pandas as pd
import arxiv
import requests
import json 

@st.experimental_singleton
def get_connection(email = None):
    """_This function returns an OpenAlex connection object.

    Args:
        email (string): Defaults to None.

    Returns:
        _type_: connection object
    """
    try:
        return OpenAlex(email)
    except:
        raise Exception("Invalid email address")

def convert_to_display_format(record):
    """This function takes in a JSON record and filters based on fixed set of fields
    Not recommended to general use

    Args:
        record (JSON record/dict): Single record from OpenAlex

    Returns:
        JSON record/dict: filtered and processed information for display
    """
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

@st.experimental_memo
def get_related_results(id = None, result_type = "referenced_works", id_type = "DOI"): #TODO: add title support
    """
    _summary_: This function returns a dataframe of results from OpenAlex based on the id and result_type
    
    Args:
        id (str): DOI or arXiv ID string
        result_type (str): Defaults to "referenced_works"
        id_type (str): Defaults to "DOI"

    Returns:
        original_result and related results: Dataframe of results
    """
    if not id: return None

    try:
        if id_type == "Title":
            test_autocomplete(id)
        #handling the arxiv case
        if id_type == "Arxiv":
            id = arxiv_to_doi(id)
        elif id_type == "DOI":
            if id and "doi.org/" not in id:
                id = "doi/" + id
            if id and not id.startswith('https://'):
                id = 'https://' + id

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
        rel_list = rel_list[['title', 'publication_date', 'doi', 'authors', 'issn', 'location',
         'publisher', 'oa_url']]
        #rename columns with proper names
        rel_list.columns = ["Title", "Publication Date", "DOI", "Authors", "ISSN", "Location",
         "Publisher", "Open Access URL"]
        return original_result, rel_list
    except:
        raise Exception("")   

@st.experimental_memo
def get_recommended_results(search_text, entity_type = "All", exact_match = False):
    """_summary_: This function returns a dataframe of recommended results from OpenAlex based on the search_text

    Args:
        search_text (str): Single or multiple word phrases
        exact_match (bool, optional): Defaults to False. If True, only exact matches are returned

    Returns:
        DataFrame: Dataframe of recommended results computed by OpenAlex
    """
    if not search_text: return None
    #replace spaces with %20
    search_text = search_text.replace(" ", "%20")
    if exact_match:
        #enclose the search text in %22
        search_text = "%22" + search_text + "%22"
    
    #dictionary that matches entity type to crossref type
    type_match = {"Journal Articles": "journal-article", "Data": "dataset", "Reports": "report",
     "Proceedings Articles": "proceedings-article", "Dissertations": "dissertation", "Books": "book"}
    
    query_string = 'https://api.openalex.org/works?filter=display_name.search:' + search_text + ',abstract.search:' + search_text + ',title.search:' + search_text

    if entity_type != "All":
        entity_type = type_match[entity_type]
        query_string += ',type:' + entity_type

    response = json.loads(requests.get(query_string, params = {'mailto': 'chinardankhara@gmail.com'}).text)['results']
    response = pd.DataFrame.from_records([convert_to_display_format(i) for i in response])
    response = response[['title', 'publication_date', 'doi', 'authors', 'issn', 'location', 'publisher', 'oa_url']]
    response.columns = ["Title", "Publication Date", "DOI", "Authors", "ISSN", "Location",
         "Publisher", "Open Access URL"]
    return response

def arxiv_to_doi(arxiv_id):
    """_summary_: This function converts an arXiv ID to a DOI

    Args:
        arxiv_id (str): None

    Returns:
        str: None
    """
    #if the id is a link, extract the id
    if "arxiv.org" in arxiv_id:
        arxiv_id = arxiv_id.split("/")[-1]
    return next(arxiv.Search(id_list = [arxiv_id]).results()).doi
