import streamlit as st
import pandas as pd
import random
import time

# 1. 페이지 설정 및 이미지 느낌의 미니멀 UI/애니메이션 정의
st.set_page_config(page_title="아진T와 함께하는 단어 게임", page_icon="🕹️", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
    }
    
    @keyframes fallDown {
        0% { transform: translateY(-50px); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateY(320px); opacity: 0; }
    }
    
    @keyframes splashEffect {
        0% { transform: scale(1); opacity: 1; letter-spacing: 0px; }
        50% { transform: scale(1.3); opacity: 0.5; letter-spacing: 4px; }
        100% { transform: scale(1.6); opacity: 0; filter: blur(4px); }
    }
    
    .game-canvas {
        display: flex;
        justify-content: center;
        gap: 40px;
        height: 350px;
        overflow: hidden;
        background: #ffffff;
        position: relative;
        align-items: flex-start;
        padding-top: 20px;
    }
    
    .floating-word {
        font-size: 26px; 
        font-weight: 600;
        font-family: 'Helvetica Neue', sans-serif;
        text-align: center;
        display: inline-block;
        position: relative;
        cursor: default;
        user-select: none;
    }
    
    .w1 { animation: fallDown 10.0s linear infinite; }
    .w2 { animation: fallDown 13.0s linear infinite; animation-delay: 3.5s; }
    .w3 { animation: fallDown 11.5s linear infinite; animation-delay: 1.5s; }
    
    .popped-word {
        animation: splashEffect 0.3s ease-out forwards !important;
    }
    
    .score-box {
        font-size: 16px;
        font-weight: 500;
        color: #555555;
        text-align: center;
        padding: 5px;
    }
    
    div.stTextInput {
        margin-top: 30px;
    }

    .tts-button {
        background-color: #2AM2FF;
        color: white;
        border: none;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: bold;
        cursor: pointer;
        transition: background 0.2s;
    }
    .tts-button:hover {
        background-color: #008be3;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 데이터 로드
@st.cache_data
def load_data():
    try:
        return pd.read_csv("data.csv")
    except:
        return pd.DataFrame({
            "word": ["observe", "giant", "information", "harmony", "ocean", "travel", "save", "leaf"],
            "meaning": ["관찰하다", "거인", "정보", "조화", "대양, 바다", "이동하다", "구하다", "잎"]
        })

df_origin = load_data()

# 3. 세션 상태 초기화
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "score" not in st.session_state:
