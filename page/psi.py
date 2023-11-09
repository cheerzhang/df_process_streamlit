import streamlit as st
import pandas as pd
from pandas.api.types import is_string_dtype
import matplotlib.pyplot as plt

from page.tool_func import read_dataframe_file

    

def get_psi():
    st.markdown(f"Upload 2 files to compare")
    df1 = None
    df2 = None
    arr_1 = []
    col1, col2 = st.columns(2)
    with col1:
        upload_df_1 = st.file_uploader("Choose 1st data file:", key="psi_1_upload")
        if upload_df_1 is not None:
            df1 = read_dataframe_file(upload_df_1)
            df1_column = st.selectbox('Selct Column', df1.columns.values, index=0, key='psi_1_column')
            catogery_on_1 = st.toggle('Catogery Feature', value = is_string_dtype(df1[df1_column]), key='psi_1_switch')
            if catogery_on_1:
                # do repeat check
                arr_1 = df1[df1_column].unique()
                st.write(f"All Catogery is :blue[{len(arr_1)}]")
    with col2:
        upload_df_2 = st.file_uploader("Choose 2nd data file:", key="psi_2_upload")
        if upload_df_2 is not None:
            df2 = read_dataframe_file(upload_df_2)
            df2_column = st.selectbox('Selct Column', df2.columns.values, index=0, key='psi_2_column')
            catogery_on_2 = st.toggle('Catogery Feature', value = is_string_dtype(df2[df2_column]), key='psi_2_switch')
            if catogery_on_2 and len(arr_1) > 0:
                df2['is_in_1'] = df2[df2_column].apply(lambda x: 1 if x in arr_1 else 0)
                sum_total = df2['is_in_1'].shape[0]
                sum_old = df2['is_in_1'].sum()
                sum_new = sum_total - sum_old
                st.write(f"In total :blue[{sum_total}], New catogery is :blue[{sum_new}]")
                fig, ax = plt.subplots()
                ax.pie([sum_old, sum_new], labels=['Old', 'New'], autopct='%1.1f%%', startangle=90)
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                st.pyplot(fig)

