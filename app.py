import streamlit as st
import streamlit_option_menu as som
import openalex as oa
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

st.set_page_config(page_title="Lit Search", layout = "wide")

st.markdown('<h1 style="text-align: center;">Literature Search</h1>', unsafe_allow_html=True)
st.markdown('<br>', unsafe_allow_html=True)
type_menu = som.option_menu(None, ["Search by DOI", "Search by Topic"],
 icons = ['123', 'collection'], default_index=0, orientation="horizontal")

def display_search_by_doi():
    #add radio button for refereced and related works
    type = st.radio("Type of results", ["Referenced Works", "Related Works"], horizontal=True,
     help="Referenced works are works that are cited by the given DOI. Related works are works that are similar to the given DOI - generated algorithmically.")
    #put a text input box
    doi = st.text_input('Search DOI',
     help = "Returns works related to the input paper")

    #some doi handling  
    if doi and "doi.org/" not in doi:
        doi = "doi/" + doi
    if doi and not doi.startswith('https://'):
        doi = 'https://' + doi
    
    try:
        data = oa.get_results_from_doi(doi, key = type)
        data = df_to_aggrid(data)
    except:
        if doi: st.markdown('<p style="color:white; font-weight:bold;">Invalid DOI</p>',
         unsafe_allow_html=True)

def df_to_aggrid(df):
        #TODO: make this function configurable
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gridOptions = gb.build()   
        df = AgGrid(df, gridOptions=gridOptions)
        return df

#TODO: add search by topic code
display_search_by_doi()

hide_streamlit_style = """<style> # footer {visibility: hidden;}</style>"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)




