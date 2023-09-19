import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from util import model_util, process_util, data_util

def app():
    st.markdown("# Display TimeSeries DataFrame")
    time_tool = process_util.Time_Tool()
    model_obj = model_util.GetModelPredict()
    data_obj = data_util.FE_Base()
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
        else:
            col_gender_select_left, col_gender_select_right = st.columns(2)
            with col_gender_select_left:
                gender_column = st.selectbox('Select Gender Column', df1.columns.values)
            with col_gender_select_right:
                gender_f_values = st.multiselect('Values as Female', df1[gender_column].unique())
                df1['gender'] = df1[gender_column].apply(lambda x: 'F' if x in gender_f_values else 'M')
        # plot ratio of female male 
        female_user_counts = df1[df1['gender'] == 'F'].groupby('day')['gender'].count().reset_index(name='female_count')
        total_user_counts = df1.groupby('day')['gender'].count().reset_index(name='total_count')
        gender_df = total_user_counts.merge(female_user_counts, on='day')
        gender_df['female_ratio'] = round(gender_df['female_count'] / gender_df['total_count'], 2)
        gender_df['male_ratio'] = 1 - gender_df['female_ratio']
        gender_df.set_index('day', inplace=True)
        col_f_left, col_f_right = st.columns([3, 1])
        with col_f_left:
            st.bar_chart(gender_df[['female_ratio', 'male_ratio']])
            st.bar_chart(gender_df[['female_ratio']])
            st.line_chart(gender_df[['female_ratio']])
        with col_f_right:
            st.dataframe(gender_df[['female_ratio', 'male_ratio', 'female_count', 'total_count']])
        st.divider()
        # --------------------------------------  Age Logic --------------------------------------
        col_age_select_left, col_age_select_right = st.columns(2)
        with col_age_select_left:
            birthdate_column = st.selectbox('Select Birthdate Column', df1.columns.values)
            df1[birthdate_column] = pd.to_datetime(df1[birthdate_column], errors='coerce')
            df1['age'] = data_obj.calculate_age(df1, birthdate_column)
            df1['date'] = pd.to_datetime(df1['date'])
            df1["day"] = df1['date'].dt.date
            display_date = st.selectbox('Select Time Value', df1['day'].unique(), index=0)
            df_age_distrub = df1[df1['day'] == display_date]
            # age distribution
            fig, ax = plt.subplots()
            ax.hist(df_age_distrub['age'], bins=10, edgecolor='k')
            ax.set_xlabel('Age')
            ax.set_ylabel('Frequency')
            st.pyplot(fig) 
        with col_age_select_right:
            # age range
            age_range = st.slider('Select a range of age', 0, 100, (25, 35))
            df1['age_range'] = df1['age'].apply(lambda x: 1 if (x>=age_range[0] and x<=age_range[1]) else 0)
            df1['f_age_range'] = (df1['age_range'] == 1) & (df1['gender'] == 'F')
            df1['f_age_range'] = df1['f_age_range'].astype(int)
            # st.dataframe(df1[['age', 'gender', 'f_age_range']])
            female_age_counts = df1[df1['f_age_range'] == 1].groupby('day')['f_age_range'].count().reset_index(name='female_age_counts')
            total_user_counts = df1.groupby('day')['f_age_range'].count().reset_index(name='total_count')
            f_age_df = total_user_counts.merge(female_age_counts, on='day')
            f_age_df['female_age_ratio'] = round(f_age_df['female_age_counts'] / f_age_df['total_count'], 2)
            f_age_df['rest_ratio'] = 1 - f_age_df['female_age_ratio']
            f_age_df.set_index('day', inplace=True) 
            st.dataframe(f_age_df[['female_age_ratio', 'female_age_counts', 'total_count']])
        st.bar_chart(f_age_df[['female_age_ratio']])
        st.line_chart(f_age_df[['female_age_ratio']]) 


if __name__ == '__main__':
    app()