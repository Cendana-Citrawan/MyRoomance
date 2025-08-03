import streamlit as st
from mysql.connector import Error
from .connection import get_connection

def get_user_profile(user_id):
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM Profile WHERE UserID = %s",
            (user_id,)
        )
        return cursor.fetchone()
    except Error as e:
        st.error(f"Error retrieving profile: {e}")
        return None
    finally:
        cursor.close()

def update_profile(profile_id, user_id, name, gender, major, phone=None, hobby=None, image=None):
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE Profile 
               SET Name = %s, Gender = %s, Major = %s, Phone = %s, Hobby = %s, 
                   Image = %s, ProfileStatus = 'Completed'
               WHERE UserID = %s AND ProfileID = %s""",
            (name, gender, major, phone, hobby, image, user_id, profile_id)
        )
        conn.commit()
        return True
    except Error as e:
        conn.rollback()
        st.error(f"Error updating profile: {e}")
        return False
    finally:
        cursor.close()