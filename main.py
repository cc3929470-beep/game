import streamlit as st
import random
import re

# Page Config
st.set_page_config(
    page_title="fromis_9 가사맞추기",
    page_icon="🍀",
    layout="centered"
)

# Custom CSS (Vitamin Me 감성 + 연초록 사이드바)
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    * {
        font-family: 'Pretendard', sans-serif !important;
    }

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

    .stat-badge {
        display: inline-block;
        background-color: #FFE5EC;
        color: #FF4D6D;
        padding: 0.4rem 1rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 0.9rem;
    }

    /* Input Field */
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

    /* Buttons */
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
    
    /* 눈이 편안한 연한 초록색 사이드바 */
    section[data-testid="stSidebar"] {
        background-color: #E8F5E9 !important;
        border-right: 2px solid #C8E6C9 !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 프로미스나인 디스코그래피 전체 곡 데이터베이스 (최신곡 추가)
# ----------------------------------------------------
ALL_SONG_DATA = {
    # [최신 곡 추가]
    "Vitamin ME": [
        {"lyrics": "I'ma make you happy, 달콤한 ___ fizz", "answer": "lemon", "hint": "상큼한 레몬 (영어)"},
        {"lyrics": "Got you feeling ___, ooh, ooh, ooh", "answer": "new", "hint": "새로운 느낌의 영단어"}
    ],
    "하얀 그리움": [
        {"lyrics": "하얀 눈이 내려와 내 맘을 ___ 해", "answer": "아프게", "hint": "초성: ㅇㅍㄱ"},
        {"lyrics": "사라져 버린 눈처럼 그댄 ___ 흩어져", "answer": "눈물로", "hint": "초성: ㄴㅁㄹ"}
    ],
    "Supersonic": [
        {"lyrics": "속도를 높여 더 ___ 너에게 가고 있어", "answer": "빠르게", "hint": "초성: ㅂㄹㄱ"},
        {"lyrics": "Hit me up when you need some ___", "answer": "energy", "hint": "뜻: 에너지 (영어)"},
        {"lyrics": "너의 맘속으로 ___", "answer": "Supersonic", "hint": "곡 제목과 동일!"}
    ],
    "Beat the Heat": [
        {"lyrics": "뜨거운 태양 아래 ___ 날려버려", "answer": "더위를", "hint": "여름의 무더움"}
    ],
    "Love Me Back": [
        {"lyrics": "너의 마음도 나와 같기를 ___", "answer": "바래", "hint": "희망하다"}
    ],
    "#menow": [
        {"lyrics": "솔직하게 보여줄게 ___ 모습", "answer": "지금의", "hint": "현재의"},
        {"lyrics": "I like me, ___ no matter what", "answer": "me now", "hint": "곡 제목 관련"}
    ],
    "Attitude": [
        {"lyrics": "당당하게 걸어가 나의 ___대로", "answer": "스타일", "hint": "자신만의 방식"}
    ],
    "DM": [
        {"lyrics": "좋아해 너를 ___ 말해 버릴까", "answer": "솔직하게", "hint": "초성: ㅅㅈㅎㄱ"},
        {"lyrics": "내 맘을 전해줘 ___", "answer": "DM", "hint": "다이렉트 메시지 약자"}
    ],
    "Stay This Way": [
        {"lyrics": "바람이 불어오는 ___ 타고", "answer": "언덕을", "hint": "초성: ㅇㄷㅇ"},
        {"lyrics": "우리만의 ___ 비밀이야", "answer": "여름은", "hint": "계절 이름"}
    ],
    "WE GO": [
        {"lyrics": "바람을 따라 ___ 나를 던져봐", "answer": "몸을", "hint": "초성: ㅁㅇ"},
        {"lyrics": "Come on and ___ with me", "answer": "WE GO", "hint": "곡 제목"}
    ],
    "LOVE BOMB": [
        {"lyrics": "터진 듯해 ___ LOVE BOMB", "answer": "내 맘속에", "hint": "초성: ㄴ ㅁㅅㅇ"},
        {"lyrics": "조금씩 타들어 가 ___", "answer": "심장에", "hint": "가슴 속 쿵쾅대는 곳"}
    ],
    "Rewind": [
        {"lyrics": "시간을 돌려 ___ 순간으로", "answer": "그때 그", "hint": "초성: ㄱㄸ ㄱ"},
        {"lyrics": "다시 돌아가는 ___", "answer": "Rewind", "hint": "되돌리다라는 뜻의 제목"}
    ],
    "Escape Room": [
        {"lyrics": "아무도 모르게 ___ 문을 열어", "answer": "비밀의", "hint": "초성: ㅂㅁㅇ"}
    ]
}

def normalize_string(s):
    return re.sub(r'\s+', '', s).lower()

# Session State 초기화
if "score" not in st.session_state:
    st.session_state.score = 0
if "combo" not in st.session_state:
    st.session_state.combo = 0
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "random_queue" not in st.session_state:
    st.session_state.random_queue = []

# Header
st.markdown("""
<div class="header-card">
    <h1>🍀 fromis_9 가사맞추기</h1>
    <p>상큼함 터지는 프로미스나인 전곡 가사 맞추기 퀴즈!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### 🎵 곡 선택")
song_options = ["✨ 전체 랜덤 (전곡 모드)"] + list(ALL_SONG_DATA.keys())
selected_song = st.sidebar.selectbox("퀴즈를 풀 곡 또는 모드를 선택하세요!", song_options)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 My Stats")
st.sidebar.metric(label="총 점수", value=f"{st.session_state.score} 점")
st.sidebar.metric(label="현재 콤보", value=f"🔥 {st.session_state.combo} Combo")

def generate_all_questions():
    questions = []
    for song_title, q_list in ALL_SONG_DATA.items():
        for item in q_list:
            q_copy = item.copy()
            q_copy["song_title"] = song_title
            questions.append(q_copy)
    random.shuffle(questions)
    return questions

# 모드 변경 시 초기화
if "last_mode" not in st.session_state or st.session_state.last_mode != selected_song:
    st.session_state.last_mode = selected_song
    st.session_state.current_q_index = 0
    if selected_song == "✨ 전체 랜덤 (전곡 모드)":
        st.session_state.random_queue = generate_all_questions()

# 문제 데이터 추출
if selected_song == "✨ 전체 랜덤 (전곡 모드)":
    if not st.session_state.random_queue:
        st.session_state.random_queue = generate_all_questions()
    
    current_q = st.session_state.random_queue[st.session_state.current_q_index % len(st.session_state.random_queue)]
    display_title = f"{current_q['song_title']} (전곡 랜덤 모드)"
    total_q_count = len(st.session_state.random_queue)
else:
    song_q_list = ALL_SONG_DATA[selected_song]
    current_q = song_q_list[st.session_state.current_q_index % len(song_q_list)]
    display_title = selected_song
    total_q_count = len(song_q_list)

# Main UI
col_info1, col_info2 = st.columns([2, 1])
with col_info1:
    st.markdown(f"#### 🎧 현재 곡: **{display_title}**")
with col_info2:
    q_num = (st.session_state.current_q_index % total_q_count) + 1
    st.markdown(f"<div style='text-align: right;'><span class='stat-badge'>Q {q_num} / {total_q_count}</span></div>", unsafe_allow_html=True)

# Quiz Box
st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888888; font-weight: 600;'>가사의 빈칸 '___' 에 들어갈 단어는?</p>", unsafe_allow_html=True)
st.markdown(f'<div class="lyrics-box">"{current_q["lyrics"]}"</div>', unsafe_allow_html=True)

# User Input
user_input = st.text_input("정답 입력", placeholder="정답을 입력하고 [정답 확인]을 눌러보세요!", key=f"q_input_{st.session_state.current_q_index}")

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("힌트 / 정답 보기 💡"):
        st.info(f"🔑 **힌트**: {current_q['hint']}\n\n💡 **정답**: **{current_q['answer']}**")

with col2:
    check_btn = st.button("정답 확인 ✨")

if check_btn:
    if user_input.strip() == "":
        st.warning(f"가사를 입력해 주세요! (정답은 **'{current_q['answer']}'** 입니다)")
    else:
        norm_user = normalize_string(user_input)
        norm_answer = normalize_string(current_q["answer"])
        
        if norm_user == norm_answer:
            st.session_state.combo += 1
            added_score = 10 + (st.session_state.combo * 2)
            st.session_state.score += added_score
            st.success(f"🎉 **정답입니다! ('{current_q['answer']}')** (+{added_score}점 / 🔥 {st.session_state.combo} 콤보!)")
            st.balloons()
        else:
            st.session_state.combo = 0
            st.error(f"❌ 아쉬워요! 정답은 **'{current_q['answer']}'** 입니다.")

st.markdown('</div>', unsafe_allow_html=True)

# Bottom Controls
col_prev, col_next = st.columns(2)

with col_prev:
    if st.button("🔄 리셋"):
        st.session_state.score = 0
        st.session_state.combo = 0
        st.session_state.current_q_index = 0
        if selected_song == "✨ 전체 랜덤 (전곡 모드)":
            st.session_state.random_queue = generate_all_questions()
        st.rerun()

with col_next:
    if st.button("다음 문제로 ➡️"):
        st.session_state.current_q_index += 1
        st.rerun()
