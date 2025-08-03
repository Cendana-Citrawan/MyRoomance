import streamlit as st
import time
import numpy as np
import re
import tensorflow_hub as hub
from sklearn.metrics.pairwise import cosine_similarity
from models.connection import get_connection
from datetime import datetime
from scipy.spatial.distance import euclidean

def get_matching_status_counts():
    conn = get_connection()
    if not conn:
        return "Error", "Database connection failed.", None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MatchingStatus, COUNT(*) as Count
            FROM Profile
            WHERE ProfileStatus = 'Completed'
            GROUP BY MatchingStatus
        """)
        
        results = cursor.fetchall()
        status_counts = {status: count for status, count in results}
        
        return None, None, status_counts

    except:
        return "Error", "Failed to retrieve matching status counts.", None
    finally:
        cursor.close()
        
def get_profile_responses():
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.ProfileID, p.Name, p.Gender, p.Major, 
                   r.QuestionID, r.ResponseOption, r.ResponseText,
                   q.QuestionType, qo.OptionValue
            FROM Profile p
            JOIN Response r ON p.ProfileID = r.ProfileID
            JOIN Questionnaire q ON r.QuestionID = q.QuestionID
            LEFT JOIN QuestionnaireOption qo ON q.QuestionID = qo.QuestionID AND r.ResponseOption = qo.OptionText
            WHERE p.ProfileStatus = 'Completed' AND p.MatchingStatus = 'In Progress'
        """)
        
        return cursor.fetchall()
    except:
        return None
    finally:
        cursor.close()
        
# def calculate_match_score(profile1_responses, profile2_responses):
#     all_questions = set(profile1_responses) | set(profile2_responses)
    
#     # Early exit if all answers are identical or all differ
#     if all(profile1_responses.get(q, {}).get('value', 0) == profile2_responses.get(q, {}).get('value', 0) for q in all_questions):
#         return 100, 'A'
#     if all(profile1_responses.get(q, {}).get('value', 0) != profile2_responses.get(q, {}).get('value', 0) for q in all_questions):
#         return 0, 'E'
    
#     # Extract values and weights
#     values1 = np.array([profile1_responses.get(q, {}).get('value', 0) for q in all_questions])
#     values2 = np.array([profile2_responses.get(q, {}).get('value', 0) for q in all_questions])
#     weights = np.array([profile1_responses.get(q, {}).get('weight', 1) for q in all_questions])

#     # Euclidean Distance Calculation
#     euclidean_dist = euclidean(values1, values2)
#     max_possible_distance = np.sqrt(len(all_questions))
#     euclidean_score = int((1 - euclidean_dist / max_possible_distance) * 100)

#     # Calculate weighted similarity score
#     similarity = 1 - np.abs(values1 - values2)
#     weighted_score = int(np.sum(similarity * weights) / np.sum(weights) * 100)
    
#     final_score = int((euclidean_score + weighted_score) / 2)

#     # Categorize match score based on final score
#     category = 'A' if final_score >= 90 else 'B' if final_score >= 75 else 'C' if final_score >= 60 else 'D' if final_score >= 45 else 'E'
    
#     return final_score, category

# @st.cache_resource
# def get_use_model():
#     try:
#         model = tf.saved_model.load("models/USE")
#         return model
#     except Exception as e:
#         print(f"Error loading USE model: {e}")
#         return None

@st.cache_resource
def get_use_model():
    try:
        model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
        return model
    except Exception as e:
        st.error(f"Error loading USE model: {e}")
        return None

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text

def calculate_match_score(profile1, profile2, use_model):
    all_q_ids = set(profile1.keys()) | set(profile2.keys())

    close_values1, close_values2, close_weights = [], [], []

    for q_id in all_q_ids:
        if profile1.get(q_id, {}).get("type") == "Close Ended":
            v1 = profile1.get(q_id, {}).get("value", 0.0)
            v2 = profile2.get(q_id, {}).get("value", 0.0)
            w = profile1.get(q_id, {}).get("weight", 1)
            close_values1.append(v1)
            close_values2.append(v2)
            close_weights.append(w)

    if close_values1:
        values1 = np.array(close_values1)
        values2 = np.array(close_values2)
        weights = np.array(close_weights)

        if np.array_equal(values1, values2):
            close_score = 100.0
        else:
            eu_dist = euclidean(values1, values2)
            max_dist = np.sqrt(len(close_values1))
            eu_score = (1 - eu_dist / max_dist) * 100

            similarity = 1 - np.abs(values1 - values2)
            weighted_score = np.sum(similarity * weights) / np.sum(weights) * 100

            close_score = (eu_score + weighted_score) / 2
    else:
        close_score = 0

    texts1, texts2, weights = [], [], []

    for q_id in profile1:
        if profile1[q_id].get("type") == "Open Ended" and profile2.get(q_id):
            t1 = clean_text(profile1[q_id].get("text", ""))
            t2 = clean_text(profile2[q_id].get("text", ""))
            if t1 and t2:
                texts1.append(t1)
                texts2.append(t2)
                weights.append(profile1[q_id].get("weight", 1))

    if not texts1:
        return 0.0

    embeddings1 = use_model(texts1).numpy()
    embeddings2 = use_model(texts2).numpy()

    sims = [
        cosine_similarity([e1], [e2])[0][0] * w
        for e1, e2, w in zip(embeddings1, embeddings2, weights)
    ]

    open_score = sum(sims) / sum(weights) * 100

    if close_values1 and open_score:
        final_score = (int(close_score) + int(open_score)) / 2
    elif close_values1:
        final_score = close_score
    else:
        final_score = open_score

    category = (
        "A" if final_score >= 90 else
        "B" if final_score >= 75 else
        "C" if final_score >= 60 else
        "D" if final_score >= 45 else
        "E"
    )

    return int(final_score), category

def run_matching():
    use_model = get_use_model()
    if use_model is None:
        return "Error", "Failed to load the USE model."
    conn = get_connection()
    if not conn:
        return "Error", "Database connection failed."
    
    start_time = time.time()
    
    try:
        # Get all profile responses
        responses_data = get_profile_responses()
        if not responses_data:
            return "Error", "An error occurred while running the matching algorithm."

        # Create a job record
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO MatchingJob 
               (MatchingName, Success, Error, TotalProcessed, RunningTime, Date) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (f"AI Matching Job {datetime.now()}", 0, 0, 0, 0.0, datetime.now())
        )
        job_id = cursor.lastrowid
        
        # Organize responses by profile
        profiles = {}
        question_weights = {}
        
        for row in responses_data:
            profile_id = row['ProfileID']
            
            if profile_id not in profiles:
                profiles[profile_id] = {
                    'ProfileID': profile_id,
                    'Name': row['Name'],
                    'Gender': row['Gender'],
                    'Major': row['Major'],
                    'Responses': {}
                }
            
            q_id = row['QuestionID']
            
            # Store question weight
            if q_id not in question_weights:
                query = "SELECT Weight FROM Questionnaire WHERE QuestionID = %s"
                cursor.execute(query, (q_id,))
                weight_result = cursor.fetchone()
                question_weights[q_id] = weight_result[0] if weight_result else 1
            
            response_value = 0.0
            
            if row['QuestionType'] == 'Close Ended' and row['OptionValue'] is not None:
                response_value = float(row['OptionValue'])
            
            profiles[profile_id]['Responses'][q_id] = {
                'value': response_value,
                'type': row['QuestionType'],
                'text': row['ResponseText'] if row['ResponseText'] else row['ResponseOption'],
                'weight': question_weights[q_id]
            }
        
        # Match profiles based on gender and compatibility
        profile_ids = list(profiles.keys())
        matches = []
        errors = 0
        success = 0
        
        # Group by gender
        males = [p_id for p_id in profile_ids if profiles[p_id]['Gender'] == 'Male']
        females = [p_id for p_id in profile_ids if profiles[p_id]['Gender'] == 'Female']

        # Check if either group has odd number of profiles
        if len(males) % 2 != 0 or len(females) % 2 != 0:
            return "Failed", "Make sure the number of students aren't odd."
        
        # Process each gender group separately to ensure everyone gets matched
        for gender_group in [males, females]:
            if len(gender_group) < 2:
                continue  # Skip if not enough profiles in this gender
            
            # Create all possible pairings and calculate match scores
            pair_scores = []
            
            for i in range(len(gender_group)):
                for j in range(i+1, len(gender_group)):
                    profile1_id = gender_group[i]
                    profile2_id = gender_group[j]
                    
                    score, category = calculate_match_score(
                        profiles[profile1_id]['Responses'],
                        profiles[profile2_id]['Responses'],
                        use_model
                    )
                    
                    pair_scores.append({
                        'profile1': profile1_id,
                        'profile2': profile2_id,
                        'score': score,
                        'category': category
                    })
            
            # Sort pairs by score (highest first)
            pair_scores.sort(key=lambda x: x['score'], reverse=True)
            
            # Assign pairs using greedy algorithm to maximize overall compatibility
            matched_profiles = set()
            
            for pair in pair_scores:
                profile1_id = pair['profile1']
                profile2_id = pair['profile2']
                
                # If neither profile has been matched yet
                if profile1_id not in matched_profiles and profile2_id not in matched_profiles:
                    matches.append(pair)
                    matched_profiles.add(profile1_id)
                    matched_profiles.add(profile2_id)
                    success += 1
            
            # Check for any unmatched profiles (this should not happen with even numbers, but just in case)
            unmatched = [p_id for p_id in gender_group if p_id not in matched_profiles]
            
            # If there are exactly 2 unmatched profiles, match them together
            if len(unmatched) == 2:
                profile1_id = unmatched[0]
                profile2_id = unmatched[1]
                
                score, category = calculate_match_score(
                    profiles[profile1_id]['Responses'],
                    profiles[profile2_id]['Responses']
                )
                
                matches.append({
                    'profile1': profile1_id,
                    'profile2': profile2_id,
                    'score': score,
                    'category': category
                })
                success += 1
            elif len(unmatched) > 0:
                errors += len(unmatched)
        
        # Save matches to database
        for match in matches:
            cursor.execute(
                """INSERT INTO `Match` 
                   (MatchingJobID, ProfileID1, ProfileID2, MatchScore, MatchCategory) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (job_id, match['profile1'], match['profile2'], match['score'], match['category'])
            )
            
            # Update profiles' matching status
            cursor.execute(
                """UPDATE Profile 
                   SET MatchingStatus = 'Completed'
                   WHERE ProfileID = %s OR ProfileID = %s""",
                (match['profile1'], match['profile2'])
            )
        
        # Update job stats
        elapsed_time = time.time() - start_time
        cursor.execute(
            """UPDATE MatchingJob 
               SET Success = %s, Error = %s, TotalProcessed = %s, RunningTime = %s, 
                   MatchingName = %s
               WHERE MatchingJobID = %s""",
            (success, errors, success + errors, elapsed_time, 
             f"AI Matching Job {datetime.now()}", job_id)
        )
        
        conn.commit()
        return "Success", "Matching algorithm completed successfully."
    except:
        conn.rollback()
        return "Error", "An error occurred while running the matching algorithm."
    finally:
        cursor.close()