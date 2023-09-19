import streamlit as st
import pandas as pd
from util import model_util, process_util

def app():
    st.markdown("# Display TimeSeries DataFrame")
    time_tool = process_util.Time_Tool()
    model_obj = model_util.GetModelPredict()
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
        # plot gender f, m ratio
        st.divider()
        fix_gender = st.checkbox("Fix gender by firstname")
        if fix_gender:
            first_name_column = st.selectbox('Select First Name Column', df1.columns.values)
            df_gender = df1[[first_name_column]]
            model_obj.set_url("http://16.170.214.92:5002/api/predict_gender_v1")
            df_gender = model_obj.call_gender_model(df_gender, first_name_column)
            df1['gender'] = df_gender['pred']
            # plot ratio of female everyday
        else:
            col_gender_select_left, col_gender_select_right = st.columns(2)
            with col_gender_select_left:
                gender_column = st.selectbox('Select Gender Column', df1.columns.values)
            with col_gender_select_right:
                gender_f_values = st.multiselect('Values as Female', df1[gender_column].unique())
                df1['gender'] = df1[gender_column].apply(lambda x: 'F' if x in gender_f_values else 'M')
        female_user_counts = df1[df1['gender'] == 'F'].groupby('day')['gender'].count().reset_index(name='female_count')
        total_user_counts = df1.groupby('day')['gender'].count().reset_index(name='total_count')
        gender_df = total_user_counts.merge(female_user_counts, on='day')
        gender_df['female_ratio'] = gender_df['female_count'] / gender_df['total_count']
        gender_df['male_ratio'] = 1 - gender_df['female_ratio']
        gender_df.set_index('day', inplace=True)
        col_f_left, col_f_right = st.columns([3, 1])
        with col_f_left:
            st.bar_chart(gender_df[['female_ratio', 'male_ratio']])
        with col_f_right:
            st.dataframe(gender_df[['female_ratio', 'male_ratio', 'female_count', 'total_count']])


if __name__ == '__main__':
    app()