from diophila import OpenAlex
import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

def get_connection(email = None):
    return OpenAlex(email)

def get_results_from_doi(doi = None, key = "referenced_works"):
    if not doi: return None
    oa = get_connection('chinardankhara@gmail.com') #TODO: this will need parameterization
    try:
        #replace Refereced Works with referenced_works and Related Works with related_works
        key = key.replace(" ", "_").lower()
        temp = oa.get_single_work(doi, "doi")[key]

        cite_list = []
        sub_key_list = set(["title", "doi", "publication_date", "host_venue", "open_access"])
        
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

            cite_list.append(temp2)
        #make a dataframe with sub_key_list as columns
        cite_list = pd.DataFrame.from_records(cite_list)
        cite_list = cite_list[['title', 'publication_date', 'doi', 'issn', 'location', 'publisher', 'oa_url']]

        return cite_list
    except:
        return None   
