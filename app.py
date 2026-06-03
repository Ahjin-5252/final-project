import streamlit as st
import pandas as pd
import random
import time

# 1. 페이지 설정 및 이미지 느낌의 미니멀 UI/애니메이션 정의
st.set_page_config(page_title="아진T와 함께하는 단어 게임", page_icon="🕹️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
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
        display: flex; justify-content: center; gap: 40px; height: 350px;
        overflow: hidden; background: #ffffff; position: relative; align-items: flex-start; padding-top: 20px;
    }
    .floating-word {
        font-size: 26px; font-weight: 600; font-family: 'Helvetica Neue', sans-serif;
        text-align: center; display: inline-block; position: relative; cursor: default; user-select: none;
    }
    .w1 { animation: fallDown 10.0s linear infinite; }
    .w2 { animation: fallDown 13.0s linear infinite; animation-delay: 3.5s; }
    .w3 { animation: fallDown 11.5s linear infinite; animation-delay: 1.5s; }
    .popped-word { animation: splashEffect 0.3s ease-out forwards !important; }
    .score-box { font-size: 16px; font-weight: 500; color: #555555; text-align: center; padding: 5px; }
    div.stTextInput { margin-top: 30px; }
    </style>
""", unsafe_allow_html=True)

# 2. 데이터 로드
@st.cache_data
def load_game_data():
    try:
        return pd.read_csv("data_game.csv")
    except:
        return pd.DataFrame({
            "word": ["observe", "giant", "information", "harmony", "ocean"],
            "meaning": ["관찰하다", "거인", "정보", "조화", "대양, 바다"]
        })

df_game = load_game_data()

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
if "used_words" not in st.session_state:
    st.session_state.used_words = []
if "just_popped_word" not in st.session_state:
    st.session_state.just_popped_word = None
if "popped_index" not in st.session_state:
    st.session_state.popped_index = None
if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = None

COLORS = ["#2AM2FF", "#FF3B6F", "#2BD9A5", "#FFAA00", "#9B5DE5"]

def replace_single_word(index_to_replace):
    if index_to_replace is None:
        return
    remaining_pool = [
        item for item in df_game.to_dict(orient="records")
        if item["word"] not in st.session_state.used_words
        and item["word"] not in [w["word"] for w in st.session_state.active_words if w]
    ]
    if not remaining_pool:
        remaining_pool = [item for item in df_game.to_dict(orient="records") if item["word"] not in [w["word"] for w in st.session_state.active_words if w]]
        if not remaining_pool: 
            remaining_pool = df_game.to_dict(orient="records")
            
    new_item = random.choice(remaining_pool)
    word_info = {
        "word": new_item["word"], "meaning": new_item["meaning"],
        "color": COLORS[random.randint(0, len(COLORS)-1)], "class": f"w{index_to_replace + 1}"
    }
    if len(st.session_state.active_words) < 3:
        st.session_state.active_words.append(word_info)
    else:
        st.session_state.active_words[index_to_replace] = word_info

def init_game_words():
    st.session_state.active_words = []
    st.session_state.used_words = []
    for i in range(3):
        replace_single_word(i)
    st.session_state.last_refresh_time = time.time()

def check_answer_callback():
    user_answer = st.session_state.game_input_box.strip()
    if user_answer:
        for i, b in enumerate(st.session_state.active_words):
            valid_meanings = [m.strip() for m in b["meaning"].split(",")]
            if user_answer in valid_meanings:
                st.session_state.score += 1
                st.session_state.just_popped_word = b["word"]
                st.session_state.popped_index = i
                st.session_state.used_words.append(b["word"])
                st.session_state.last_refresh_time = time.time()
                break
    st.session_state.game_input_box = ""

# --- 화면 구현 ---
st.title("🕹️ 아진T와 함께하는 단어 게임")

# [화면 1] 로그인 및 시작 전 화면
if not st.session_state.game_started:
    # 🧼 퀴즈 안내 문구를 완전히 삭제하고 깔끔하게 수정 완료
    st.write("위에서 내려오는 영단어의 뜻을 시간 내에 맞춰보세요!")
    
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
            st.session_state.popped_index = None
            init_game_words()
            st.rerun()

# [화면 2] 게임 시작 후 화면
else:
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(0, 50 - int(elapsed_time))
    
    if remaining_time <= 0:
        st.title("🚨 Game Over")
        st.error(f"게임이 끝났습니다! {st.session_state.user_name}님의 최종 점수는 **{st.session_state.score}점**입니다.")
        if st.button("다시 도전하기", use_container_width=True):
            st.session_state.game_started = False
            st.session_state.start_time = None
            st.session_state.active_words = []
            st.session_state.used_words = []
            st.session_state.just_popped_word = None
            st.session_state.popped_index = None
            st.session_state.last_refresh_time = None
            st.rerun()
    else:
        # 3단어가 바닥에 다 내려갈 때까지 못 맞추면 새로운 단어 세트로 갱신
        if time.time() - st.session_state.last_refresh_time > 12.0:
            for b in st.session_state.active_words:
                st.session_state.used_words.append(b["word"])
            for i in range(3):
                replace_single_word(i)
            st.session_state.last_refresh_time = time.time()
            st.rerun()

        # 대시보드 스코어 레이아웃
        col1, col2 = st.columns(2)
        with col1: 
            st.markdown(f"<div class='score-box'>👤 이름: {st.session_state.user_name}</div>", unsafe_allow_html=True)
        with col2: 
            st.markdown(f"<div class='score-box'>⭐ SCORE: {st.session_state.score}점 | ⏱️ {remaining_time}초</div>", unsafe_allow_html=True)
        st.write("---")
        
        # 메인 게임 캔버스 출력
        b_html = "<div class='game-canvas'>"
        for b in st.session_state.active_words:
            if st.session_state.just_popped_word == b["word"]:
                b_html += f"<div class='floating-word popped-word' style='color: {b['color']};'>{b['word']}</div>"
            else:
                b_html += f"<div class='floating-word {b['class']}' style='color: {b['color']};'>{b['word']}</div>"
        b_html += "</div>"
        st.markdown(b_html, unsafe_allow_html=True)
        
        # 정답 입력을 위한 입력 상자
        st.text_input("", key="game_input_box", placeholder="Type here...", on_change=check_answer_callback)
        
        # 단어 폭발 및 리플레이스 트리거 연산
        p_idx = st.session_state.get("popped_index", None)
        if st.session_state.just_popped_word and p_idx is not None:
            time.sleep(0.3)
            replace_single_word(p_idx)
            st.session_state.just_popped_word = None
            st.session_state.popped_index = None
            st.rerun()
            
        time.sleep(0.4)
        st.rerun()
