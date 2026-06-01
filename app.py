import streamlit as st
import pandas as pd
import random
import time

# 1. 페이지 설정 및 이미지 느낌의 미니멀 UI/애니메이션 정의
st.set_page_config(page_title="아진T와 함께하는 단어 게임", page_icon="🕹️", layout="centered")

st.markdown("""
    <style>
    /* 배경을 완전히 하얗고 깨끗하게 설정 */
    .stApp {
        background-color: #ffffff;
    }
    
    /* 단어들이 위에서 아래로 천천히 내려오는 애니메이션 */
    @keyframes fallDown {
        0% { transform: translateY(-50px); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateY(320px); opacity: 0; }
    }
    
    /* 정답 시 사방으로 퍼지며 사라지는 이펙트 */
    @keyframes splashEffect {
        0% { transform: scale(1); opacity: 1; letter-spacing: 0px; }
        50% { transform: scale(1.3); opacity: 0.5; letter-spacing: 4px; }
        100% { transform: scale(1.6); opacity: 0; filter: blur(4px); }
    }
    
    /* 캔버스 컨테이너 (테두리 없이 투명하고 깔끔하게) */
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
    
    /* 단어 글자 자체만 깔끔하게 동동 뜨게 하는 스타일 */
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
    
    /* 각 단어별 내려오는 속도 다르게 분할 */
    .w1 { animation: fallDown 10.0s linear infinite; }
    .w2 { animation: fallDown 13.0s linear infinite; animation-delay: 3.5s; }
    .w3 { animation: fallDown 11.5s linear infinite; animation-delay: 1.5s; }
    
    /* 정답 단어 터짐 이펙트 */
    .popped-word {
        animation: splashEffect 0.3s ease-out forwards !important;
    }
    
    /* 상단 대시보드 미니멀 스타일화 */
    .score-box {
        font-size: 16px;
        font-weight: 500;
        color: #555555;
        text-align: center;
        padding: 5px;
    }
    
    /* 입력창 상단 여백 조절 */
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
            "word": ["observe", "giant", "information", "harmony", "ocean", "travel", "save", "glottal", "syllable structure"],
            "meaning": ["관찰하다", "거인", "정보", "조화", "대양, 바다", "이동하다", "구하다", "성문의", "음절 구조"]
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
if "input_value" not in st.session_state:
    st.session_state.input_value = ""
if "just_popped_word" not in st.session_state:
    st.session_state.just_popped_word = None

# 감성 폰트 컬러 풀
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

# --- 화면 구현 ---

# [화면 1] 로그인 및 시작 전 화면
if not st.session_state.game_started:
    st.title("🎈 아진T와 함께하는 물풍선 단어 게임")
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
    # 절대 시간 기준으로 경과 시간 체크
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(0, 70 - int(elapsed_time)) # 💡 기존 80초에서 70초로 단축 완료
    
    # [게임 종료 조건] 70초 타임아웃
    if remaining_time <= 0:
        st.title("🚨 Game Over") # 💡 문구 수정 완료
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
                @st.dialog("📖 오늘 배울 영단어 리스트")
                def show_study_records():
                    st.write("오늘 게임에 나온 단어들을 다시 복습하며 실력을 다져봅시다!")
                    st.table(df_origin[["word", "meaning"]])
                show_study_records()
            
    else:
        # 💡 타이머가 들어가던 col3 컬럼을 제거하여 화면에서 완벽히 은닉(시각적 제거)
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
        
        # 정답 입력창 (Type here... 가이드 제공)
        user_answer = st.text_input(
            "", 
            value=st.session_state.input_value, 
            key="game_input_box",
            placeholder="Type here..."
        )
        
        if st.session_state.just_popped_word:
            time.sleep(0.3)
            refresh_balloons(matched_word=st.session_state.target_item)
            st.session_state.just_popped_word = None
            st.rerun()
            
        if user_answer:
            answered_correctly = False
            input_ans = user_answer.strip()
            
            for b in st.session_state.active_words:
                valid_meanings = [m.strip() for m in b["meaning"].split(",")]
                
                if input_ans in valid_meanings:
                    st.session_state.score += 1
                    st.session_state.just_popped_word = b["word"]
                    st.session_state.target_item = {"word": b["word"], "meaning": b["meaning"]}
                    answered_correctly = True
                    break
            
            st.session_state.input_value = ""
            st.rerun()
        
        # 보이지 않는 타이머 동기화를 위해 백엔드는 0.4초 프레임으로 유지
        time.sleep(0.4)
        st.rerun()
