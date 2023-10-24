import streamlit as st
import pandas as pd



@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

def download_csv(df_result):
    csv = convert_df(df_result)
    file_name = st.text_input('Modify file name', 'New_column_name_df')
    st.download_button( 
        label="Download the combined file",
        data=csv,
        file_name=f'{file_name}.csv',
        mime='text/csv',
    )


def app():
    upload_df = st.file_uploader("Choose dataframe file:", key="file1_upload")
    if upload_df is not None:
        df = pd.read_csv(upload_df)
        col_name, col_old_df, col_new_df = st.columns(3)
        original_names = df.columns.values.tolist()
        new_names = {}
        with col_name:
            for name in original_names:
                new_names[name] = st.text_input(f'Original Name: {name}', name, key=f"text_input_{name}")
        with col_old_df:
            st.dataframe(df)
        df_new = df.rename(columns=new_names)
        with col_new_df:
            st.dataframe(df_new)
        st.markdown('#### select the columns to download')
        column_options = st.multiselect('select the columns to download', df_new.columns.values, df_new.columns.values[0])
        df_download = df_new[column_options]
        st.dataframe(df_download)
        download_csv(df_download)


if __name__ == '__main__':
    st.markdown('# Change Dataframe Name')
    app()