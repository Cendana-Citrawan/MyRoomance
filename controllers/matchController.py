import streamlit as st
from models.matching import get_matching_status_counts, run_matching

def match_handler():
    st.markdown("""
    <style>
        .stMainBlockContainer button {
            background-color: var(--vibrant-blue);
            color: white;
        }
        .stMainBlockContainer button p{
            font-weight: bold;
        }
        .stMainBlockContainer button:hover {
            background-color: white;
            color: var(--vibrant-blue);
            border: 2px solid var(--vibrant-blue);
        }
    </style>
    """, unsafe_allow_html=True)
    status, message, status_counts = get_matching_status_counts()
    if status == "Error":
        st.error(message)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Not Started", status_counts.get("Not Started", 0))
    with col2:
        st.metric("In Progress", status_counts.get("In Progress", 0))
    with col3:
        st.metric("Completed", status_counts.get("Completed", 0))
    
    if status_counts.get("In Progress", 0) > 1:
        if st.button("Run Matching Algorithm", type="secondary", use_container_width=True):
            with st.spinner("Running matching algorithm..."):
                status, message = run_matching()
                if status == "Success":
                    st.toast(message, icon='✅')
                    st.balloons()
                    st.rerun()
                elif status == "Failed":
                    st.warning(message)
                elif status == "Error":
                    st.error(message)
    else:
        st.info("Students with 'In Progress' status not enough to run matching. Please ensure at least two students are in progress.")