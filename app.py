import streamlit as st
import streamlit_option_menu as som
import openalex as oa
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

st.set_page_config(page_title="Lit Search", layout = "wide")

st.markdown('<h1 style="text-align: center;">Literature Search</h1>', unsafe_allow_html=True)
st.markdown('<br>', unsafe_allow_html=True)
type_menu = som.option_menu(None, ["Search by DOI", "Search by Topic"], icons = ['123', 'collection'], default_index=0, orientation="horizontal")

def display_search_by_doi():
    #add radio button for refereced and related works
    type = st.radio("Type of results", ["Referenced Works", "Related Works"], horizontal=True)
    #put a text input box
    doi = st.text_input('Search DOI', help = "Returns works related to the input paper")
    #add 'https://' to the doi if it doesn't exist
    if doi and "doi.org/" not in doi:
        doi = "doi/" + doi
    if doi and not doi.startswith('https://'):
        doi = 'https://' + doi
    data = oa.get_results_from_doi(doi, key = type)
    #if dataframe is empty, display "DOI not found"
    if data is None:
        st.write("Invalid DOI")
    else:
        data = df_to_aggrid(data)

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

hide_streamlit_style = """<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)




