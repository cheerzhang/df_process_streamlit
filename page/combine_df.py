import streamlit as st
import pandas as pd
from page.tool_func import read_dataframe_file


@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

def download_csv(df_result):
    csv = convert_df(df_result)
    file_name = st.text_input('Modify file name', 'combined_df')
    st.download_button( 
        label="Download the combined file",
        data=csv,
        file_name=f'{file_name}.csv',
        mime='text/csv',
    )


def combine_two_df():
    df1 = None
    df2 = None
    time_df = st.checkbox("It's time series dataframe")
    remove_duplicate_bool = st.checkbox("Remove duplicate")
    col1, col2, col3 = st.columns([2, 2, 1], gap="medium")
    with col1:
        upload_df_1 = st.file_uploader("Choose 1st data file:", key="file1_upload")
        if upload_df_1 is not None:
            df1 = read_dataframe_file(upload_df_1)
    if time_df and df1 is not None:
        with col3:
            time_column = st.selectbox('Selct Time Column', df1.columns.values)
            df1[time_column] = pd.to_datetime(df1[time_column], infer_datetime_format=True, errors='coerce')
        with col1:
            st.write(f"file 1 created_at range:")
            st.write(f":blue[{df1[time_column].min()}] - :blue[{df1[time_column].max()}]")
            st.divider()
    if remove_duplicate_bool and df1 is not None:
        with col3:
            id_column = st.selectbox('Selct id Column', df1.columns.values)
    if df1 is not None:
        with col3:
            st.write(f"file 1 size: :blue[{df1.shape}]")
    with col2:
        upload_df_2 = st.file_uploader("Choose 2nd data file:", key="file2_upload")
        if upload_df_2 is not None:
            df2 = read_dataframe_file(upload_df_2)
    if time_df and df2 is not None:
        with col2:
            df2[time_column] = pd.to_datetime(df2[time_column], infer_datetime_format=True, errors='coerce')
            st.write(f"file 2 created_at range:")
            st.write(f":blue[{df2[time_column].min()}] - :blue[{df2[time_column].max()}]")
            st.divider()
    if df2 is not None:
        with col3:
            st.write(f"file 2 size: :blue[{df2.shape}]")
    if df1 is not None and df2 is not None:
        columns_in_df1_not_in_df2 = df1.columns.difference(df2.columns)
        if columns_in_df1_not_in_df2.size > 0:
            with col1:
                st.markdown("File1 unique features: (not in File2):")
                st.write(columns_in_df1_not_in_df2)
                st.success(f"Files columns analysis done!") 
        columns_in_df2_not_in_df1 = df2.columns.difference(df1.columns)
        if columns_in_df2_not_in_df1.size > 0:
            with col2:
                st.markdown("File2 unique features: (not in File1):")
                st.write(columns_in_df1_not_in_df2)
                st.success(f"Files columns analysis done!") 
        if columns_in_df1_not_in_df2.size == columns_in_df2_not_in_df1.size == 0:
                st.success(f"Files columns analysis done!") 
        if time_df:
            with st.spinner("combineing ..."):
                df_result = pd.concat([df1, df2], axis=0)
                st.write(f"combined dataframe size (before drop duplicate): :blue[{df_result.shape[0]}]")
                st.write(f"combined dataframe time range")
                st.write(f":blue[{df_result[time_column].min()}] - :blue[{df_result[time_column].max()}]")
                st.success(f"Files combine done!") 
                st.divider()
            if remove_duplicate_bool:
                with st.spinner("removing dplicated rows ..."):
                    df_result.drop_duplicates(subset=id_column, keep='first', inplace=True)
                    st.write(f"combined dataframe size (after drop duplicate): :blue[{df_result.shape[0]}]")
                    st.write(f"combined dataframe time range")
                    st.write(f":blue[{df_result[time_column].min()}] - :blue[{df_result[time_column].max()}]")
                    st.success(f"Files duplicate revoming done!") 
                    st.divider()
                with col3:
                    download_csv(df_result)
        else:
            with st.spinner("combineing ..."):
                df_result = pd.concat([df1, df2], axis=0)
            st.write(f"combined dataframe size (before drop duplicate): :blue[{df_result.shape[0]}]")
            st.divider()
            if remove_duplicate_bool:
                df_result.drop_duplicates(subset=id_column, keep='first', inplace=True)
                st.write(f"combined dataframe size (after drop duplicate): :blue[{df_result.shape[0]}]")
                st.success(f"Files duplicate revoming done!") 
                st.divider()
                with col3:
                    download_csv(df_result)