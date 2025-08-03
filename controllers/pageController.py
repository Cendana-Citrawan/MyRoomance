import streamlit as st
from views.splashView import splash_page
from views.authenticationView import show_login_page, show_register_page
from views.admin.matchingView import show_run_matching_page
from views.admin.manageView import show_manage_questions_page
from views.admin.resultsView import show_view_results_page
from views.student.profileView import show_profile_page
from views.student.questionnaireView import show_questionnaire_page
from views.student.roommateView import show_view_roommate_page
from views.components.pageConfig import page_config, sidebar_config

def page_handler():
    page_config(sidebar="collapsed")
    if st.session_state.get('page') == 'login':
        show_login_page()
    elif st.session_state.get('page') == 'register':
        show_register_page()
    elif st.session_state.get('page') and st.session_state.get('user_id') and st.session_state.get('user_role'):
        page_config()
        sidebar_config()
        if st.session_state.get('user_role') == 'Admin':
            if st.session_state.get('page') == 'run_matching':
                show_run_matching_page()
            elif st.session_state.get('page') == 'manage_questions':
                show_manage_questions_page()
            elif st.session_state.get('page') == 'view_results':
                show_view_results_page()
        elif st.session_state.get('user_role') == 'Student':
            if st.session_state.get('page') == 'profile':
                show_profile_page()
            elif st.session_state.get('page') == 'questionnaire':
                show_questionnaire_page()
            elif st.session_state.get('page') == 'view_roommate':
                show_view_roommate_page()
    else:
        splash_page()