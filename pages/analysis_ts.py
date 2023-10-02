import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


frequency_dist = {
      'Hour': 'H',
      'Day': 'D',
      'Week': 'W-MON'
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
        counts['counts'] = counts['zero'] + counts['one']
        counts['last_true_in_tf'] = counts['true_in_tf'] - counts['true_in_tf'].shift(1)
        counts['last_counts'] = (counts['counts'] - counts['counts'].shift(1)) / counts['counts'].shift(1)
        # Get the last value of 'last_true_in_tf'
        last_value_tf = counts['last_true_in_tf'].iloc[-1]
        last_value_counts_change = counts['last_counts'].iloc[-1]
        last_value_counts = counts['counts'].iloc[-1]
        return counts.index[-2:].values, last_value_tf, last_value_counts_change, last_value_counts
    return counts.index[-2:].values, 0, 0, 0


def display_by_filter(df, target_column, frequency_column, include_column, include_values):
    filtered_df = df[(df[include_column].isin(include_values))]
    resampled_df = filtered_df.groupby(pd.Grouper(key='time', freq=frequency_dist[frequency_column]))
    counts = resampled_df[target_column].value_counts().unstack().fillna(-1)
    counts.rename(columns={1: 'True', 0: 'False'}, inplace=True)
    if 'True' in counts.columns.values and 'False' in counts.columns.values:
        counts['true_in_tf'] = counts['True'] / (counts['False'] + counts['True'])
        counts['counts'] = counts['False'] + counts['True']
    else:
        counts['true_in_tf'] = None
    col_left_plot, col_right_plot = st.columns(2)
    with col_left_plot:
        st.line_chart(counts[['True', 'False', 'counts']])
    with col_right_plot:
        st.line_chart(counts[['true_in_tf']])
    with st.expander("data table"):
        st.dataframe(counts)

def app():
    upload_df_2 = st.file_uploader("Choose pass rate data file:", key="file2_upload")
    if upload_df_2 is not None:
        df = pd.read_csv(upload_df_2)
        # filter one week by one week
        df = df[df['created_at'] < '2023-10-02']
        col_option1, col_option2 = st.columns(2)
        with col_option1:
            st.markdown('#### filter options')
            time_column = st.selectbox('Select Time Column', df.columns.values, index=df.columns.get_loc('created_at') if 'created_at' in df.columns.values else 0)
            frequency_column = st.selectbox('Select Frequency', ['Week', 'Day', 'Hour'], index=1) 
            target_column = st.selectbox('Select Analysis Column', df.columns.values, index=5)
            type_column = st.multiselect('Select Type Value', ['p', 'c'], ['p', 'c'])
            df = df[df['type'].isin(type_column)]
        with col_option2:
            st.markdown('#### exclude values')
            col_left1, col_right1 = st.columns(2)
            with col_left1:
                include_column1 = st.selectbox('Select Include Column 1', df.columns.values, index=2)
                include_values1 = st.multiselect('Include Values 1', df[include_column1].unique(), [df[include_column1].unique()[0]])
            with col_right1:
                include_column2 = st.selectbox('Select Exclude Column 2', df.columns.values, index=4)
                include_values2 = st.multiselect('Exclude Values 2', df[include_column2].unique(), [df[include_column2].unique()[0]])
        # exclude logic
        df_ = df.copy()
        df_[time_column] = pd.to_datetime(df_[time_column], errors='coerce') 
        df_['time'] = df_[time_column]
        # df_.set_index('time', inplace=True)
        # all values plot:
        after_exclude = [item for item in df_[include_column1].unique() if item not in include_values1]
        display_by_filter(df_, target_column, frequency_column, include_column1, after_exclude)
        # logic start --------------------------------------------------------
    
        st.divider()
        st.markdown(f'### Report by {frequency_column} - {include_column1}')
        df_ = df.copy()
        df_[time_column] = pd.to_datetime(df_[time_column], errors='coerce') 
        df_['time'] = df_[time_column]
        # ----------------------------------------------------------- overall report --------------------------------------------------------------------
        st.markdown('For Ratio')
        all_values = df_[include_column1].unique()
        last_2_time, change_tf, change_count, counts = calculate_change(df_, target_column, frequency_column, include_column1, all_values)
        changes = [{
            f'{include_column1}': 'All',
            'Change': change_tf,
            'Change %': f'{np.round(change_tf * 100, 2)} %',
            'Change(Count)': change_count,
            'Change(Count) %': f'{np.round(change_count * 100, 2)} %',
            'Total Count': counts
        }]
        # Calculate the change for each include value
        for include_value in all_values:
            _, change_tf, change_count, counts = calculate_change(df_, target_column, frequency_column, include_column1, [include_value])
            changes.append({
                f'{include_column1}': include_value,
                'Change': change_tf,
                'Change %': f'{np.round(change_tf * 100, 2)} %',
                'Change(Count)': change_count,
                'Change(Count) %': f'{np.round(change_count * 100, 2)} %',
                'Total Count': counts
            })
        # Display the DataFrame using st.dataframe
        st.markdown(f"Report of changed in {last_2_time[-1]} compare to {last_2_time[-2]}")
        overall_report = pd.DataFrame(changes)
        st.markdown('For Ratio')
        col_big_negtive, col_negtive, col_other = st.columns(3)
        with col_big_negtive:
            negtive_df = overall_report[overall_report['Change'] <= -0.05].sort_values(by='Change')
            st.dataframe(negtive_df[[f'{include_column1}', 'Change %']])
        with col_negtive:
            st.dataframe(overall_report[(overall_report['Change'] < 0) & (overall_report['Change'] > -0.05)].sort_values(by='Change')[[f'{include_column1}', 'Change %']])
        with col_other:
            st.dataframe(overall_report[overall_report['Change'] >= 0].sort_values(by='Change')[[f'{include_column1}', 'Change %']])
        st.markdown('For Counts')
        col_image, col_df = st.columns([3, 1])
        all_count_plot = overall_report.sort_values(by='Total Count', ascending=False)
        all_ = all_count_plot[all_count_plot[f'{include_column1}']=='All']['Total Count'].values
        all_count_plot['count_ratio'] = all_count_plot['Total Count'] / all_
        with col_df:
            st.dataframe(all_count_plot[[f'{include_column1}', 'Total Count', 'count_ratio', 'Change %']])
        with col_image:
            all_count_plot = all_count_plot.iloc[1:]
            st.bar_chart(data=all_count_plot[[f'{include_column1}', 'Total Count']], x=f'{include_column1}', y='Total Count')
        


        st.divider()
        st.markdown('For Counts Change')
        col_big_negtive1, col_negtive1, col_other1 = st.columns(3)
        with col_big_negtive1:
            negtive_df = overall_report[overall_report['Change(Count)'] <= -0.05].sort_values(by='Change(Count)')
            st.dataframe(negtive_df[[f'{include_column1}', 'Change(Count) %']])
        with col_negtive1:
            st.dataframe(overall_report[(overall_report['Change(Count)'] < 0.05) & (overall_report['Change(Count)'] > -0.05)].sort_values(by='Change(Count)')[[f'{include_column1}', 'Change(Count) %']])
        with col_other1:
            st.dataframe(overall_report[overall_report['Change(Count)'] >= 0.05].sort_values(by='Change(Count)')[[f'{include_column1}', 'Change(Count) %']])
        # display_by_filter(df_, target_column, frequency_column, include_column1, negtive_df[f'{include_column1}'].unique())
        
        
        st.divider()
        # -----------------------------------   --------------------------------------------------
        st.markdown(f'### Report by {frequency_column} - {include_column2}')
        df_ = df.copy()
        df_[time_column] = pd.to_datetime(df_[time_column], errors='coerce') 
        df_['time'] = df_[time_column]
        changes = []
        all_values = df_[include_column2].unique()
        # Calculate the change for each include value
        last_2_time, change_tf, change_count, counts = calculate_change(df_, target_column, frequency_column, include_column2, all_values)
        changes = [{
            f'{include_column2}': 'All',
            'Change': change_tf,
            'Change %': f'{np.round(change_tf * 100, 2)} %',
            'Change(Count)': change_count,
            'Change(Count) %': f'{np.round(change_count * 100, 2)} %',
            'Total Count': counts
        }]
        for include_value in all_values:
            last_2_time, change_tf, change_count, counts = calculate_change(df_, target_column, frequency_column, include_column2, [include_value])
            changes.append({
                f'{include_column2}': include_value,
                'Change': change_tf,
                'Change %': f'{np.round(change_tf * 100, 2)} %',
                'Change(Count)': change_count,
                'Change(Count) %': f'{np.round(change_count * 100, 2)} %',
                'Total Count': counts
            })
        st.markdown(f"Report of changed in {last_2_time}")
        st.markdown('For Ratio')
        overall_report = pd.DataFrame(changes)
        col_big_negtive2, col_negtive2, col_other2 = st.columns(3)
        with col_big_negtive2:
            negtive_df = overall_report[overall_report['Change'] <= -0.05].sort_values(by='Change')
            st.dataframe(negtive_df[[f'{include_column2}', 'Change %']])
        with col_negtive2:
            st.dataframe(overall_report[(overall_report['Change'] < 0) & (overall_report['Change'] > -0.05)].sort_values(by='Change')[[f'{include_column2}', 'Change %']])
        with col_other2:
            st.dataframe(overall_report[overall_report['Change'] >= 0].sort_values(by='Change')[[f'{include_column2}', 'Change %']])
        st.markdown('For Counts')
        col_image1, col_df1 = st.columns([3, 1])
        all_count_plot = overall_report.sort_values(by='Total Count', ascending=False)
        all_ = all_count_plot[all_count_plot[f'{include_column2}']=='All']['Total Count'].values
        all_count_plot['count_ratio'] = all_count_plot['Total Count'] / all_
        with col_df1:
            st.dataframe(all_count_plot[[f'{include_column2}', 'Total Count', 'count_ratio', 'Change %']])
        with col_image1:
            all_count_plot = all_count_plot.iloc[1:]
            st.bar_chart(data=all_count_plot[[f'{include_column2}', 'Total Count']], x=f'{include_column2}', y='Total Count')
        



if __name__ == '__main__':
    app()