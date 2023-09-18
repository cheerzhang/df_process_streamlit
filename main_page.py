import streamlit as st

# Title: Data Scientist Work Note
st.markdown("# Dataframe Process Tools")

col1, col2 = st.columns([3, 1])
with col1:
    with st.expander("[DataFrame Combine](/df_combine)"):
        st.markdown("""
            Combine 2 same features dataframe.
        """)
    with st.expander("[DataFrame TimeSeries Plot](/df_ts_plot)"):
        st.markdown("""
            Display timeseries dataframe.
        """)