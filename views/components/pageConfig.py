import streamlit as st
from utils.helpers import load

def page_config(layout="wide", sidebar="expanded"):
    config_data = load("config.json")
    st.set_page_config(config_data['app']['appName'], config_data['app']['iconPath'], layout, sidebar)
    st.markdown(load(config_data['app']['stylesPath']), True)
    
def authentication_page():
    st.markdown("""
        <style>
        .stTextInput > div > div > button:focus svg {
            fill: var(--vibrant-blue);
            transform: scale(1.3);
            transition: transform 0.3s ease, fill 0.3s ease;
        }
        .stTextInput > div[data-testid="stTextInputRootElement"] {
            padding-right: unset;
            border: 2px solid var(--vibrant-blue) !important;
            border-radius: 0.75rem !important;
        }
        .stTextInput > div[data-testid="stTextInputRootElement"]:focus-within {
            box-shadow: 0 0 0 2px var(--vibrant-blue);
        }
        .stTextInput > div[data-testid="InputInstructions"] {
            display: none;
        }
        .stButton > button {
            background-color: var(--vibrant-blue);
            color: white;
            border: none;
            border-radius: 0.75rem;
            padding: 0.75rem 1.5rem;
            transition: background-color 0.3s ease;
        }
        .stButton > button > div > p {
            font-weight: 800;
        }
        .stButton > button:focus {
            box-shadow: 0 0 0 2px var(--vibrant-pink);
            background-color: var(--vibrant-pink);
        }
        .stButton > button:hover {
            box-shadow: 0 0 0 2px var(--vibrant-pink);
            background-color: var(--vibrant-pink);
        }
        </style>
    """, True)
    
def sidebar_config():
    with st.sidebar:
        st.image("assets/Logo.png", use_container_width=True)
        st.markdown("<h1 style='text-align: center; color: white; font-size: 2.5rem; font-family: var(--font-family-heading); margin-top: -50px;'>MyRoomance</h1>", unsafe_allow_html=True)
        
        if st.session_state.get('user_role') == 'Student':
            if st.session_state['page'] == 'profile':
                st.button("Complete Profile", 
                        on_click=lambda: st.session_state.__setitem__('page', 'profile'),
                        use_container_width=True, disabled=True)
            else:
                st.button("Complete Profile", 
                        on_click=lambda: st.session_state.__setitem__('page', 'profile'),
                        use_container_width=True)
            
            if st.session_state['page'] == 'questionnaire':
                st.button("Questionnaire", 
                        on_click=lambda: st.session_state.__setitem__('page', 'questionnaire'),
                        use_container_width=True, disabled=True)
            else:
                st.button("Questionnaire", 
                        on_click=lambda: st.session_state.__setitem__('page', 'questionnaire'),
                        use_container_width=True)
            
            if st.session_state['page'] == 'view_roommate':
                st.button("View Roommate", 
                        on_click=lambda: st.session_state.__setitem__('page', 'view_roommate'),
                        use_container_width=True, disabled=True)
            else:
                st.button("View Roommate", 
                        on_click=lambda: st.session_state.__setitem__('page', 'view_roommate'),
                        use_container_width=True)

        if st.session_state.get('user_role') == 'Admin':
            if st.session_state['page'] == 'run_matching':
                st.button("Run Matching", 
                        on_click=lambda: st.session_state.__setitem__('page', 'run_matching'),
                        use_container_width=True, disabled=True)
            else:
                st.button("Run Matching", 
                        on_click=lambda: st.session_state.__setitem__('page', 'run_matching'),
                        use_container_width=True)
                
            if st.session_state['page'] == 'manage_questions':
                st.button("Manage Questions", 
                        on_click=lambda: st.session_state.__setitem__('page', 'manage_questions'),
                        use_container_width=True, disabled=True)
            else:
                st.button("Manage Questions", 
                        on_click=lambda: st.session_state.__setitem__('page', 'manage_questions'),
                        use_container_width=True)
            
            if st.session_state['page'] == 'view_results':
                st.button("View Results", 
                        on_click=lambda: st.session_state.__setitem__('page', 'view_results'),
                        use_container_width=True, disabled=True)
            else:
                st.button("View Results", 
                        on_click=lambda: st.session_state.__setitem__('page', 'view_results'),
                        use_container_width=True)

        st.button("Logout", 
                on_click=lambda: (st.session_state.clear(), st.session_state.setdefault('page', 'login')),
                use_container_width=True)