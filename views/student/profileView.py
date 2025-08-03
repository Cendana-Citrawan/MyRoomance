import streamlit as st
import time
from models.profile import get_user_profile, update_profile

def show_profile_page():
    # Custom CSS for React-like styling
    st.title("Complete Your Profile")
    st.text("Please fill out your profile information to help us find the best roommate match for you.")
    
    st.markdown("""
    <style>
    .stForm button {
        background-color: var(--vibrant-blue);
        color: white;
    }
    .stForm button p{
        font-weight: bold;
    }
    .stForm button:hover p{
        color: var(--vibrant-blue);
    }
    .stForm button:hover {
        background-color: white;
        border: 2px solid var(--vibrant-blue);
    }
    [data-testid="stForm"] {
        background: white;
        border-radius: 1rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        padding: 2rem;
        border: 2px solid rgba(139, 147, 254, 0.2);
        margin-bottom: 2rem;
    }
    .form-container {
        background: white;
        border-radius: 1rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        padding: 2rem;
        border: 2px solid rgba(139, 147, 254, 0.2);
        margin-bottom: 2rem;
    }
    .form-label {
        color: #374151;
        display: block;
        font-weight: 700;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
    }
    .stSelectbox > div > div {
        border: 2px solid rgba(139, 147, 254, 0.4) !important;
        border-radius: 0.75rem !important;
        background-color: white !important;
    }
    .stTextInput > div > div > input {
        border: 2px solid rgba(139, 147, 254, 0.4) !important;
        border-radius: 0.75rem !important;
        padding: 0.75rem 1rem !important;
        background-color: white !important;
    }
    .stTextArea > div > div > textarea {
        border: 2px solid rgba(139, 147, 254, 0.4) !important;
        border-radius: 0.75rem !important;
        padding: 0.75rem 1rem !important;
        background-color: white !important;
    }
    .primary-button {
        background-color: #5755fe;
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .secondary-button {
        background-color: rgba(139, 147, 254, 0.2);
        color: #8b93fe;
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .warning-box {
        background-color: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    input[type="text"],
    textarea {
        border: 2px solid rgba(139, 147, 254, 0.4) !important;
        border-radius: 0.75rem !important;
        background-color: white !important;
        padding: 0.75rem 1rem !important;
        font-family: inherit;
    }
    </style>
    """, unsafe_allow_html=True)
    
    
    # Get current profile
    profile = get_user_profile(st.session_state.user_id)
    if not profile:
        st.error("Unable to load profile")
        return

    # Gender options
    gender_options = ['', 'Female', 'Male']
    gender_index = gender_options.index(profile['Gender']) if profile['Gender'] in gender_options else 0

    # Major options
    majors = [
        '', 'Accounting', 'Actuarial Science', 'Agribusiness', 'Business Administration',
        'Management', 'Architecture', 'Civil Engineering', 'Electrical Engineering', 
        'Environmental Engineering', 'Industrial Engineering', 'Mechanical Engineering',
        'Communication', 'International Relations', 'Primary School Teacher Education',
        'Law', 'Information Technology', 'Information Systems', 'Interior Design',
        'Visual Communication Design'
    ]
    major_index = majors.index(profile['Major']) if profile['Major'] in majors else 0

    # Form container
    
    with st.form("profile_form"):
        # Create two columns for form layout
        # No columns, just vertical layout
        st.markdown('<label class="form-label">Full Name</label>', unsafe_allow_html=True)
        name = st.text_input("", value=profile['Name'] if profile['Name'] else "", 
                            placeholder="Enter your full name", label_visibility="collapsed")

        st.markdown('<label class="form-label">Gender</label>', unsafe_allow_html=True)
        gender = st.selectbox("", gender_options, index=gender_index, label_visibility="collapsed")

        st.markdown('<label class="form-label">Major</label>', unsafe_allow_html=True)
        major = st.selectbox("", majors, index=major_index, label_visibility="collapsed")

        st.markdown('<label class="form-label">Phone Number</label>', unsafe_allow_html=True)
        phone = st.text_input("", value=profile['Phone'] if profile['Phone'] else "", 
                            placeholder="Enter phone number (digits only)", label_visibility="collapsed")

        st.markdown('<label class="form-label">Hobbies</label>', unsafe_allow_html=True)
        hobby = st.text_area("", value=profile['Hobby'] if profile['Hobby'] else "", 
                            placeholder="Tell us about your hobbies and interests", height=100, 
                            label_visibility="collapsed")

        
        # Action buttons
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            submitted = st.form_submit_button("Save Profile", help="Save your profile information", use_container_width=True)
        
        if submitted:
            # Validation
            validation_error = False
            
            if not name:
                st.error("Please enter your name")
                validation_error = True

            if not gender or gender == '':
                st.error("Please select your gender")
                validation_error = True

            if not major or major == '':
                st.error("Please select your major")
                validation_error = True

            if phone and not phone.isdigit():
                st.error("Phone number should contain only digits")
                validation_error = True

            if not hobby:
                st.error("Please enter your hobbies")
                validation_error = True

            # Save profile if valid
            if not validation_error:
                if update_profile(profile['ProfileID'], st.session_state.user_id, name, gender, major, phone, hobby, None):
                    st.success("Profile updated successfully!")
                    time.sleep(2)
                    st.session_state['page'] = 'questionnaire'
                    st.rerun()