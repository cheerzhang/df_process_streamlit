import streamlit as st
import streamlit_authenticator as stauth


import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
name, authentication_status, username = authenticator.login('Login', 'main')


from page.combine_df import combine_two_df
from page.psi import get_psi

if st.session_state["authentication_status"]:
    with st.sidebar:
        authenticator.logout('Logout', 'main', key='logout')
        st.write(f'Welcome *{st.session_state["name"]}*')
    tab1, tab2, tab3 = st.tabs(["Combine df", "PSI", "Logout"])
    with tab1:
        st.title('Combine Dataframe')
        combine_two_df()
    with tab2:
        st.title('PSI')
        get_psi()
    with tab3:
        authenticator.logout('Logout', 'main')
        st.write(f'Welcome *{st.session_state["name"]}*')
    
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')