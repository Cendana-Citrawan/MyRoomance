import streamlit as st
import base64
import time

def splash_page():
    st.markdown(f"""
                <style>
                .stMain {{
                    background-color: var(--vibrant-pink);
                    justify-content: center;
                    text-align: center;
                    overflow: hidden;
                }}

                .stMainBlockContainer {{
                    padding: 0 ;
                    max-width: none;
                }}
                
                .stButton {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    height: 100%;
                    z-index: 100;
                    cursor: pointer;
                }}
                
                .stButton>button{{
                    background-color: unset;
                    width: 100%;
                    height: 100%;
                    border-radius: 0;
                    border: none;
                }}
                
                .stButton>button:active{{
                    background-color: unset;
                }}

                .context .logo {{
                    max-width: 100%;
                    width: 15vw;
                    height: auto;
                    margin-bottom: -50px;
                    animation: floatingup 1s ease forwards, float 3s ease-in-out infinite;
                    animation-delay: 0s, 1s;
                }}
                
                .context .title {{
                    color: var(--light-pink);
                    font-size: 6rem;
                    font-weight: 600;
                    font-family: var(--font-family-heading);
                    margin-bottom: -40px;
                    animation: floatingup 1s ease forwards, float 3s ease-in-out infinite;
                    animation-delay: 0.2s, 1.2s;
                }}

                .context .subtitle {{
                    color: var(--light-pink);
                    font-size: 3rem;
                    font-weight: 400;
                    font-family: var(--font-family);
                    animation: floatingup 1s ease forwards, float 3s ease-in-out infinite;
                    animation-delay: 0.4s, 1.4s;
                }}
                
                .context {{
                    width: 100%;
                    position: relative;
                    z-index: 10;
                }}
                
                .stIFrame {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: 100;
                }}
                
                .circles{{
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    margin: 0;
                    z-index: 1;
                }}

                .circles li{{
                    position: absolute;
                    display: block;
                    list-style: none;
                    width: 20px;
                    height: 20px;
                    background: var(--vibrant-blue);
                    animation: animate 2s linear infinite;
                    bottom: -500px;
                }}
                
                .circles li:nth-child(1) {{ left: 35%; width: 7vw; height: 7vw; animation-delay: 0.1s; animation-duration: 3s;}}
                .circles li:nth-child(2) {{ left: 15%; width: 2vw; height: 2vw; animation-delay: 0.5s; animation-duration: 3s; }}
                .circles li:nth-child(3) {{ left: 75%; width: 2vw; height: 2vw; animation-delay: 4.5s; animation-duration: 5s;}}
                .circles li:nth-child(4) {{ left: 45%; width: 5vw; height: 5vw; animation-delay: 0.8s; animation-duration: 3s; }}
                .circles li:nth-child(5) {{ left: 65%; width: 2vw; height: 2vw; animation-delay: 5.5s; animation-duration: 5s;}}
                .circles li:nth-child(6) {{ left: 85%; width: 12vw; height: 12vw; animation-delay: 2.5s; animation-duration: 3s;}}
                .circles li:nth-child(7) {{ left: 0%; width: 10vw; height: 10vw; animation-delay: 7.5s; animation-duration: 3s;}}
                .circles li:nth-child(8) {{ left: 55%; width: 1.5vw; height: 1.5vw; animation-delay: 4.5s; animation-duration: 4s; }}
                .circles li:nth-child(9) {{ left: 25%; width: 0.5vw; height: 0.5vw; animation-delay: 1.5s; animation-duration: 5s; }}
                .circles li:nth-child(10) {{ left: 95%; width: 9vw; height: 9vw; animation-delay: 6.5s; animation-duration: 6s; }}

                @keyframes animate {{

                    0%{{
                        transform: translateY(0) rotate(0deg);
                        opacity: 2;
                        border-radius: 0%;
                    }}
                    100%{{
                        transform: translateY(-1000px) rotate(720deg);
                        opacity: 0;
                        border-radius: 75%;
                    }}

                }}
                
                @keyframes floatingup {{
                    0% {{ transform: translateY(1000px); opacity: 0; }}
                    100% {{ transform: translateY(0px); opacity: 1; }}
                }}
                
                @keyframes float {{
                    0%, 100% {{ transform: translateY(0); }}
                    50% {{ transform: translateY(20px); }}
                }}
                
                @media (max-width: 1200px) {{
                    .context .title {{ font-size: 5.5rem; }}
                    .context .subtitle {{ font-size: 2.5rem; }}
                    .context .logo {{ width: 25vw; }}
                }}

                @media (max-width: 768px) {{
                    .context .title {{ font-size: 4rem; }}
                    .context .subtitle {{ font-size: 2rem; }}
                    .context .logo {{ width: 30vw; }}
                }}

                </style>
                <div class="context">
                    <img src="data:image/png;base64,{base64.b64encode(open('assets/Logo.png', 'rb').read()).decode()}" alt="Logo" class="logo" />
                    <h1 class='title'>MyRoomance</h1>
                    <h2 class='subtitle'>Smart match better living</h2>
                </div>
                <div class="area" >
                    <ul class="circles">
                            <li></li>
                            <li></li>
                            <li></li>
                            <li></li>
                            <li></li>
                            <li></li>
                            <li></li>
                            <li></li>
                            <li></li>
                            <li></li>
                    </ul>
                </div >
                """, True)

    st.button("", on_click=lambda: time.sleep(2) or st.session_state.setdefault('page', 'login'))