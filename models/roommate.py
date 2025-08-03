import streamlit as st
from mysql.connector import Error
from models.connection import get_connection

def get_roommate(profile_id):
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.MatchID, m.MatchScore, m.MatchCategory,
                   p1.Name as Profile1Name, p1.ProfileID as Profile1ID,
                   p2.Name as Profile2Name, p2.ProfileID as Profile2ID
            FROM `Match` m
            JOIN Profile p1 ON m.ProfileID1 = p1.ProfileID
            JOIN Profile p2 ON m.ProfileID2 = p2.ProfileID
            WHERE m.ProfileID1 = %s OR m.ProfileID2 = %s
            ORDER BY m.MatchingJobID DESC
            LIMIT 1
        """, (profile_id, profile_id))
        
        match = cursor.fetchone()
        if not match:
            return None
            
        # Determine which profile is the roommate
        if match['Profile1ID'] == profile_id:
            roommate = {
                'Name': match['Profile2Name'],
                'ProfileID': match['Profile2ID']
            }
        else:
            roommate = {
                'Name': match['Profile1Name'],
                'ProfileID': match['Profile1ID']
            }
        
        roommate.update({
            'MatchScore': match['MatchScore'],
            'MatchCategory': match['MatchCategory']
        })
        
        return roommate
    except Error as e:
        st.error(f"Error retrieving roommate: {e}")
        return None
    finally:
        cursor.close()

def get_user_profile_by_id(profile_id):
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM Profile WHERE ProfileID = %s",
            (profile_id,)
        )
        return cursor.fetchone()
    except Error as e:
        st.error(f"Error retrieving profile: {e}")
        return None
    finally:
        cursor.close()

def get_actual_compatibility_by_category(profile_id, roommate_id):
    """
    Get actual compatibility data by category based on questionnaire responses
    """
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Get all question categories
        cursor.execute("SELECT DISTINCT Category FROM Questionnaire")
        categories = [row['Category'] for row in cursor.fetchall()]
        
        compatibility_data = []
        
        # For each category, calculate compatibility
        for category in categories:
            # Get your responses by category
            cursor.execute("""
                SELECT r.QuestionID, r.ResponseOption, qo.OptionValue, q.Weight
                FROM Response r
                JOIN Questionnaire q ON r.QuestionID = q.QuestionID
                LEFT JOIN QuestionnaireOption qo ON q.QuestionID = qo.QuestionID AND r.ResponseOption = qo.OptionText
                WHERE r.ProfileID = %s AND q.Category = %s AND q.QuestionType = 'Close Ended'
            """, (profile_id, category))
            
            your_responses = cursor.fetchall()
            
            # Get roommate's responses by category
            cursor.execute("""
                SELECT r.QuestionID, r.ResponseOption, qo.OptionValue, q.Weight
                FROM Response r
                JOIN Questionnaire q ON r.QuestionID = q.QuestionID
                LEFT JOIN QuestionnaireOption qo ON q.QuestionID = qo.QuestionID AND r.ResponseOption = qo.OptionText
                WHERE r.ProfileID = %s AND q.Category = %s AND q.QuestionType = 'Close Ended'
            """, (roommate_id, category))
            
            roommate_responses = cursor.fetchall()
            
            # Convert to dictionaries for easier comparison
            your_resp_dict = {r['QuestionID']: {'value': float(r['OptionValue']) if r['OptionValue'] else 0.5, 'weight': r['Weight']} for r in your_responses}
            roommate_resp_dict = {r['QuestionID']: {'value': float(r['OptionValue']) if r['OptionValue'] else 0.5, 'weight': r['Weight']} for r in roommate_responses}
            
            # Calculate average scores for radar chart
            your_score = sum(item['value'] for item in your_resp_dict.values()) / len(your_resp_dict) if your_resp_dict else 0.5
            roommate_score = sum(item['value'] for item in roommate_resp_dict.values()) / len(roommate_resp_dict) if roommate_resp_dict else 0.5
            
            # Calculate compatibility for this category
            total_weight = 0
            weighted_similarity = 0
            
            for q_id in set(your_resp_dict.keys()) & set(roommate_resp_dict.keys()):
                your_val = your_resp_dict[q_id]['value']
                roommate_val = roommate_resp_dict[q_id]['value']
                weight = your_resp_dict[q_id]['weight']
                
                # Calculate similarity (1 - normalized difference)
                similarity = 1 - abs(your_val - roommate_val)
                
                weighted_similarity += similarity * weight
                total_weight += weight
            
            # Calculate overall compatibility for this category
            compatibility = weighted_similarity / total_weight if total_weight > 0 else 0
            
            compatibility_data.append({
                'Category': category,
                'Your_Score': your_score,
                'Roommate_Score': roommate_score,
                'Compatibility': compatibility
            })
        
        return compatibility_data
    except Error as e:
        st.error(f"Error calculating compatibility: {e}")
        return None
    finally:
        cursor.close()