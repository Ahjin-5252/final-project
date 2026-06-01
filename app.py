import streamlit as st
import pandas as pd
import random
import time
from gtts import gTTS
import io

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
    st.session_state.score = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "active_words" not in st.session_state:
    st.session_state.active_words = []
if "word_pool" not in st.session_state:
    st.session_state.word_pool = []
if "just_popped_word" not in st.session_state:
    st.session_state.just_popped_word = None

COLORS = ["#2AM2FF", "#FF3B6F", "#2BD9A5", "#FFAA00", "#9B5DE5"]

def refresh_balloons(matched_word=None):
    if matched_word and matched_word in st.session_state.word_pool:
        st.session_state.word_pool.remove(matched_word)
        
    if len(st.session_state.word_pool) < 3:
        st.session_state.word_pool = df_origin.to_dict(orient="records")
        random.shuffle(st.session_state.word_pool)
        
    selected = st.session_state.word_pool[:3]
    st.session_state.word_pool = st.session_state.word_pool[3:] + selected
    
    st.session_state.active_words = []
    for i, item in enumerate(selected):
        st.session_state.active_words.append({
            "word": item["word"],
            "meaning": item["meaning"],
            "color": COLORS[random.randint(0, len(COLORS)-1)],
            "class": f"w{i+1}"
        })

# 안전 채점 콜백 함수
def check_answer_callback():
    user_answer = st.session_state.game_input_box.strip()
    if user_answer:
        for b in st.session_state.active_words:
            valid_meanings = [m.strip() for m in b["meaning"].split(",")]
            
            if user_answer in valid_meanings:
                st.session_state.score += 1
                st.session_state.just_popped_word = b["word"]
                st.session_state.target_item = {"word": b["word"], "meaning": b["meaning"]}
                break
    st.session_state.game_input_box = ""

# 💡 [수정] 오디오 바이너리 데이터를 안전하게 브라우저로 전달하는 로직
def get_us_audio_bytes(text):
    tts = gTTS(text=text, lang='en', tld='com', slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue() # 오디오 스트림을 고정된 바이트 배열로 추출하여 전달

# --- 화면 구현 ---

# [화면 1] 로그인 및 시작 전 화면
if not st.session_state.game_started:
    st.title("🕹️ 아진T와 함께하는 단어 게임")
    st.write("내려오는 영단어의 뜻을 맞춰보세요!")
    
    name_input = st.text_input("이름을 입력하세요:", value=st.session_state.user_name)
    
    if st.button("Start", use_container_width=True):
        if name_input.strip() == "":
            st.warning("이름을 입력해야 게임을 시작할 수 있습니다!")
        else:
            st.session_state.user_name = name_input
            st.session_state.game_started = True
            st.session_state.start_time = time.time()
            st.session_state.score = 0
            st.session_state.just_popped_word = None
            st.session_state.word_pool = df_origin.to_dict(orient="records")
            random.shuffle(st.session_state.word_pool)
            refresh_balloons()
            st.rerun()

# [화면 2] 게임 시작 후 화면
else:
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(0, 70 - int(elapsed_time))
    
    if remaining_time <= 0:
        st.title("🚨 Game Over")
        st.balloons()
        st.error(f"게임이 끝났습니다! {st.session_state.user_name}님의 최종 합산 점수는 **{st.session_state.score}점**입니다.")
        
        if st.button("다시 도전하기"):
            st.session_state.game_started = False
            st.session_state.start_time = None
            st.session_state.just_popped_word = None
            st.session_state.word_pool = []
            st.rerun()
            
        st.write("---")
        main_col, side_col = st.columns([4, 1])
        with side_col:
            if st.button("📚 단어학습하기", use_container_width=True):
                @st.dialog("📖 오늘 배울 영단어 리스트 (미국식 발음 지원)")
                def show_study_records():
                    st.write("단어 옆의 재생 버튼을 누르면 미국식 표준 발음을 들을 수 있습니다!")
                    st.write("")
                    
                    for index, row in df_origin.iterrows():
                        col_word, col_meaning, col_audio = st.columns([2, 2, 3])
                        with col_word:
                            st.markdown(f"**{row['word']}**")
                        with col_meaning:
                            st.write(row['meaning'])
                        with col_audio:
                            # 💡 [수정] 오디오 포인터가 초기화되지 않도록 완전히 정형화된 바이트 값 전송
                            audio_bytes = get_us_audio_bytes(row['word'])
                            st.audio(audio_bytes, format="audio/mp3")
                        st.write("---")
                show_study_records()
            
    else:
        # 상단 대시보드
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='score-box'>👤 이름: {st.session_state.user_name}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='score-box'>⭐ SCORE: {st.session_state.score}점</div>", unsafe_allow_html=True)
            
        st.write("---")
        
        # 캔버스 렌더링
        b_html = "<div class='game-canvas'>"
        for b in st.session_state.active_words:
            if st.session_state.just_popped_word == b["word"]:
                b_html += f"<div class='floating-word popped-word' style='color: {b['color']};'>{b['word']}</div>"
            else:
                b_html += f"<div class='floating-word {b['class']}' style='color: {b['color']};'>{b['word']}</div>"
        b_html += "</div>"
        st.markdown(b_html, unsafe_allow_html=True)
        
        # 정답 입력창
        st.text_input(
            "", 
            key="game_input_box",
            placeholder="Type here...",
            on_change=check_answer_callback
        )
        
        if st.session_state.just_popped_word:
            time.sleep(0.3)
            refresh_balloons(matched_word=st.session_state.target_item)
            st.session_state.just_popped_word = None
            st.rerun()
        
        time.sleep(0.4)
        st.rerun()
