import streamlit as st
from models.connection import get_connection
from mysql.connector import Error

def get_matching_jobs():
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM MatchingJob
            ORDER BY Date DESC
        """)
        return cursor.fetchall()
    except Error as e:
        st.error(f"Error retrieving matching jobs: {e}")
        return []
    finally:
        cursor.close()

def get_matching_results(job_id=None):
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        if job_id:
            query = """
                SELECT m.MatchID, m.MatchScore, m.MatchCategory,
                       p1.Name as Profile1Name, p1.Major as Profile1Major,
                       p2.Name as Profile2Name, p2.Major as Profile2Major
                FROM `Match` m
                JOIN Profile p1 ON m.ProfileID1 = p1.ProfileID
                JOIN Profile p2 ON m.ProfileID2 = p2.ProfileID
                WHERE m.MatchingJobID = %s
                ORDER BY m.MatchScore DESC
            """
            cursor.execute(query, (job_id,))
        else:
            query = """
                SELECT m.MatchID, m.MatchScore, m.MatchCategory,
                       p1.Name as Profile1Name, p1.Major as Profile1Major,
                       p2.Name as Profile2Name, p2.Major as Profile2Major
                FROM `Match` m
                JOIN Profile p1 ON m.ProfileID1 = p1.ProfileID
                JOIN Profile p2 ON m.ProfileID2 = p2.ProfileID
                JOIN (
                    SELECT MAX(MatchingJobID) as latest_job
                    FROM MatchingJob
                ) lj ON m.MatchingJobID = lj.latest_job
                ORDER BY m.MatchScore DESC
            """
            cursor.execute(query)
            
        return cursor.fetchall()
    except Error as e:
        st.error(f"Error retrieving matching results: {e}")
        return []
    finally:
        cursor.close()