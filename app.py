import streamlit as st
import pandas as pd
import random
import time

# 1. 페이지 설정 및 미니멀 UI/애니메이션 정의
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

    /* 🔊 발음 재생 버튼 스타일링 */
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
    st.session_state.score = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "active_words" not in st.session_state:
    st.session_state.active_words = []
if "used_words" not in st.session_state:
    st.session_state.used_words = []
if "just_popped_word" not in st.session_state:
    st.session_state.just_popped_word = None

COLORS = ["#2AM2FF", "#FF3B6F", "#2BD9A5", "#FFAA00", "#9B5DE5"]

def replace_single_word(index_to_replace):
    remaining_pool = [
        item for item in df_origin.to_dict(orient="records")
        if item["word"] not in st.session_state.used_words
        and item["word"] not in [w["word"] for w in st.session_state.active_words if w]
    ]
    
    if not remaining_pool:
        remaining_pool = [
            item for item in df_origin.to_dict(orient="records")
            if item["word"] not in [w["word"] for w in st.session_state.active_words if w]
        ]
        if not remaining_pool:
            remaining_pool = df_origin.to_dict(orient="records")
            
    new_item = random.choice(remaining_pool)
    
    word_info = {
        "word": new_item["word"],
        "meaning": new_item["meaning"],
        "color": COLORS[random.randint(0, len(COLORS)-1)],
        "class": f"w{index_to_replace + 1}"
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

# 안전 채점 콜백 함수
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
                break
    st.session_state.game_input_box = ""

# 💡 [핵심 구현] 브라우저 자체 음성 합성 엔진(Web Speech API)을 호출하는 HTML/JS 생성 함수
def generate_browser_tts_html(text, btn_id):
    # 미국식 표준 영어(en-US) 발음을 브라우저에 직접 지시하는 자바스크립트 코드
    html_code = f"""
    <button class="tts-button" onclick="speak_{btn_id}()">🔊 Listen</button>
    <script>
    def speak_{btn_id}() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel(); // 이전 음성 겹침 방지
            var speech = new SpeechSynthesisUtterance("{text}");
            speech.lang = "en-US"; // 표준 미국식 액센트 지정
            speech.rate = 0.9;     // 학생들이 듣기 편하도록 살짝 여유로운 속도
            speech.pitch = 1.0;
            window.speechSynthesis.speak(speech);
        }} else {{
            alert("이 브라우저는 음성 재생을 지원하지 않습니다.");
        }}
    }}
    speak_{btn_id}();
    </script>
    """
    return html_code

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
            init_game_words()
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
            st.session_state.active_words = []
            st.session_state.used_words = []
            st.rerun()
            
        st.write("---")
        main_col, side_col = st.columns([4, 1])
        with side_col:
            if st.button("📚 단어학습하기", use_container_width=True):
                @st.dialog("📖 오늘 배울 영단어 리스트 (미국식 발음 지원)")
                def show_study_records():
                    st.write("단어 옆의 Listen 버튼을 누르면 브라우저 음성으로 발음이 재생됩니다!")
                    st.write("")
                    
                    for index, row in df_origin.iterrows():
                        col_word, col_meaning, col_audio = st.columns([2, 2, 2])
                        with col_word:
                            st.markdown(f"**{row['word']}**")
                        with col_meaning:
                            st.write(row['meaning'])
                        with col_audio:
                            # 💡 브라우저 내장 자바스크립트 스피커 버튼을 화면에 직접 임베딩
                            tts_html = generate_browser_tts_html(row['word'], index)
                            st.components.v1.html(tts_html, height=45)
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
            refresh_balloons(st.session_state.popped_index)
            st.session_state.just_popped_word = None
            st.rerun()
        
        time.sleep(0.4)
        st.rerun()
