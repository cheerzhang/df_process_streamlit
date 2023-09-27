import streamlit as st
import pandas as pd


frequency_dist = {
      'Hour': 'H',
      'Day': 'D',
      'Week': 'W-SUN'
}


def app():
    upload_df_2 = st.file_uploader("Choose pass rate data file:", key="file2_upload")
    if upload_df_2 is not None:
        df = pd.read_csv(upload_df_2)
        col_option1, col_option2 = st.columns(2)
        with col_option1:
            st.markdown('#### filter options')
            time_column = st.selectbox('Select Time Column', df.columns.values, index=df.columns.get_loc('created_at') if 'created_at' in df.columns.values else 0)
            frequency_column = st.selectbox('Select Frequency', ['Week', 'Day', 'Hour'], index=1) 
            target_column = st.selectbox('Select Analysis Column', df.columns.values, index=0)
        with col_option2:
            st.markdown('#### exxclude values')
            col_left1, col_right1 = st.columns(2)
            with col_left1:
                exclude_column = st.selectbox('Select Exclude Column 1', df.columns.values, index=0)
                exclude_values = st.multiselect('Exclude Values 1', df[exclude_column].unique(), [df[exclude_column].unique()[0]])
            with col_right1:
                exclude_column = st.selectbox('Select Exclude Column 2', df.columns.values, index=0)
                exclude_values = st.multiselect('Exclude Values 2', df[exclude_column].unique(), [df[exclude_column].unique()[0]])
        # exclude logic
        df = df[~df[exclude_column].isin(exclude_values)]
        df[time_column] = pd.to_datetime(df[time_column], errors='coerce') 
        df['time'] = df[time_column]
        df.set_index('time', inplace=True)
        # time series logic - 3 value
        df_3_true = df[df[target_column] == 1].resample(frequency_dist[frequency_column]).size().reset_index(name='total_true')
        df_3_false = df[df[target_column] == 0].resample(frequency_dist[frequency_column]).size().reset_index(name='total_false')
        df_3_null = df[df[target_column] == -1].resample(frequency_dist[frequency_column]).size().reset_index(name='total_null')
        df_3 = df_3_true.merge(df_3_false, on='time', how='outer')
        df_3 = df_3.merge(df_3_null, on='time', how='outer')
        df_3.set_index('time', inplace=True)
        st.markdown('Total True, Total False, Total Null counts')
        with st.expander('Total True, Total False, Total Null counts'):
            st.line_chart(df_3[['total_true', 'total_false', 'total_null']])
        # calculate ratio
        df_3['true_in_all'] = df_3['total_true'] / (df_3['total_true'] + df_3['total_false'] + df_3['total_null'])
        df_3['true_in_tf'] = df_3['total_true'] / (df_3['total_true'] + df_3['total_false'])
        df_3['true_in_tn'] = df_3['total_true'] / (df_3['total_true'] + df_3['total_null'])

        df_3['false_in_all'] = df_3['total_false'] / (df_3['total_true'] + df_3['total_false'] + df_3['total_null'])
        df_3['false_in_tf'] = df_3['total_false'] / (df_3['total_true'] + df_3['total_false'])
        df_3['false_in_fn'] = df_3['total_false'] / (df_3['total_false'] + df_3['total_null'])

        df_3['null_in_all'] = df_3['total_null'] / (df_3['total_true'] + df_3['total_false'] + df_3['total_null'])
        df_3['null_in_fn'] = df_3['total_null'] / (df_3['total_false'] + df_3['total_null'])
        df_3['null_in_tn'] = df_3['total_null'] / (df_3['total_true'] + df_3['total_null'])

        st.markdown('True, False, Null ratio')
        with st.expander('True, False, Null ratio'):
            ratio_columns = ['true_in_all', 'true_in_tf', 'true_in_tn', 'false_in_all', 'false_in_tf', 'false_in_fn', 'null_in_all', 'null_in_fn', 'null_in_tn']
            display_columns = st.multiselect('Select Display Columns', ratio_columns, ratio_columns)
            st.line_chart(df_3[display_columns])
        
        



if __name__ == '__main__':
    app()