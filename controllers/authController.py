import time
import streamlit as st
from models.auth import authenticate_user, register_user

def login_handler(email, password):
    status, message, user_id, role = authenticate_user(email, password)
    
    if status == "Success":
        st.session_state['user_id'] = user_id
        st.session_state['user_role'] = role
        st.session_state['page'] = 'profile' if role == 'Student' else 'run_matching'
        st.toast(message, icon='✅')
        time.sleep(2)
        st.rerun()
    elif status == "Failed":
        st.toast(message, icon='❌')
    elif status == "Error":
        st.toast(message, icon='⚠')
        
def register_handler(email, password, confirm_password):
    status, message = register_user(email, password, confirm_password)
    if status == "Success":
        st.toast(message, icon='✅')
        del st.session_state['register_email'], st.session_state['register_password'], st.session_state['register_confirm_password']
        st.session_state['page'] = 'login'
        time.sleep(2)
        st.rerun()
    elif status == "Failed":
        st.toast(message, icon='❌')
    elif status == "Error":
        st.toast(message, icon='🚨')
