import streamlit as st
import pandas as pd
import io
from datetime import datetime
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from models.results import get_matching_jobs, get_matching_results


def show_view_results_page():
    st.title(" Matching Results")
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
    
    # Show list of matching jobs
    jobs = get_matching_jobs()
    
    if not jobs:
        st.info("No matching jobs have been run yet.")
        return
    
    # Select job to view
    job_options = ["Latest Job"] + [f"Job {job['MatchingJobID']} - {job['Date']}" for job in jobs]
    selected_job = st.selectbox("Select Matching Job", job_options)
    
    # Get job results
    if selected_job == "Latest Job":
        results = get_matching_results()
    else:
        job_id = int(selected_job.split(" ")[1])
        results = get_matching_results(job_id)
    
    if not results:
        st.info("No matches found for this job.")
        return
    
    # Display results
    st.markdown("### Roommate Pairs")
    
    categories = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
    for match in results:
        categories[match['MatchCategory']] += 1

    category_colors = {
        'A': '#4ade80',  # green
        'B': '#60a5fa',  # blue
        'C': '#facc15',  # yellow
        'D': '#f97316',  # orange
        'E': '#ef4444',  # red
    }

    cols = st.columns(5)
    for i, (cat, count) in enumerate(categories.items()):
        with cols[i]:
            st.markdown(
                f"""
                <div style='
                    background-color: {category_colors[cat]}20;
                    padding: 1rem;
                    border-radius: 12px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
                    text-align: center;
                '>
                    <div style='font-size: 18px; font-weight: 600; color: {category_colors[cat]};'>
                        Category {cat}
                    </div>
                    <div style='font-size: 28px; font-weight: bold; color: #111;'>
                        {count}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Create dataframe for easier display
    results_df = pd.DataFrame([
        {
            "Match ID": match['MatchID'],
            "Student 1": match['Profile1Name'],
            "Major 1": match['Profile1Major'],
            "Student 2": match['Profile2Name'],
            "Major 2": match['Profile2Major'],
            "Score": f"{match['MatchScore']}%",
            "Category": match['MatchCategory']
        }
        for match in results
    ])
    
    st.dataframe(results_df, use_container_width=True, hide_index=True)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Matching Results"

    for r in dataframe_to_rows(results_df, index=False, header=True):
        ws.append(r)

    excel_buffer = io.BytesIO()
    wb.save(excel_buffer)
    excel_buffer.seek(0)

    st.download_button(
        label="Export Result as Excel",
        data=excel_buffer,
        file_name=f"roommate_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )