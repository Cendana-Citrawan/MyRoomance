import streamlit as st
from mysql.connector import Error
from models.connection import get_connection

def check_user_responses(profile_id):
    """Check if user has already submitted responses"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM Response
            WHERE ProfileID = %s
        """, (profile_id,))
        
        count = cursor.fetchone()[0]
        return count > 0
    except Error as e:
        st.error(f"Error checking responses: {e}")
        return False
    finally:
        cursor.close()

def check_user_responses(profile_id):
    """Check if user has already submitted responses"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM Response
            WHERE ProfileID = %s
        """, (profile_id,))
        
        count = cursor.fetchone()[0]
        return count > 0
    except Error as e:
        st.error(f"Error checking responses: {e}")
        return False
    finally:
        cursor.close()

def show_user_responses(profile_id):
    """Show user's previous responses with styling"""
    st.markdown("""
    <style>
    .response-card {
        background: white;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #5755fe;
    }
    .question-text {
        color: #1f2937;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .answer-text {
        color: #4b5563;
        background-color: #f9fafb;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border-left: 3px solid #8b93fe;
    }
    </style>
    """, unsafe_allow_html=True)
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT q.QuestionText, q.QuestionType, 
                   r.ResponseOption, r.ResponseText
            FROM Response r
            JOIN Questionnaire q ON r.QuestionID = q.QuestionID
            WHERE r.ProfileID = %s
        """, (profile_id,))
        
        responses = cursor.fetchall()
        
        if not responses:
            st.info("No responses found.")
            return
        
        st.markdown("### Your Previous Answers")
        
        for i, resp in enumerate(responses, 1):
            q_text = resp['QuestionText']
            if resp['QuestionType'] == 'Open Ended':
                answer = resp['ResponseText']
            else:
                answer = resp['ResponseOption']
                
            st.markdown(f"""
            <div class="response-card">
                <div class="question-text">Q{i}: {q_text}</div>
                <div class="answer-text">💬 {answer}</div>
            </div>
            """, unsafe_allow_html=True)
            
    except Error as e:
        st.error(f"Error retrieving responses: {e}")
    finally:
        cursor.close()
        
def save_responses(profile_id, responses):
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        # First delete any existing responses for this profile
        cursor.execute(
            "DELETE FROM Response WHERE ProfileID = %s",
            (profile_id,)
        )
        
        # Insert new responses
        for question_id, response in responses.items():
            if isinstance(response, dict):
                # For close-ended questions with option selection
                cursor.execute(
                    """INSERT INTO Response 
                       (QuestionID, ProfileID, ResponseOption) 
                       VALUES (%s, %s, %s)""",
                    (question_id, profile_id, response.get('OptionText', ''))
                )
            else:
                # For open-ended questions with text
                cursor.execute(
                    """INSERT INTO Response 
                       (QuestionID, ProfileID, ResponseText) 
                       VALUES (%s, %s, %s)""",
                    (question_id, profile_id, response)
                )
        
        # Update matching status to in progress
        cursor.execute(
            """UPDATE Profile 
               SET MatchingStatus = 'In Progress'
               WHERE ProfileID = %s""",
            (profile_id,)
        )
        
        conn.commit()
        return True
    except Error as e:
        conn.rollback()
        st.error(f"Error saving responses: {e}")
        return False
    finally:
        cursor.close()