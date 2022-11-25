import streamlit as st
import streamlit_option_menu as som
import openalex as oa
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

#set page title and favicon
st.set_page_config(page_title="ScholarWeb", layout="wide")

#adding raise issue link to the right
col1, col2, col3 = st.columns([1,3,1])
with col3:
    link = '[Report a bug / Request a feature](https://forms.gle/5M564n5YFtAVtGHi8)'
    st.markdown(link, unsafe_allow_html=True)

#set title and description display
st.markdown('<h1 style="text-align: center;">Welcome to ScholarWeb</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center;">Your place for finding research, people, and more</h3>',
 unsafe_allow_html=True)
#add an option menu
st.markdown('<br>', unsafe_allow_html=True)
type_menu = som.option_menu(None, ["Related Papers", "Discover", "Find People"],
 icons = ['123', 'search'], default_index=0, orientation="horizontal")

def display_search_by_id():
    """_summary_: This function displays the search by id section of the app
    Only handles the display of the section, not the logic
    For logic, check get_related_results()
    """
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

    try:
        og_result, data = oa.get_related_results(id, result_type = result_type, id_type = id_type)
        data = df_to_aggrid(data)
    except:
        if id:
            st.markdown('<p style="color:white; font-weight:bold;">Invalid ID. The application is under development' +
             '- so it might be a system fault. Thanks for your patience.</p>', unsafe_allow_html=True)
        
def display_discovery():
    """_summary_: This function displays the discovery section of the app
    For logic, check get_recommended_results()
    """
    #add a checkbox for exact search
    exact = st.checkbox("Exact Search", help="For multi-word phrases, exact search checks for full phrase match.")
    #add a text input for search
    search = st.text_input('Search Relevant Papers',
     help = "Returns works related to the input search term")
    if search:
        data = oa.get_recommended_results(search, exact_match = exact)
        data = df_to_aggrid(data)

def display_find_people():
    st.markdown('<p style="color:white; font-weight:bold;">This feature is under development.</p>', unsafe_allow_html=True)


def df_to_aggrid(df):
    """
    _summary_: This function converts a pandas dataframe to a streamlit aggrid
    streamlit aggrid is a wrapper for ag-grid, a javascript library for displaying data in a table
    """
    #TODO: make this function configurable
    cell_renderer = JsCode("""function(params) {return `<a href=${params.value} target="_blank">${params.value}</a>`}""")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
    gb.configure_side_bar() #Add a sidebar
    gb.configure_column("DOI", cellRenderer=cell_renderer) #Add a link to the DOI column
    gb.configure_column("Open Access URL", cellRenderer=cell_renderer) #Add a link to the Open Access URL column
    gridOptions = gb.build()   
    df = AgGrid(df, gridOptions=gridOptions, allow_unsafe_jscode=True)
    return df

if type_menu == "Related Papers":
    display_search_by_id()
elif type_menu == "Discover":
    display_discovery()
elif type_menu == "Find People":
    display_find_people()

#hide streamlit footer
hide_streamlit_style = """ <style> footer {visibility: hidden;} </style> """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)




