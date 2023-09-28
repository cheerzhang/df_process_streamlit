import streamlit as st
import pandas as pd
import numpy as np


frequency_dist = {
      'Hour': 'H',
      'Day': 'D',
      'Week': 'W-SUN'
}

def calculate_change(df, target_column, frequency_column, include_column, include_values):
    # Filter the DataFrame for the specified include values
    filtered_df = df[(df[include_column].isin(include_values))]
    # Resample the filtered DataFrame to the specified frequency
    resampled_df = filtered_df.groupby(pd.Grouper(key='time', freq=frequency_dist[frequency_column]))
    # Calculate the number of true, false, and null values
    counts = resampled_df[target_column].value_counts().unstack().fillna(0)
    counts.rename(columns={1: 'one', 0: 'zero'}, inplace=True)
    if 'one' in counts.columns.values and 'zero' in counts.columns.values:
        counts['true_in_tf'] = counts['one'] / (counts['zero'] + counts['one'])
        counts['last_true_in_tf'] = counts['true_in_tf'] - counts['true_in_tf'].shift(1)
        # Get the last value of 'last_true_in_tf'
        last_value = counts['last_true_in_tf'].iloc[-1]
        return counts.index[-2:].values, last_value
    return counts.index[-2:].values, 0

def app():
    upload_df_2 = st.file_uploader("Choose pass rate data file:", key="file2_upload")
    if upload_df_2 is not None:
        df = pd.read_csv(upload_df_2)
        col_option1, col_option2 = st.columns(2)
        with col_option1:
            st.markdown('#### filter options')
            time_column = st.selectbox('Select Time Column', df.columns.values, index=df.columns.get_loc('created_at') if 'created_at' in df.columns.values else 0)
            frequency_column = st.selectbox('Select Frequency', ['Week', 'Day', 'Hour'], index=1) 
            target_column = st.selectbox('Select Analysis Column', df.columns.values, index=5)
        with col_option2:
            st.markdown('#### exclude values')
            col_left1, col_right1 = st.columns(2)
            with col_left1:
                include_column1 = st.selectbox('Select Include Column 1', df.columns.values, index=2)
                include_values1 = st.multiselect('Include Values 1', df[include_column1].unique(), [df[include_column1].unique()[0]])
            with col_right1:
                exclude_column = st.selectbox('Select Exclude Column 2', df.columns.values, index=0)
                exclude_values = st.multiselect('Exclude Values 2', df[exclude_column].unique(), [df[exclude_column].unique()[0]])
        # exclude logic
        df_ = df.copy()
        df_ = df_[df_[include_column1].isin(include_values1)]
        df_[time_column] = pd.to_datetime(df_[time_column], errors='coerce') 
        df_['time'] = df_[time_column]
        df_.set_index('time', inplace=True)
        # time series logic - 3 value
        df_3_true = df_[df_[target_column] == 1].resample(frequency_dist[frequency_column]).size().reset_index(name='total_true')
        df_3_false = df_[df_[target_column] == 0].resample(frequency_dist[frequency_column]).size().reset_index(name='total_false')
        df_3_null = df_[df_[target_column] == -1].resample(frequency_dist[frequency_column]).size().reset_index(name='total_null')
        df_3 = df_3_true.merge(df_3_false, on='time', how='outer')
        df_3 = df_3.merge(df_3_null, on='time', how='outer')
        df_3.set_index('time', inplace=True)
        st.markdown('Total True, Total False, Total Null counts')
        with st.expander('Total True, Total False, Total Null counts'):
            st.bar_chart(df_3[['total_true', 'total_false', 'total_null']])
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
            st.bar_chart(df_3[display_columns])

        st.divider()
        st.markdown('### Report')
        df_ = df.copy()
        df_[time_column] = pd.to_datetime(df_[time_column], errors='coerce') 
        df_['time'] = df_[time_column]
        # overall report
        all_values = df_[include_column1].unique()
        last_2_time, change = calculate_change(df_, target_column, frequency_column, include_column1, all_values)
        changes = [{
                f'{include_column1}': 'All',
                'Change': change,
                'Change %': f'{np.round(change * 100, 2)} %'
        }]
        # Calculate the change for each include value
        for include_value in all_values:
            _, change = calculate_change(df_, target_column, frequency_column, include_column1, [include_value])
            changes.append({
                f'{include_column1}': include_value,
                'Change': change,
                'Change %': f'{np.round(change * 100, 2)} %'
            })
        # Create a DataFrame from the changes
        # Display the DataFrame using st.dataframe
        st.markdown(f"Report of changed in {last_2_time[-1]} compare to {last_2_time[-2]}")
        overall_report = pd.DataFrame(changes)
        col_big_negtive, col_negtive, col_other = st.columns(3)
        with col_big_negtive:
            st.dataframe(overall_report[overall_report['Change'] <= -0.05])
        with col_negtive:
            st.dataframe(overall_report[overall_report['Change'] <= 0])

        



if __name__ == '__main__':
    app()