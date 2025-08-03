import streamlit as st
from controllers.matchController import match_handler

def show_run_matching_page():
    st.title("🧩 Run Roommate Matching")
    
    st.markdown("### Student Matching Status")
    match_handler()