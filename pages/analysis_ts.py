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
        counts['shift_counts'] = counts['counts'].shift(1)
        # Get the last value of 'last_true_in_tf'
        last_value_tf = counts['last_true_in_tf'].iloc[-1]
        last_value_counts_change = counts['last_counts'].iloc[-1]
        last_value_counts = counts['counts'].iloc[-1]
        last_shift_counts = counts['shift_counts'].iloc[-1]
        return counts.index[-2:].values, last_value_tf, last_value_counts_change, last_value_counts, last_shift_counts
    return counts.index[-2:].values, 0, 0, 0, 0

def calculate_ratio(df, target_column, frequency_column, prefix):
    resampled_df = df.groupby(pd.Grouper(key='time', freq=frequency_dist[frequency_column]))
    counts = resampled_df[target_column].value_counts().unstack().fillna(-1)
    counts.rename(columns={1: f'{prefix}_True', 0: f'{prefix}_False'}, inplace=True)
    if f'{prefix}_True' in counts.columns.values and f'{prefix}_False' in counts.columns.values:
        counts[f'{prefix}_true_in_tf'] = counts[f'{prefix}_True'] / (counts[f'{prefix}_False'] + counts[f'{prefix}_True'])
        counts[f'{prefix}_counts'] = counts[f'{prefix}_False'] + counts[f'{prefix}_True']
    else:
        counts[f'{prefix}_true_in_tf'] = None
    return counts


def display_by_filter(df, target_column, frequency_column, include_column, include_values, type_column=['p', 'c', 'all']):
    if 'All' in include_values:
        filtered_df = df
    else:
        filtered_df = df[(df[include_column].isin(include_values))]
    filtered_df_p = filtered_df[filtered_df['type'].isin(['p'])]
    filtered_df_c = filtered_df[filtered_df['type'].isin(['c'])]
    counts = calculate_ratio(filtered_df, target_column, frequency_column, prefix = 'all')
    counts_p = calculate_ratio(filtered_df_p, target_column, frequency_column, prefix = 'p')
    counts_c = calculate_ratio(filtered_df_c, target_column, frequency_column, prefix = 'c')
    counts['p_counts'] = counts_p['p_counts']
    counts['p_true_in_tf'] = counts_p['p_true_in_tf']
    counts['c_counts'] = counts_c['c_counts']
    counts['c_true_in_tf'] = counts_c['c_true_in_tf']
    col_left_plot, col_right_plot = st.columns(2)
    with col_left_plot:
        with st.expander('All true, false total counts'):
            st.line_chart(counts[['all_True', 'all_False', 'all_counts']])
        with st.expander("data table (original)"):
            st.dataframe(counts)
    with col_right_plot:
        with st.expander('Acceptance rate true/(true+false)'):
            st.line_chart(counts[[f'{item}_true_in_tf' for item in type_column]])
        with st.expander("data table (last 2 line)"):
            counts.rename(columns={'all_counts': 'total counts', 
                                   'p_counts':   'P counts',
                                   'c_counts':   'C counts',
                                   'all_true_in_tf': 'total pass rate',
                                   'p_true_in_tf': 'P pass rate',
                                   'c_true_in_tf': 'C pass rate'}, inplace=True)
            st.dataframe(counts[['total counts', 'P counts', 'C counts', 'total pass rate', 'P pass rate', 'C pass rate']].iloc[-2:])

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
            frequency_column = st.selectbox('Select Frequency', ['Week', 'Day', 'Hour'], index=0) 
            target_column = st.selectbox('Select Analysis Column', df.columns.values, index=5)
            type_column = st.multiselect('Select Type Value (diaplay)', ['p', 'c', 'all'], ['p', 'c', 'all'])
        with col_option2:
            st.markdown('#### exclude values')
            col_left1, col_right1 = st.columns(2)
            with col_left1:
                include_column1 = st.selectbox('Select Include Column 1', df.columns.values, index=2)
                df[include_column1] = df[include_column1].astype(str)
                options1 = ['All'] + df[include_column1].unique().tolist()
                include_values1 = st.multiselect('Include Values 1', options1, default=['All'])
            with col_right1:
                include_column2 = st.selectbox('Select Exclude Column 2', df.columns.values, index=4)
                include_values2 = st.multiselect('Exclude Values 2', df[include_column2].unique(), [df[include_column2].unique()[0]])
        # exclude logic
        df_ = df.copy()
        df_[time_column] = pd.to_datetime(df_[time_column], errors='coerce') 
        df_['time'] = df_[time_column]
        # df_.set_index('time', inplace=True)
        display_by_filter(df_, target_column, frequency_column, include_column1, include_values1, type_column)
        # logic start --------------------------------------------------------
    
        st.divider()
        st.markdown(f'### Report by {frequency_column} - {include_column1}')
        df_ = df.copy()
        df_ = df_[df_['type'].isin(type_column)]
        df_[time_column] = pd.to_datetime(df_[time_column], errors='coerce') 
        df_['time'] = df_[time_column]
        # ----------------------------------------------------------- overall report --------------------------------------------------------------------
        st.markdown('For Ratio')
        all_values = df_[include_column1].unique()
        last_2_time, change_tf, change_count, counts, shift_counts = calculate_change(df_, target_column, frequency_column, include_column1, all_values)
        changes = [{
            f'{include_column1}': 'All',
            'Change': change_tf,
            'Change %': f'{np.round(change_tf * 100, 2)} %',
            'Change(Count)': change_count,
            'Change(Count) %': f'{np.round(change_count * 100, 2)} %',
            'Total Count': counts,
            'Total count (-1)': shift_counts
        }]
        # Calculate the change for each include value
        for include_value in all_values:
            _, change_tf, change_count, counts, shift_counts = calculate_change(df_, target_column, frequency_column, include_column1, [include_value])
            changes.append({
                f'{include_column1}': include_value,
                'Change': change_tf,
                'Change %': f'{np.round(change_tf * 100, 2)} %',
                'Change(Count)': change_count,
                'Change(Count) %': f'{np.round(change_count * 100, 2)} %',
                'Total Count': counts,
                'Total count (-1)': shift_counts
            })
        # Display the DataFrame using st.dataframe
        st.markdown(f"Report of changed in {last_2_time[-1]} compare to {last_2_time[-2]}")
        overall_report = pd.DataFrame(changes)
        st.markdown('For Ratio')
        col_big_negtive, col_negtive, col_other = st.columns(3)
        with col_big_negtive:
            with st.expander('pass rate drop more than 5%'):
                negtive_df = overall_report[overall_report['Change'] <= -0.05].sort_values(by='Change')
                st.dataframe(negtive_df[[f'{include_column1}', 'Change %']])
        with col_negtive:
            with st.expander('pass rate drop less than 5%'):
                st.dataframe(overall_report[(overall_report['Change'] < 0) & (overall_report['Change'] > -0.05)].sort_values(by='Change')[[f'{include_column1}', 'Change %']])
        with col_other:
            with st.expander('pass rate increase:'):
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
            with st.expander('counts drop more than 5%'):
                negtive_df = overall_report[overall_report['Change(Count)'] <= -0.05].sort_values(by='Change(Count)')
                st.dataframe(negtive_df[[f'{include_column1}', 'Change(Count) %']])
        with col_negtive1:
            with st.expander('counts drop less than 5%'):
                st.dataframe(overall_report[(overall_report['Change(Count)'] < 0.05) & (overall_report['Change(Count)'] > -0.05)].sort_values(by='Change(Count)')[[f'{include_column1}', 'Change(Count) %']])
        with col_other1:
            with st.expander('counts increase:'):
                st.dataframe(overall_report[overall_report['Change(Count)'] >= 0.05].sort_values(by='Change(Count)')[[f'{include_column1}', 'Change(Count) %']])
        st.markdown('original table of count change (by check group)')
        st.dataframe(overall_report[[f'{include_column1}', 'Change(Count) %', 'Total Count', 'Total count (-1)']])
        # display_by_filter(df_, target_column, frequency_column, include_column1, negtive_df[f'{include_column1}'].unique())
        
        
        st.divider()
        # -----------------------------------   --------------------------------------------------
        st.markdown(f'### Report by {frequency_column} - {include_column2}')
        df_ = df.copy()
        df_ = df_[df_['type'].isin(type_column)]
        df_[time_column] = pd.to_datetime(df_[time_column], errors='coerce') 
        df_['time'] = df_[time_column]
        changes = []
        all_values = df_[include_column2].unique()
        # Calculate the change for each include value
        last_2_time, change_tf, change_count, counts, shift_counts = calculate_change(df_, target_column, frequency_column, include_column2, all_values)
        changes = [{
            f'{include_column2}': 'All',
            'Change': change_tf,
            'Change %': f'{np.round(change_tf * 100, 2)} %',
            'Change(Count)': change_count,
            'Change(Count) %': f'{np.round(change_count * 100, 2)} %',
            'Total Count': counts,
            'Total count (-1)': shift_counts
        }]
        for include_value in all_values:
            last_2_time, change_tf, change_count, counts, shift_counts = calculate_change(df_, target_column, frequency_column, include_column2, [include_value])
            changes.append({
                f'{include_column2}': include_value,
                'Change': change_tf,
                'Change %': f'{np.round(change_tf * 100, 2)} %',
                'Change(Count)': change_count,
                'Change(Count) %': f'{np.round(change_count * 100, 2)} %',
                'Total Count': counts,
                'Total count (-1)': shift_counts
            })
        st.markdown(f"Report of changed in {last_2_time}")
        st.markdown('For Ratio')
        overall_report = pd.DataFrame(changes)
        col_big_negtive2, col_negtive2, col_other2 = st.columns(3)
        with col_big_negtive2:
            with st.expander('pass rate drop more than 5%'):
                negtive_df = overall_report[overall_report['Change'] <= -0.05].sort_values(by='Change')
                st.dataframe(negtive_df[[f'{include_column2}', 'Change %']])
        with col_negtive2:
            with st.expander('pass rate drop less than 5%'):
                st.dataframe(overall_report[(overall_report['Change'] < 0) & (overall_report['Change'] > -0.05)].sort_values(by='Change')[[f'{include_column2}', 'Change %']])
        with col_other2:
            with st.expander('pass rate increase:'):
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
        st.dataframe(all_count_plot[[f'{include_column2}', 'Total Count', 'count_ratio', 'Change %', 'Change(Count) %', 'Total count (-1)']])



if __name__ == '__main__':
    app()