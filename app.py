import streamlit as st
import streamlit_option_menu as som
import openalex as oa
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

st.set_page_config(page_title="Lit Search", layout = "wide")

st.markdown('<h1 style="text-align: center;">Literature Search</h1>', unsafe_allow_html=True)
st.markdown('<br>', unsafe_allow_html=True)
type_menu = som.option_menu(None, ["Search by DOI", "Search Author"],
 icons = ['123', 'person'], default_index=0, orientation="horizontal")

def display_search_by_id():
    #create twto columns for result and id radio buttons
    col1, col2 = st.columns(2)
    with col1:
        result_type = st.radio("Type of results", ["Referenced Works", "Related Works"], horizontal=True,
     help="Referenced works are works that are cited by the given DOI. Related works are works that are similar to the given DOI - generated algorithmically.")
    with col2:
        id_type = st.radio("Type of ID", ["DOI", "Arxiv"], horizontal=True,
     help="DOI is the Digital Object Identifier. Arxiv is the Arxiv ID.")
    
    id = st.text_input('Search ID',
     help = "Returns works related to the input paper").strip()
    if id and "doi.org/" not in id:
        id = "doi/" + id
    if id and not id.startswith('https://'):
        id = 'https://' + id


    try:
        data = oa.get_results_from_id(id, result_type = result_type, id_type = id_type)
        data = df_to_aggrid(data)
    except:
        if id:
            st.markdown('<p style="color:white; font-weight:bold;">Invalid ID. The application is under development' +
             '- so it might be a system fault. Thanks for your patience.</p>', unsafe_allow_html=True)

def display_search_author():
    #add radio button for profile and works
    # type = st.radio("Type of results", ["Profile", "Works"], horizontal=True,
    #  help="Profile returns information about the author. Works returns works by the author.")
    # name = st.text_input('Search Authors',
    #  help = "If things don't work, please try putting exact name of the author").strip()
    #coming soon
    st.markdown('<h3 style="color:white; font-weight:bold;">Coming soon</h3>', unsafe_allow_html=True)

    

def df_to_aggrid(df):
        #TODO: make this function configurable
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gridOptions = gb.build()   
        df = AgGrid(df, gridOptions=gridOptions)
        return df


if type_menu == "Search by DOI":
    display_search_by_id()
elif type_menu == "Search Author":
    display_search_author()


#hide streamlit footer
hide_streamlit_style = """ <style> footer {visibility: hidden;} </style> """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)




