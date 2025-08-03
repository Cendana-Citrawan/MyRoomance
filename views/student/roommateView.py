import streamlit as st
import plotly.graph_objects as go
from models.roommate import get_actual_compatibility_by_category, get_user_profile_by_id, get_roommate
from models.profile import get_user_profile

def show_view_roommate_page():
    # Custom CSS for React-like styling
    st.markdown("""
    <style>
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
    .roommate-card {
        display: flex;
        flex-direction: column;
        overflow: auto;
        max-width: 100%;
        background: white;
        border-radius: 1rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        padding: 2rem;
        border: 2px solid rgba(139, 147, 254, 0.2);
        margin-bottom: 2rem;
    }
    .profile-section {
        text-align: center;
        padding: 1rem;
    }
    .profile-avatar {
        width: 8rem;
        height: 8rem;
        border-radius: 50%;
        background: rgba(255, 113, 205, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem auto;
        font-size: 4rem;
    }
    .roommate-name {
        color: #5755fe;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .roommate-major {
        color: #6b7280;
        margin-bottom: 1rem;
    }
    .match-score-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    .match-score {
        color: #ff71cd;
        font-weight: bold;
        font-size: 1.25rem;
    }
    .match-category {
        background-color: #5755fe;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-weight: 600;
        display: inline-block;
    }
    .info-section {
        background: rgba(139, 147, 254, 0.05);
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .info-title {
        color: #5755fe;
        font-size: 1.125rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .info-item {
        display: flex;
        align-items: center;
        margin-bottom: 0.75rem;
        color: #374151;
    }
    .info-icon {
        margin-right: 0.75rem;
        color: #8b93fe;
    }
    .compatibility-bar {
        background-color: #e5e7eb;
        border-radius: 9999px;
        height: 0.5rem;
        margin-top: 0.25rem;
        overflow: hidden;
    }
    .compatibility-fill {
        background: linear-gradient(90deg, #8b93fe, #5755fe);
        height: 100%;
        border-radius: 9999px;
        transition: width 0.3s ease;
    }
    .action-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin-top: 2rem;
    }
    .primary-btn {
        background-color: #5755fe;
        color: white;
        padding: 0.75rem 2rem;
        border-radius: 0.75rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .secondary-btn {
        background-color: rgba(255, 113, 205, 0.2);
        color: #ff71cd;
        padding: 0.75rem 2rem;
        border-radius: 0.75rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .warning-container {
        background-color: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
    }
    .info-message {
        background-color: #dbeafe;
        border: 1px solid #3b82f6;
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
    }
    .compatibility-section {
        background: white;
        border-radius: 1rem;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        border: 2px solid rgba(139, 147, 254, 0.2);
    }
    .section-title {
        color: #5755fe;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
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
    st.markdown('<h1 class="main-title">Your Roommate Match </h1>', unsafe_allow_html=True)

    # Get user profile
    profile = get_user_profile(st.session_state.user_id)
    if not profile:
        st.error("Unable to load profile")
        return

    if profile['ProfileStatus'] != 'Completed':
        st.markdown("""
        <div class="roommate-card">
            <div class="warning-container">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="m12 17 .01 0"/></svg>
                Please complete your profile first.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Profile", help="Complete your profile"):
            st.session_state.page = 'profile'
            st.rerun()
        return

    if profile['MatchingStatus'] != 'Completed':
        st.markdown("""
        <div class="roommate-card">
            <div class="info-message">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-3.7 1.3c-1.2.7-2.3 1.6-3.4 2.4L3 8l2 3h3l-2-3 1.5-1.5C8.75 5.5 10.25 5 12 5a7 7 0 0 1 7 7h2Z"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 3.7-1.3c1.2-.7 2.3-1.6 3.4-2.4L21 16l-2-3h-3l2 3-1.5 1.5c-1.25 1-2.75 1.5-4.5 1.5a7 7 0 0 1-7-7H3Z"/></svg>
                Your roommate matching is not complete yet. Please check back later.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Get roommate info
    roommate = get_roommate(profile['ProfileID'])
    if not roommate:
        st.markdown("""
        <div class="roommate-card">
            <div class="info-message">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
                We haven't found a roommate match for you yet. Please check back later.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Get detailed profile information for roommate
    roommate_profile = get_user_profile_by_id(roommate['ProfileID'])
    if not roommate_profile:
        st.error("Unable to load roommate profile information")
        return

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"""
        <div class="profile-section">
            <div class="profile-avatar">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#ff71cd" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
            <h2 class="roommate-name">{roommate['Name']}</h2>
            <p class="roommate-major">{roommate_profile['Major']}</p>
            <div class="match-score-container">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="#ff71cd" stroke="#ff71cd" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>
                <span class="match-score">{roommate['MatchScore']}% Match</span>
            </div>
            <span class="match-category">
                {get_category_display(roommate['MatchCategory'])}
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="info-section">
            <h3 class="info-title">Contact Information</h3>
            <div class="info-item">
                <span class="info-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                </span>
                <span>{roommate_profile['Phone'] if roommate_profile['Phone'] else 'Not provided'}</span>
            </div>
            <div class="info-item">
                <span class="info-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
                </span>
                <span>{roommate_profile['Major']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-section">
            <h3 class="info-title">Hobbies & Interests</h3>
            <div class="info-item">
                <span class="info-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>
                </span>
                <span>{roommate_profile['Hobby'] if roommate_profile['Hobby'] else 'Not provided'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    
    # Compatibility section inside the same container
    compatibility_data = get_actual_compatibility_by_category(profile['ProfileID'], roommate['ProfileID'])
    
    if compatibility_data:
        st.markdown('<h3 class="section-title" style="margin-top: 2rem;"> Compatibility Radar</h3>', unsafe_allow_html=True)
        
        # Create radar chart using plotly
        categories = [item['Category'] for item in compatibility_data]
        your_values = [item['Your_Score'] for item in compatibility_data]
        roommate_values = [item['Roommate_Score'] for item in compatibility_data]
        compatibility = [item['Compatibility'] for item in compatibility_data]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=your_values,
            theta=categories,
            fill='toself',
            name='You',
            line_color='#5755fe'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=roommate_values,
            theta=categories,
            fill='toself',
            name=roommate['Name'],
            line_color='#ff71cd'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Compatibility by category with styled bars
        st.markdown('<h3 class="section-title">Compatibility Highlights</h3>', unsafe_allow_html=True)
        
        for i, (cat, comp) in enumerate(zip(categories, compatibility)):
            percentage = int(comp * 100)
            st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                    <span style="font-weight: 600; color: #374151;">{cat}</span>
                    <span style="font-weight: 600; color: #8b93fe;">{percentage}%</span>
                </div>
                <div class="compatibility-bar">
                    <div class="compatibility-fill" style="width: {percentage}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Action buttons inside the main container
        col1, col2, col3 = st.columns([1, 1, 1])
        
def get_category_display(category):
    """Helper function to display category with emojis"""
    category_emojis = {
        'A': '🌟🌟🌟🌟🌟 Perfect Match',
        'B': '🌟🌟🌟🌟 Great Match',
        'C': '🌟🌟🌟 Good Match',
        'D': '🌟🌟 Average Match',
        'E': '🌟 Basic Match'
    }
    return category_emojis.get(category, f'{category} Match')