import streamlit as st
import random
import re

# Page Config
st.set_page_config(
    page_title="fromis_9 가사맞추기",
    page_icon="🍀",
    layout="centered"
)

# Custom CSS for 'Vitamin Me' Aesthetic (Bright, Fresh, Pastel Glassmorphism)
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    * {
        font-family: 'Pretendard', sans-serif !important;
    }

    /* Main Background & Text Color */
    .stApp {
        background: linear-gradient(180deg, #FFFDF0 0%, #FFF5F7 100%);
        color: #333333;
    }
    
    /* Header Card */
    .header-card {
        background: linear-gradient(135deg, #FF758C 0%, #FF7EB3 100%);
        padding: 2.2rem 1.5rem;
        border-radius: 28px;
        text-align: center;
        box-shadow: 0px 12px 24px rgba(255, 117, 140, 0.25);
        margin-bottom: 1.8rem;
        color: white;
        position: relative;
        overflow: hidden;
    }
    .header-card h1 {
        color: #FFFFFF !important;
        font-weight: 900;
        font-size: 2.3rem;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .header-card p {
        font-size: 1.05rem;
        opacity: 0.95;
        font-weight: 500;
        margin: 0;
    }

    /* Quiz Card Container */
    .quiz-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 28px;
        border: 2px solid #FFE5EC;
        box-shadow: 0px 15px 30px rgba(255, 182, 193, 0.15);
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease;
    }
    
    .lyrics-box {
        background: linear-gradient(135deg, #FFF0F5 0%, #FFE6ED 100%);
        padding: 1.8rem 1.5rem;
        border-radius: 20px;
        font-size: 1.35rem;
        font-weight: 700;
        color: #FF3366;
        line-height: 1.8;
        margin: 1.2rem 0;
        text-align: center;
        border: 1px solid #FFD1DC;
        word-break: keep-all;
    }

    /* Stats Badge */
    .stat-badge {
        display: inline-block;
        background-color: #FFE5EC;
        color: #FF4D6D;
        padding: 0.4rem 1rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 0.9rem;
        margin-right: 0.5rem;
    }

    /* Custom Input Box styling */
    .stTextInput > div > div > input {
        border-radius: 14px !important;
        border: 2px solid #FFCCD5 !important;
        padding: 12px 16px !important;
        font-size: 1.1rem !important;
        color: #333333 !important;
        background-color: #FFFFFF !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #FF4D6D !important;
        box-shadow: 0 0 0 3px rgba(255, 77, 109, 0.2) !important;
    }

    /* Buttons Style */
    .stButton > button {
        background: linear-gradient(135deg, #FF6B8B 0%, #FF8E53 100%);
        color: white !important;
        border: none;
        border-radius: 16px;
        font-weight: 800;
        font-size: 1.05rem;
        padding: 0.7rem 1.2rem;
        box-shadow: 0 6px 16px rgba(255, 107, 139, 0.3);
        transition: all 0.2s ease-in-out;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255, 107, 139, 0.4);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #FFF9FA;
        border-right: 1px solid #FFE0E6;
    }
</style>
""", unsafe_allow_html=True)

# 곡 및 가사 데이터베이스
SONG_DATA = {
    "Supersonic": [
        {"lyrics": "속도를 높여 더 ___ 너에게 가고 있어", "answer": "빠르게", "hint": "초성: ㅂㄹㄱ"},
        {"lyrics": "Hit me up when you need some ___", "answer": "energy", "hint": "뜻: 에너지 (영어)"},
        {"lyrics": "너의 맘속으로 ___", "answer": "Supersonic", "hint": "곡 제목과 동일!"}
    ],
    "DM": [
        {"lyrics": "좋아해 너를 ___ 말해 버릴까", "answer": "솔직하게", "hint": "초성: ㅅㅈㅎㄱ"},
        {"lyrics": "Doesn't matter ___ 숨길 수가 없는걸", "answer": "where", "hint": "장소를 뜻하는 영단어"},
        {"lyrics": "내 맘을 전해줘 ___", "answer": "DM", "hint": "인스타그램 다이렉트 메시지 약자"}
    ],
    "Stay This Way": [
        {"lyrics": "바람이 불어오는 ___ 타고", "answer": "언덕을", "hint": "초성: ㅇㄷㅇ"},
        {"lyrics": "Stay this way ___ 넘어로", "answer": "수평선", "hint": "바다와 하늘이 만나는 선"},
        {"lyrics": "우리만의 ___ 비밀이야", "answer": "여름은", "hint": "계절 이름이 들어갑니다"}
    ],
    "WE GO": [
        {"lyrics": "바람을 따라 ___ 나를 던져봐", "answer": "몸을", "hint": "초성: ㅁㅇ"},
        {"lyrics": "Come on and ___ with me", "answer": "WE GO", "hint": "곡 제목과 동일"},
        {"lyrics": "망설이지 마 ___", "answer": "Right now", "hint": "뜻: 지금 당장 (영어)"}
    ],
    "LOVE BOMB": [
        {"lyrics": "터진 듯해 ___ LOVE BOMB", "answer": "내 맘속에", "hint": "초성: ㄴ ㅁㅅㅇ"},
        {"lyrics": "어쩌나 터져 버린 ___", "answer": "LOVE BOMB", "hint": "곡 제목"},
        {"lyrics": "조금씩 타들어 가 ___", "answer": "심장에", "hint": "가슴 속 쿵쾅대는 곳"}
    ],
    "Rewind": [
        {"lyrics": "시간을 돌려 ___ 순간으로", "answer": "그때 그", "hint": "초성: ㄱㄸ ㄱ"},
        {"lyrics": "다시 돌아가는 ___", "answer": "Rewind", "hint": "되돌리다라는 뜻의 곡 제목"}
    ],
    "Escape Room": [
        {"lyrics": "아무도 모르게 ___ 문을 열어", "answer": "비밀의", "hint": "초성: ㅂㅁㅇ"},
        {"lyrics": "이 밤이 지새도록 ___", "answer": "Escape Room", "hint": "방탈출을 뜻하는 영문 제목"}
    ]
}

# 정답 유연성 체크 함수 (공백 및 대소문자 무시)
def normalize_string(s):
    return re.sub(r'\s+', '', s).lower()

# Session State 초기화
if "score" not in st.session_state:
    st.session_state.score = 0
if "combo" not in st.session_state:
    st.session_state.combo = 0
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "answered" not in st.session_state:
    st.session_state.answered = False

# Header
st.markdown("""
<div class="header-card">
    <h1>🍀 fromis_9 가사맞추기</h1>
    <p>상큼함 터지는 프로미스나인 명곡 빈칸 퀴즈!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar: 곡 선택 및 스탯
st.sidebar.markdown("### 🎵 플레이리스트")
selected_song = st.sidebar.selectbox("퀴즈를 풀 곡을 선택해주세요!", list(SONG_DATA.keys()))

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 My Stats")
st.sidebar.metric(label="총 점수", value=f"{st.session_state.score} 점")
st.sidebar.metric(label="현재 콤보", value=f"🔥 {st.session_state.combo} Combo")

# 곡 선택 변경 시 인덱스 초기화
if "last_selected_song" not in st.session_state or st.session_state.last_selected_song != selected_song:
    st.session_state.last_selected_song = selected_song
    st.session_state.current_q = 0
    st.session_state.answered = False

quiz_list = SONG_DATA[selected_song]
q_data = quiz_list[st.session_state.current_q]

# UI Top bar
col_info1, col_info2 = st.columns([2, 1])
with col_info1:
    st.markdown(f"#### 🎧 현재 재생 곡: **{selected_song}**")
with col_info2:
    st.markdown(f"<div style='text-align: right;'><span class='stat-badge'>Q {st.session_state.current_q + 1} / {len(quiz_list)}</span></div>", unsafe_allow_html=True)

# Progress Bar
progress = (st.session_state.current_q + 1) / len(quiz_list)
st.progress(progress)

# Quiz Main Card
st.markdown('<div class="quiz-card">', unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #888888; font-weight: 600;'>가사의 빈칸 '___' 에 들어갈 단어는?</p>", unsafe_allow_html=True)
st.markdown(f'<div class="lyrics-box">"{q_data["lyrics"]}"</div>', unsafe_allow_html=True)

# User Input
user_input = st.text_input("정답 입력", placeholder="정답을 입력하고 Enter를 누르세요", key=f"q_{selected_song}_{st.session_state.current_q}")

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("힌트 보기 💡"):
        st.info(f"🔑 {q_data['hint']}")

with col2:
    check_btn = st.button("정답 확인 ✨")

if check_btn:
    if user_input.strip() == "":
        st.warning("가사를 입력해주세요!")
    else:
        norm_user = normalize_string(user_input)
        norm_answer = normalize_string(q_data["answer"])
        
        if norm_user == norm_answer:
            st.session_state.combo += 1
            added_score = 10 + (st.session_state.combo * 2) # 콤보 추가점수
            st.session_state.score += added_score
            st.success(f"🎉 **정답입니다!** (+{added_score}점 / 🔥 {st.session_state.combo} 콤보!)")
            st.balloons()
            st.session_state.answered = True
        else:
            st.session_state.combo = 0
            st.error(f"아쉬워요! 정답은 **'{q_data['answer']}'** 입니다.")
            st.session_state.answered = True

st.markdown('</div>', unsafe_allow_html=True)

# Control Buttons
col_prev, col_next = st.columns(2)

with col_prev:
    if st.button("🔄 게임 리셋"):
        st.session_state.score = 0
        st.session_state.combo = 0
        st.session_state.current_q = 0
        st.session_state.answered = False
        st.rerun()

with col_next:
    if st.button("다음 문제로 ➡️"):
        if st.session_state.current_q < len(quiz_list) - 1:
            st.session_state.current_q += 1
            st.session_state.answered = False
            st.rerun()
        else:
            st.success(f"🏆 '{selected_song}'의 모든 문제를 마쳤습니다! 다른 곡도 도전해 보세요!")
