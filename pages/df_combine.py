import streamlit as st
import pandas as pd
from util import process_util

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

def app():
    time_tool = process_util.Time_Tool()
    df1 = None
    df2 = None
    time_column = []
    col1, col2 = st.columns([3, 2], gap="medium")
    with col1:
        time_df = st.checkbox("It's time series dataframe")
        remove_duplicate_bool = st.checkbox("Remove duplicate")
        upload_df_1 = st.file_uploader("Choose 1st data file:", key="file1_upload")
        if upload_df_1 is not None:
            df1 = pd.read_csv(upload_df_1)
            if time_df:
                time_column = st.selectbox('Selct Time Column', df1.columns.values)
                df1[time_column] = pd.to_datetime(df1[time_column], infer_datetime_format=True, errors='coerce')
                with col2:
                    st.write(f"file 1 created_at range:")
                    st.write(f":blue[{df1[time_column].min()}] - :blue[{df1[time_column].max()}]")
                    st.divider()
            with col2:
                st.write(f"file 1 size: :blue[{df1.shape}]")
                st.divider()
            if remove_duplicate_bool:
                id_column = st.selectbox('Selct id Column', df1.columns.values)
        upload_df_2 = st.file_uploader("Choose 2nd data file:", key="file2_upload")
        if upload_df_2 is not None:
            df2 = pd.read_csv(upload_df_2)
            if time_df:
                st.markdown(f"time column: {time_column}")
                df2[time_column] = pd.to_datetime(df2[time_column], infer_datetime_format=True, errors='coerce')
                with col2:
                    st.write(f"file 2 created_at range:")
                    st.write(f":blue[{df2[time_column].min()}] - :blue[{df2[time_column].max()}]")
                    st.divider()
            with col2:
                st.write(f"file 2 size: :blue[{df2.shape}]")
                st.divider()
    if upload_df_1 is not None and upload_df_2 is not None:
        time_tool.start_timer()
        with col1:
            columns_in_df1_not_in_df2 = df1.columns.difference(df2.columns)
            if columns_in_df1_not_in_df2.size > 0:
                st.markdown("File1 unique features: (not in File2):")
                st.write(columns_in_df1_not_in_df2)
                st.success(f"Files columns analysis done!") 
                st.success(f"time using: {time_tool.end_timer()}")
            columns_in_df2_not_in_df1 = df2.columns.difference(df1.columns)
            if columns_in_df2_not_in_df1.size > 0:
                st.markdown("File2 unique features: (not in File1):")
                st.write(columns_in_df1_not_in_df2)
                st.success(f"Files columns analysis done!") 
                st.success(f"time using: {time_tool.end_timer()}")
            if columns_in_df1_not_in_df2.size == columns_in_df2_not_in_df1.size == 0:
                st.success(f"Files columns analysis done!") 
                st.success(f"time using: {time_tool.end_timer()}")
            if time_df:
                with st.spinner("combineing ..."):
                    time_tool.start_timer()
                    df_result = pd.concat([df1, df2], axis=0)
                    with col2:
                        st.write(f"combined dataframe size (before drop duplicate): :blue[{df_result.shape[0]}]")
                        st.write(f"combined dataframe time range")
                        st.write(f":blue[{df_result[time_column].min()}] - :blue[{df_result[time_column].max()}]")
                        st.success(f"Files combine done!") 
                        st.success(f"time using: {time_tool.end_timer()}")
                        st.divider()
                    if remove_duplicate_bool:
                        with col2:
                            df_result.drop_duplicates(subset=id_column, keep='first', inplace=True)
                            st.write(f"combined dataframe size (after drop duplicate): :blue[{df_result.shape[0]}]")
                            st.write(f"combined dataframe time range")
                            st.write(f":blue[{df_result[time_column].min()}] - :blue[{df_result[time_column].max()}]")
                            st.success(f"Files duplicate revoming done!") 
                            st.success(f"time using: {time_tool.end_timer()}")
                            st.divider()
                with col2:
                    download_csv(df_result)
            else:
                with st.spinner("combineing ..."):
                    time_tool.start_timer()
                    df_result = pd.concat([df1, df2], axis=0)
                    with col2:
                        st.write(f"combined dataframe size (before drop duplicate): :blue[{df_result.shape[0]}]")
                        st.divider()
                    if remove_duplicate_bool:
                        df_result.drop_duplicates(subset=id_column, keep='first', inplace=True)
                        st.write(f"combined dataframe size (after drop duplicate): :blue[{df_result.shape[0]}]")
                        st.success(f"Files duplicate revoming done!") 
                        st.success(f"time using: {time_tool.end_timer()}")
                        st.divider()
                with col2:
                    download_csv(df_result)
        

if __name__ == '__main__':
    st.markdown('# Combind Dataframe')
    app()