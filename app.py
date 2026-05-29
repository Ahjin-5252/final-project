import streamlit as st
import pandas as pd
import random
import time

# 1. 페이지 설정 및 애니메이션
st.set_page_config(page_title="아진T와 함께하는 물풍선 단어 게임", page_icon="🎈", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-color: #f7f9fc;
    }
    
    @keyframes fallDown {
        0% { transform: translateY(-100px); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateY(350px); opacity: 0; }
    }
    
    .balloon-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        height: 380px;
        overflow: hidden;
        background: #eef2f7;
        border-radius: 15px;
        padding: 20px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.05);
        position: relative;
    }
    .balloon {
        font-size: 20px;
        font-weight: bold;
        color: white;
        width: 110px;
        height: 130px;
        line-height: 100px;
        text-align: center;
        border-radius: 50% 50% 50% 50% / 40% 40% 60% 60%;
        box-shadow: inset -8px -8px 15px rgba(0,0,0,0.2), 0 5px 10px rgba(0,0,0,0.1);
        display: inline-block;
        position: relative;
    }
    
    .b1 { animation: fallDown 9.0s linear infinite; }
    .b2 { animation: fallDown 12.0s linear infinite; animation-delay: 3.0s; }
    .b3 { animation: fallDown 10.5s linear infinite; animation-delay: 1.0s; }
    
    .score-box {
        font-size: 18px;
        font-weight: bold;
        background-color: white;
        padding: 12px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* 🎯 화면 정중앙 팝업 피드백 스타일 */
    .popup-feedback {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 9999;
        padding: 30px 60px;
        border-radius: 20px;
        font-size: 32px;
        font-weight: bold;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        animation: popEffect 0.4s ease-out;
    }
    @keyframes popEffect {
        0% { transform: translate(-50%, -50%) scale(0.5); opacity: 0; }
        100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
    }
    .popup-success { background-color: #4BB543; }
    .popup-error { background-color: #FF3333; }
    </style>
""", unsafe_allow_html=True)

# 2. 데이터 로드 및 원본 보존
@st.cache_data
def load_data():
    try:
        return pd.read_csv("data.csv")
    except:
        return pd.DataFrame({
            "word": ["observe", "giant", "information", "harmony", "ocean", "travel", "save", "expected", "human"],
            "meaning": ["관찰하다", "거인", "정보", "조화", "대양, 바다", "이동하다", "구하다", "예상했다", "인간의"]
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
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "word_pool" not in st.session_state:
    st.session_state.word_pool = []

COLORS = ["#FF595E", "#FFCA3A", "#8AC926", "#1982C4", "#6A4C93", "#FF60B5"]

# 🔄 중복 없는 완전 랜덤 순환 풀 매니저 함수
def refresh_balloons(matched_word=None):
    # 정답을 맞춘 단어가 있다면 전체 단어 데이터 풀(word_pool)에서 완전히 영구 제외
    if matched_word and matched_word in st.session_state.word_pool:
        st.session_state.word_pool.remove(matched_word)
        
    # 만약 풀이 비었거나 남아있는 단어가 3개 미만이면 원본 데이터에서 다시 채워서 섞음
    if len(st.session_state.word_pool) < 3:
        st.session_state.word_pool = df_origin.to_dict(orient="records")
        random.shuffle(st.session_state.word_pool)
        
    # 현재 화면에 떠 있는 단어들과 중복되지 않게 무작위로 3개 추출
    selected = st.session_state.word_pool[:3]
    
    # 다음 턴을 위해 방금 사용된 3개 단어는 리스트의 맨 뒤로 보내서 순환 유도
    # (단, 정답을 맞춘 단어는 위에서 원천 제외되었으므로 오답/미입력 단어들만 순환됨)
    st.session_state.word_pool = st.session_state.word_pool[3:] + selected
    
    st.session_state.active_words = []
    for i, item in enumerate(selected):
        st.session_state.active_words.append({
            "word": item["word"],
            "meaning": item["meaning"],
            "color": COLORS[i % len(COLORS)],
            "class": f"b{i+1}"
        })

# --- 화면 구현 ---

# [화면 1] 로그인 및 시작 전 화면
if not st.session_state.game_started:
    st.title("🎈 아진T와 함께하는 물풍선 단어 게임")
    st.write("내려오는 물풍선 속 영단어의 뜻을 맞춰보세요!")
    
    name_input = st.text_input("이름을 입력하세요:", value=st.session_state.user_name)
    
    if st.button("Start", use_container_width=True):
        if name_input.strip() == "":
            st.warning("이름을 입력해야 게임을 시작할 수 있습니다!")
        else:
            st.session_state.user_name = name_input
            st.session_state.game_started = True
            st.session_state.start_time = time.time()
            st.session_state.score = 0
            st.session_state.feedback = None
            st.session_state.word_pool = df_origin.to_dict(orient="records")
            random.shuffle(st.session_state.word_pool)
            refresh_balloons()
            st.rerun()

# [화면 2] 게임 시작 후 화면
else:
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(0, 80 - int(elapsed_time))
    
    # [게임 종료 조건] 80초 끝
    if remaining_time <= 0:
        st.title("🚨 It's over.")
        st.balloons()
        st.error(f"게임이 끝났습니다! {st.session_state.user_name}님의 최종 합산 점수는 **{st.session_state.score}점**입니다.")
        
        if st.button("다시 도전하기"):
            st.session_state.game_started = False
            st.session_state.start_time = None
            st.session_state.feedback = None
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
            
    # [게임 진행 중]
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='score-box'>👤 이름: {st.session_state.user_name}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='score-box'>⭐ SCORE: {st.session_state.score}점</div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='score-box'>⏱️ TIME: {remaining_time}초</div>", unsafe_allow_html=True)
            
        st.write("---")
        
        # 🎈 물풍선 및 🎯 정중앙 팝업 렌더링 컨테이너
        b_html = "<div class='balloon-container' style='position: relative;'>"
        
        if st.session_state.feedback == "success":
            b_html += "<div class='popup-feedback popup-success'>💥 정답 💖</div>"
        elif st.session_state.feedback == "error":
            b_html += "<div class='popup-feedback popup-error'>다시 해보세요 🔥</div>"
            
        for b in st.session_state.active_words:
            # 정답 처리 순간에는 풍선이 터지는 이펙트를 위해 숨김
            if st.session_state.feedback == "success":
                continue
            b_html += f"<div class='balloon {b['class']}' style='background-color: {b['color']};'>{b['word']}</div>"
            
        b_html += "</div>"
        st.markdown(b_html, unsafe_allow_html=True)
        
        # 정답 입력창 (오답 제출 시 입력창 초기화를 위해 score와 무관하게 고정 키 할당)
        st.write("")
        user_answer = st.text_input("화면에 보이는 단어 중 하나의 뜻을 입력하고 Enter를 누르세요:", key="game_input_box")
        
        # 피드백 오버레이 제어 제어 루틴 (Sleep 후 상태 클리어 및 강제 리프레시)
        if st.session_state.feedback in ["success", "error"]:
            time.sleep(0.7)  # 피드백 박스가 정중앙에 머무는 시간
            if st.session_state.feedback == "success":
                # 정답 맞춘 단어는 풀에서 완전 제거 타겟팅
                refresh_balloons(matched_word=st.session_state.target_word)
            else:
                # 틀렸을 경우에는 현재 조합을 유지하지 않고 요청대로 '새로운 단어들'이 내려오도록 풀 순환 교체
                refresh_balloons()
                
            st.session_state.feedback = None
            st.rerun()
            
        if user_answer:
            answered_correctly = False
            input_ans = user_answer.strip()
            
            for b in st.session_state.active_words:
                valid_meanings = [m.strip() for m in b["meaning"].split(",")]
                
                if input_ans in valid_meanings:
                    st.session_state.score += 1
                    st.session_state.feedback = "success"
                    # 맞춘 타겟 단어 임시 세션 기록
                    st.session_state.target_word = {"word": b["word"], "meaning": b["meaning"]}
                    answered_correctly = True
                    break
            
            if not answered_correctly:
                st.session_state.feedback = "error"
            
            st.rerun()
        
        # 평소 타이머 흐름 제어 (1초씩 차감 후 강제 동기화)
        time.sleep(1)
        st.rerun()
