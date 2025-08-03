import streamlit as st
import time
from models.profile import get_user_profile
from models.questionnaire import check_user_responses, show_user_responses, save_responses
from models.manage import get_questionnaire

def show_questionnaire_page():
    # Custom CSS for React-like styling
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
    .main-title {
        color: #5755fe;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #6b7280;
        font-size: 1.125rem;
        margin-bottom: 2rem;
    }
    .progress-container {
        background: white;
        border-radius: 1rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        border: 2px solid rgba(139, 147, 254, 0.2);
        margin-bottom: 1.5rem;
    }
    .question-card {
        background: white;
        border-radius: 1rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        padding: 2rem;
        border: 2px solid rgba(139, 147, 254, 0.2);
        margin-bottom: 1.5rem;
    }
    .question-number {
        background-color: #ff71cd;
        color: white;
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 1rem;
    }
    .category-badge {
        background-color: rgba(139, 147, 254, 0.2);
        color: #8b93fe;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-block;
        margin-left: 1rem;
    }
    .question-text {
        color: #1f2937;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 1rem 0;
    }
    .warning-container {
        background-color: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 0.75rem;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    .success-container {
        background-color: #d1fae5;
        border: 1px solid #10b981;
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
    }
    .stTextArea > div > div > textarea {
        border: 2px solid rgba(139, 147, 254, 0.4) !important;
        border-radius: 0.75rem !important;
        padding: 0.75rem 1rem !important;
        background-color: white !important;
    }
    .stRadio > div {
        background: white;
        border-radius: 0.5rem;
        padding: 1rem;
    }
    .stRadio > div > label > div {
        background-color: var(--vibrant-blue);
    }
    .stRadio > div > label > div:last-child {
        background-color: white;
    }
    .stRadio > div > label > div > div{
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Set background color
    st.markdown("""
    <style>
    .main .block-container {
        background: linear-gradient(135deg, #fff7fc 0%, rgba(139, 147, 254, 0.1) 100%);
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.markdown('<h1 class="main-title">Questionnaire </h1>', unsafe_allow_html=True)

    profile = get_user_profile(st.session_state.user_id)
    
    if not profile:
        st.error("Profile data is missing.")
        return
    
    # Check if profile is complete before allowing questionnaire
    if not profile['Name'] or not profile['Gender'] or not profile['Major'] or not profile['Hobby']:
        st.markdown("""
        <div class="warning-container">
            ⚠️ You must complete your profile before accessing the questionnaire.
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Go to Profile", help="Complete your profile first"):
            st.session_state.page = 'profile'
            st.rerun()
        return
    
    # Check if user has already completed the questionnaire
    has_completed = check_user_responses(profile['ProfileID'])
    
    if has_completed:
        st.markdown("""
        <div class="success-container">
            <h3 style="color: #059669;">✅ Questionnaire Completed!</h3>
            <p style="color: #065f46;">You have already completed the questionnaire! We'll notify you when matching is complete.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show previous responses button
        if st.button("View My Previous Answers", help="See your previous questionnaire responses"):
            show_user_responses(profile['ProfileID'])
    else:
        questions = get_questionnaire()
        if len(questions) != 15:
            st.info("The questionnaire is being prepared. Please check back later once it has been set by the Administrator.")
            return
            
        display_questionnaire_form_styled(profile, questions)
        
def display_questionnaire_form_styled(profile, questions):
    """Helper function to display the styled questionnaire form"""
    
    # # Progress indicator
    # total_questions = len(questions)
    # st.markdown(f"""
    # <div class="progress-container">
    #     <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
    #         <span style="color: #5755fe; font-weight: 600;">Progress</span>
    #         <span style="color: #5755fe; font-weight: 600;">0 of {total_questions}</span>
    #     </div>
    #     <div style="width: 100%; background-color: #e5e7eb; border-radius: 9999px; height: 0.75rem;">
    #         <div style="background-color: #8b93fe; height: 0.75rem; border-radius: 9999px; width: 0%; transition: width 0.3s;"></div>
    #     </div>
    # </div>
    # """, unsafe_allow_html=True)

    st.write("Please answer all questions honestly to help us find your best roommate match.")
    
    close_ended_questions = [q for q in questions if q['QuestionType'] != 'Open Ended']
    open_ended_questions = [q for q in questions if q['QuestionType'] == 'Open Ended']
    
    sorted_questions = close_ended_questions + open_ended_questions

    responses = {}
    with st.form("questionnaire_form"):
        for i, q in enumerate(sorted_questions, 1):
            q_id = q['QuestionID']
            q_text = q['QuestionText']
            q_type = q['QuestionType']
            q_category = q.get('Category', 'General')
            
            # Question card
            st.markdown(f"""
            <div class="question-card">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <span class="question-number">{i}</span>
                    <span class="category-badge">{q_category}</span>
                </div>
                <h3 class="question-text">{q_text}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if q_type == 'Open Ended':
                response = st.text_area("Your answer:", key=f"q_{q_id}", 
                                      placeholder="Type your answer here...",
                                      label_visibility="collapsed")
                responses[q_id] = response
            else:
                # Close Ended with options
                options = q['Options']
                option_texts = [opt['OptionText'] for opt in options]
                selected = st.radio("Choose your answer:", option_texts, 
                                  index=None, key=f"q_{q_id}",
                                  label_visibility="collapsed")
                
                # Find the selected option
                selected_option = next((opt for opt in options if opt['OptionText'] == selected), None)
                responses[q_id] = selected_option
            
            st.markdown("<br>", unsafe_allow_html=True)

        # Submit button with custom styling
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("Submit All Answers 🚀", 
                                            help="Submit your questionnaire responses", use_container_width=True,)

    if submitted:
        # Validate all answers are provided
        validation_error = False
        
        for q_id, response in responses.items():
            if response is None or (isinstance(response, str) and not response.strip()):
                q_text = next((q['QuestionText'] for q in questions if q['QuestionID'] == q_id), f"Question {q_id}")
                st.error(f"Please answer: {q_text}")
                validation_error = True
        
        if not validation_error:
            if save_responses(profile['ProfileID'], responses):
                st.markdown("""
                <div class="success-container">
                    <h2 style="color: #059669;"> Questionnaire Submitted Successfully!</h2>
                    <p style="color: #065f46;">Your answers have been saved! We'll notify you when matching is complete.</p>
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
                time.sleep(2)
                st.rerun()