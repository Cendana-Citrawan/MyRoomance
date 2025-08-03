import streamlit as st
from controllers.authController import login_handler, register_handler
from views.components.pageConfig import authentication_page

def show_login_page():
    authentication_page()
    st.title("Login")
    st.text("Please enter your credentials to continue")

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            login_handler(email, password)

    with col2:
        st.text("Don't have an account?")
        if st.button("Register", use_container_width=True):
            st.session_state['page'] = 'register'
            st.rerun()

def show_register_page():
    authentication_page()
    st.title("Register")
    st.text("Create a new account to get started")

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")

        if st.button("Register", use_container_width=True):
            register_handler(email, password, confirm_password)

    with col2:
        st.text("Already have an account?")
        if st.button("Login", use_container_width=True):
            st.session_state['page'] = 'login'
            st.rerun()