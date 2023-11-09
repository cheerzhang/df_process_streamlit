import streamlit as st
import pandas as pd

def read_dataframe_file(file_obj):
    if file_obj is not None:
        file_predix = file_obj.name.split('.')[1]
        if file_predix == 'csv':
            df = pd.read_csv(file_obj)
        if file_predix == 'xlsx':
            df = pd.read_excel(file_obj)
        return df
    else:
        st.info(f"Please select file")
        return None