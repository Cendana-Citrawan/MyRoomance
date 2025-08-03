import streamlit as st
from mysql.connector import Error
from datetime import datetime
from models.connection import get_connection

def get_questionnaire():
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT q.QuestionID, q.QuestionText, q.QuestionType, q.Category, q.Weight,
                   o.OptionID, o.OptionText, o.OptionValue, o.OptionOrder
            FROM Questionnaire q
            LEFT JOIN QuestionnaireOption o ON q.QuestionID = o.QuestionID
            ORDER BY q.Category, q.QuestionID, o.OptionOrder
        """)
        
        result = cursor.fetchall()
        
        # Group options by question
        questions = {}
        for row in result:
            q_id = row['QuestionID']
            if q_id not in questions:
                questions[q_id] = {
                    'QuestionID': q_id,
                    'QuestionText': row['QuestionText'],
                    'QuestionType': row['QuestionType'],
                    'Category': row['Category'],
                    'Weight': row['Weight'],
                    'Options': []
                }
            
            if row['OptionText']:  # Add option if it exists
                questions[q_id]['Options'].append({
                    'OptionID': row['OptionID'],
                    'OptionText': row['OptionText'],
                    'OptionValue': row['OptionValue'],
                    'OptionOrder': row['OptionOrder']
                })
        
        return list(questions.values())
    except Error as e:
        st.error(f"Error retrieving questionnaire: {e}")
        return []
    finally:
        cursor.close()
        
def get_close_ended_count_by_category(category):
    """Get count of Close Ended questions in a specific category"""
    conn = get_connection()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM Questionnaire WHERE Category = %s AND QuestionType = 'Close Ended'",
            (category,)
        )
        result = cursor.fetchone()
        return result[0] if result else 0
    except Error as e:
        st.error(f"Error checking category count: {e}")
        return 0
    finally:
        cursor.close()
        
def get_open_ended_count_by_category(category):
    """Get count of Open Ended questions in a specific category"""
    conn = get_connection()
    if not conn:
        return 0

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM Questionnaire WHERE Category = %s AND QuestionType = 'Open Ended'",
            (category,)
        )
        result = cursor.fetchone()
        return result[0] if result else 0
    except Error as e:
        st.error(f"Error checking category count: {e}")
        return 0
    finally:
        cursor.close()

def add_question(question_text, question_type, category, weight, options=None):
    conn = get_connection()
    if not conn:
        st.error("❌ Database connection failed!")
        return False
    
    try:
        cursor = conn.cursor()
        # Add the question
        cursor.execute(
            "INSERT INTO Questionnaire (QuestionText, QuestionType, Category, Weight) VALUES (%s, %s, %s, %s)",
            (question_text, question_type, category, weight)
        )
        question_id = cursor.lastrowid
        
        # Add options if it's a closed question
        if question_type == 'Close Ended' and options:
            for i, option in enumerate(options):
                cursor.execute(
                    """INSERT INTO QuestionnaireOption 
                       (QuestionID, OptionText, OptionOrder, OptionValue) 
                       VALUES (%s, %s, %s, %s)""",
                    (question_id, option['text'], i+1, option['value'])
                )
        
        conn.commit()
        return True
    except Error as e:
        conn.rollback()
        st.error(f"❌ Error adding question: {e}")
        return False
    finally:
        cursor.close()

def update_question(question_id, question_text, category, weight):
    conn = get_connection()
    if not conn:
        st.error("❌ Database connection failed!")
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE Questionnaire 
               SET QuestionText = %s, Category = %s, Weight = %s
               WHERE QuestionID = %s""",
            (question_text, category, weight, question_id)
        )
        conn.commit()
        return True
    except Error as e:
        conn.rollback()
        st.error(f"❌ Error updating question: {e}")
        return False
    finally:
        cursor.close()

def update_option(option_id, option_text, option_value):
    conn = get_connection()
    if not conn:
        st.error("❌ Database connection failed!")
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE QuestionnaireOption 
               SET OptionText = %s, OptionValue = %s
               WHERE OptionID = %s""",
            (option_text, option_value, option_id)
        )
        conn.commit()
        return True
    except Error as e:
        conn.rollback()
        st.error(f"❌ Error updating option: {e}")
        return False
    finally:
        cursor.close()

def add_option(question_id, option_text, option_value, option_order):
    conn = get_connection()
    if not conn:
        st.error("❌ Database connection failed!")
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO QuestionnaireOption 
               (QuestionID, OptionText, OptionOrder, OptionValue) 
               VALUES (%s, %s, %s, %s)""",
            (question_id, option_text, option_order, option_value)
        )
        conn.commit()
        return True
    except Error as e:
        conn.rollback()
        st.error(f"❌ Error adding option: {e}")
        return False
    finally:
        cursor.close()

def delete_option(option_id):
    conn = get_connection()
    if not conn:
        st.error("❌ Database connection failed!")
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM QuestionnaireOption WHERE OptionID = %s",
            (option_id,)
        )
        conn.commit()
        return True
    except Error as e:
        conn.rollback()
        st.error(f"❌ Error deleting option: {e}")
        return False
    finally:
        cursor.close()

def delete_question(question_id):
    conn = get_connection()
    if not conn:
        st.error("❌ Database connection failed!")
        return False
    
    try:
        cursor = conn.cursor()
        # First delete options
        cursor.execute(
            "DELETE FROM QuestionnaireOption WHERE QuestionID = %s",
            (question_id,)
        )
        
        # Then delete responses
        cursor.execute(
            "DELETE FROM Response WHERE QuestionID = %s",
            (question_id,)
        )
        
        # Finally delete the question
        cursor.execute(
            "DELETE FROM Questionnaire WHERE QuestionID = %s",
            (question_id,)
        )
        
        conn.commit()
        return True
    except Error as e:
        conn.rollback()
        st.error(f"❌ Error deleting question: {e}")
        return False
    finally:
        cursor.close()
        
def log_import_start(importing_name, total_records):
    """Log the start of an import operation"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO importingjob (ImportingName, Activity, Success, Error, TotalProcessed, RunningTime, Date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        start_time = datetime.now()
        values = (
            importing_name,
            'Create',  # Activity type
            0,         # Success count (will be updated later)
            0,         # Error count (will be updated later)
            total_records,  # Total records to process
            0.0,       # Running time (will be calculated later)
            start_time
        )
        
        cursor.execute(query, values)
        conn.commit()
        
        # Get the auto-generated ImportingJobID
        import_job_id = cursor.lastrowid
        
        # Store start time in session state for later calculation
        st.session_state[f'import_start_time_{import_job_id}'] = start_time
        
        return import_job_id
        
    except Error as e:
        st.error(f"Failed to log import start: {e}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def log_import_completion(import_job_id, success_count, error_count):
    """Update the import log with completion details"""
    if not import_job_id:
        return False
    
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Calculate running time
        start_time_key = f'import_start_time_{import_job_id}'
        if start_time_key in st.session_state:
            start_time = st.session_state[start_time_key]
            running_time = (datetime.now() - start_time).total_seconds()
            # Clean up session state
            del st.session_state[start_time_key]
        else:
            running_time = 0.0
        
        # Update the record with completion details
        query = """
        UPDATE importingjob 
        SET Success = %s, Error = %s, RunningTime = %s, Activity = %s
        WHERE ImportingJobID = %s
        """
        
        activity = 'Update'  # Since we're updating existing questions
        values = (success_count, error_count, running_time, activity, import_job_id)
        
        cursor.execute(query, values)
        conn.commit()
        
        return cursor.rowcount > 0
        
    except Error as e:
        st.error(f"Failed to log import completion: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()