import streamlit as st
import pandas as pd

def app():
    upload_df = st.file_uploader("Choose dataframe file:", key="file1_upload")
    if upload_df is not None:
        df = pd.read_csv(upload_df)
        col_old_df, col_new_df = st.columns(2)
        with col_old_df:
            st.dataframe(df)
        original_names = df.columns.values.tolist()
        new_names = {}
        for name in original_names:
            new_names[name] = st.text_input(f'Original Name: {name}', name, key=f"text_input_{name}")
        df_new = df.rename(columns=name)
        with col_new_df:
            st.dataframe(df_new)


if __name__ == '__main__':
    st.markdown('# Change Dataframe Name')
    app()