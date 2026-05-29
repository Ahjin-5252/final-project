import streamlit as st
import pandas as pd
import random
import time

# 1. 페이지 기본 설정 및 알록달록한 CSS 디자인
st.set_page_config(page_title="아진T와 함께하는 단어 게임", page_icon="🎈", layout="centered")

st.markdown("""
    <style>
    .balloon {
        font-size: 24px;
        font-weight: bold;
        padding: 20px;
        border-radius: 50% 50% 50% 50% / 40% 40% 60% 60%;
        display: inline-block;
        animation: float Down 5s linear infinite;
        text-align: center;
        box-shadow: inset -10px -10px 20px rgba(0,0,0,0.2);
        color: white;
    }
    .score-box {
        font-size: 20px;
        font-weight: bold;
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CSV 데이터 로드 기능 (data.csv 파일이 같은 경로에 있다고 가정)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv")
        return df
    except:
        # 데이터 파일이 없을 경우를 대비한 샘플 데이터
        return pd.DataFrame({
            "word": ["observe", "giant", "information", "harmony"],
            "meaning": ["관찰하다", "거인", "정보", "조화"]
        })

df = load_data()

# 3. 세션 상태(Session State) 초기화
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "score" not in st.session_state:
    st.session_state.score = 0
if "current_idx" not in st.session_state:
    st.session_state.current_idx = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = 0
if "balloon_color" not in st.session_state:
    st.session_state.balloon_color = "#FF4B4B"

# 알록달록한 물풍선 색상 리스트
COLORS = ["#FF4B4B", "#1C83E1", "#00D4B2", "#FFD166", "#9B5DE5", "#F15BB5"]

def next_word():
    st.session_state.current_idx = random.randint(0, len(df) - 1)
    st.session_state.balloon_color = random.choice(COLORS)

# --- 화면 구현 ---

# [화면 1] 로그인 및 시작 전 화면
if not st.session_state.game_started:
    st.title("🐋 아진T의 영단어 연구소")
    st.subheader("물풍선 단어 맞추기 게임 🎈")
    
    name_input = st.text_input("연구원 이름을 입력하세요:", value=st.session_state.user_name)
    
    if st.button("Start", use_container_width=True):
        if name_input.strip() == "":
            st.warning("이름을 입력해야 게임을 시작할 수 있습니다!")
        else:
            st.session_state.user_name = name_input
            st.session_state.game_started = True
            st.session_state.start_time = time.time()
            st.session_state.score = 0
            next_word()
            st.rerun()

# [화면 2] 게임 시작 후 화면
else:
    # 80초 제한 시간 계산
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(0, 80 - int(elapsed_time))
    
    # [게임 오버 조건] 제한 시간 종료
    if remaining_time <= 0:
        st.title("🚨 Game Over!")
        st.balloons()
        st.error(f"It's over. {st.session_state.user_name} 연구원의 최종 합산 점수는 **{st.session_state.score}점**입니다!")
        
        if st.button("다시 도전하기"):
            st.session_state.game_started = False
            st.rerun()
            
    # [게임 진행 중]
    else:
        # 대시보드 표시 (이름, 점수, 남은 시간)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='score-box'>👤 연구원: {st.session_state.user_name}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='score-box'>⭐ SCORE: {st.session_state.score}점</div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='score-box'>⏱️ TIME: {remaining_time}초</div>", unsafe_allow_html=True)
            
        st.write("---")
        
        # 현재 맞춰야 할 단어 정보
        current_word = df.iloc[st.session_state.current_idx]["word"]
        correct_meaning = df.iloc[st.session_state.current_idx]["meaning"]
        
        # 물풍선 시각화 (알록달록한 색상 반영)
        st.markdown(f"""
            <div style='text-align: center; margin-top: 50px; margin-bottom: 50px;'>
                <div class='balloon' style='background-color: {st.session_state.balloon_color}; width: 160px; height: 180px; line-height: 140px;'>
                    {current_word}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # 정답 입력창
        user_answer = st.text_input("이 단어의 뜻은 무엇일까요?", key=f"ans_{st.session_state.score}", placeholder="정답을 입력하고 엔터를 누르세요")
        
        # 정답 검증 메커니즘
        if user_answer:
            if user_answer.strip() == correct_meaning.strip():
                st.success("💥 펑! 정답입니다! (+1점)")
                st.session_state.score += 1
                time.sleep(0.5) # 정답 이펙트를 잠시 보여줌
                next_word()
                st.rerun()
            else:
                st.error("❌ 틀렸습니다! 물풍선이 내려오고 있어요! 다시 입력해보세요.")

# --- 하단 공통 영역: 단어 학습하기 창 (Modal) ---
st.write("")
st.write("")
main_col, side_col = st.columns([4, 1])

with side_col:
    # 오른쪽 하단에 '단어학습하기' 버튼 배치
    if st.button("📚 단어학습하기", use_container_width=True):
        # 별도의 모달창(dialog) 형태로 데이터 프레임 노출
        @st.dialog("📖 오늘 배울 영단어 리스트")
        def show_study_records():
            st.write("게임에 나오기 전에 단어들을 다시 한번 복습해봅시다!")
            st.table(df[["word", "meaning"]])
        show_study_records()
