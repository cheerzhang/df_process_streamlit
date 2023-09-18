import streamlit as st
import pandas as pd
from util import data_util, process_util

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

def app():
    st.markdown('# Combind Dataframe')
    time_tool = process_util.Time_Tool()
    df1 = None
    df2 = None
    col1, col2 = st.columns([3, 1])
    with col1:
        time_df = st.checkbox("It's time series dataframe")
        upload_df_1 = st.file_uploader("Choose 1st data file:", key="file1_upload")
        upload_df_2 = st.file_uploader("Choose 2nd data file:", key="file2_upload")
    with col2:
        if upload_df_1 is not None and upload_df_2 is not None:
            time_tool.start_timer()
            df1 = pd.read_csv(upload_df_1)
            df2 = pd.read_csv(upload_df_2)
            columns_in_df1_not_in_df2 = df1.columns.difference(df2.columns)
            if len(columns_in_df1_not_in_df2) > 0:
                st.markdown("File1 unique features: (not in File2):")
                st.write(columns_in_df1_not_in_df2)
                st.success(f"Files columns analysis done! time using: {time_tool.end_timer()}")
            columns_in_df2_not_in_df1 = df2.columns.difference(df1.columns)
            if len(columns_in_df2_not_in_df1) > 0:
                st.markdown("File2 unique features: (not in File1):")
                st.write(columns_in_df1_not_in_df2)
                st.success(f"Files columns analysis done! time using: {time_tool.end_timer()}")
            if columns_in_df1_not_in_df2 == columns_in_df1_not_in_df2 == []:
                st.success(f"Files columns analysis done! time using: {time_tool.end_timer()}")


if __name__ == '__main__':
    app()