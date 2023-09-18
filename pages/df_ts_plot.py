import streamlit as st
import pandas as pd
from util import process_util

def app():
    st.markdown("# Display TimeSeries DataFrame")
    time_tool = process_util.Time_Tool()
    upload_df_1 = st.file_uploader("Choose 1st data file:", key="file1_upload")
    if upload_df_1 is not None:
        df1 = pd.read_csv(upload_df_1)
        col1, col2, col3 = st.columns(3)
        with col1:
            time_column = st.selectbox('Select Time Column', df1.columns.values)
        with col2:
            numeric_columns = st.selectbox('Select Numeric Column', df1.select_dtypes(include='number').columns.values)
        with col3:
            agg_frequence = st.selectbox('Select Aggreegation', ['Day', 'Week', 'Month'], disabled=True)
        # processing
        col_left, col_right = st.columns([3, 1], gap="medium")
        with st.spinner("processing..."):
            time_tool.start_timer()
            df1[time_column] = pd.to_datetime(df1[time_column], errors='coerce') 
            df1['date'] = df1[time_column]
            df1['date'] = pd.to_datetime(df1['date'])
            df1["day"] = df1['date'].dt.date
            day_user_counts = df1.groupby('day').size().reset_index(name=numeric_columns)
            day_user_counts.set_index('day', inplace=True)
            with col_left:
                st.line_chart(day_user_counts[[numeric_columns]])
            with col_right:
                st.dataframe(day_user_counts)
            st.success(f"procesed, time using: {time_tool.end_timer()}")


if __name__ == '__main__':
    app()