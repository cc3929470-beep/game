import streamlit as st
import random
import re

# Page Config
st.set_page_config(
    page_title="fromis_9 가사맞추기 퀴즈",
    page_icon="🍀",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    * {
        font-family: 'Pretendard', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(180deg, #FFFDF0 0%, #FFF5F7 100%);
        color: #111111 !important;
    }
    
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

    p, span, label, .stMarkdown {
        color: #111111 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #111111 !important;
    }

    .stTextInput > div > div > input {
        border-radius: 14px !important;
        border: 2px solid #FFCCD5 !important;
        padding: 12px 16px !important;
        font-size: 1.1rem !important;
        color: #111111 !important;
        background-color: #FFFFFF !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #FF4D6D !important;
        box-shadow: 0 0 0 3px rgba(255, 77, 109, 0.2) !important;
    }

    .stButton > button, div[data-testid="stForm"] button {
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
    .stButton > button:hover, div[data-testid="stForm"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255, 107, 139, 0.4);
    }
    
    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #FFF9FA;
        border-right: 1px solid #FFE0E6;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 지정된 11개 곡 확장 데이터베이스
# ----------------------------------------------------
ALL_SONG_DATA = {
    "Vitamin ME": [
        {"lyrics": "I'ma make you happy, 달콤한 ___ fizz", "answer": "lemon", "hint": "상큼한 레몬 (영어)"},
        {"lyrics": "Got you feeling ___, ooh, ooh, ooh", "answer": "new", "hint": "새로운 느낌의 영단어"},
        {"lyrics": "톡 쏘는 탄산처럼 ___ 전해지는 걸", "answer": "찌릿", "hint": "전율이 느껴지는 느낌"},
        {"lyrics": "너를 위한 특별한 ___ 에너지", "answer": "비타민", "hint": "영양소 이름"}
    ],
    "하얀 그리움": [
        {"lyrics": "하얀 눈이 내려와 내 맘을 ___ 해", "answer": "아프게", "hint": "초성: ㅇㅍㄱ"},
        {"lyrics": "사라져 버린 눈처럼 그댄 ___ 흩어져", "answer": "눈물로", "hint": "초성: ㄴㅁㄹ"},
        {"lyrics": "소중했던 기억들이 ___ 번져가네", "answer": "다시", "hint": "Again"},
        {"lyrics": "차가운 겨울 바람에 널 ___ 본다", "answer": "부러", "hint": "외쳐 부르다"}
    ],
    "Supersonic": [
        {"lyrics": "속도를 높여 더 ___ 너에게 가고 있어", "answer": "빠르게", "hint": "초성: ㅂㄹㄱ"},
        {"lyrics": "Hit me up when you need some ___", "answer": "energy", "hint": "뜻: 에너지 (영어)"},
        {"lyrics": "너의 맘속으로 ___", "answer": "Supersonic", "hint": "곡 제목과 동일!"},
        {"lyrics": "한계 따위는 넘어서 ___ 순간", "answer": "지름길", "hint": "빠르게 지르는 길"}
    ],
    "DM": [
        {"lyrics": "좋아해 너를 ___ 말해 버릴까", "answer": "솔직하게", "hint": "초성: ㅅㅈㅎㄱ"},
        {"lyrics": "Doesn't matter ___ 숨길 수가 없는걸", "answer": "where", "hint": "장소를 뜻하는 영단어"},
        {"lyrics": "내 맘을 전해줘 ___", "answer": "DM", "hint": "다이렉트 메시지 약자"},
        {"lyrics": "새벽 세 시의 ___ 넘치는 마음", "answer": "감성", "hint": "마음의 결"}
    ],
    "Like You Better": [
        {"lyrics": "널 닮은 파도에 ___, I can go anywhere", "answer": "dive", "hint": "뛰어들다 (영어)"},
        {"lyrics": "I LIKE YOU BETTER, 널 ___이라 부를래", "answer": "내일", "hint": "오늘 다음 날"},
        {"lyrics": "점점 더 길어지는 ___ 그림자", "answer": "노을", "hint": "해질녘의 상징"}
    ],
    "from": [
        {"lyrics": "Dear darling 네 세상을 나로 가득히 ___ 수 있다면", "answer": "채울", "hint": "가득 채우다"},
        {"lyrics": "추운 겨울에 만나 ___ 여름까지", "answer": "뜨거운", "hint": "여름의 온도"},
        {"lyrics": "너에게 전하는 마지막 ___ 편지", "answer": "비밀", "hint": "숨겨진 것"}
    ],
    "너를 따라 너에게": [
        {"lyrics": "여기 문이 열리면 나는 너를 ___", "answer": "따라가", "hint": "뒤를 쫓아가는 행동"},
        {"lyrics": "하얀 ___처럼 네게 달려가고 있는 나를 향해서", "answer": "토끼", "hint": "귀여운 동물의 이름"},
        {"lyrics": "발자국 따라 거니는 ___ 길", "answer": "동화속", "hint": "이야기 속"}
    ],
    "Rewind": [
        {"lyrics": "시간을 돌려 ___ 순간으로", "answer": "그때 그", "hint": "초성: ㄱㄸ ㄱ"},
        {"lyrics": "다시 돌아가는 ___", "answer": "Rewind", "hint": "되돌리다라는 뜻의 제목"},
        {"lyrics": "거꾸로 흐르는 ___ 시계", "answer": "모래", "hint": "시간을 재는 도구"}
    ],
    "WE GO": [
        {"lyrics": "바람을 따라 ___ 나를 던져봐", "answer": "몸을", "hint": "초성: ㅁㅇ"},
        {"lyrics": "Come on and ___ with me", "answer": "WE GO", "hint": "곡 제목"},
        {"lyrics": "시원한 파도 소리 ___ 속으로", "answer": "바다", "hint": "넓고 푸른 곳"}
    ],
    "Stay This Way": [
        {"lyrics": "바람이 불어오는 ___ 타고", "answer": "언덕을", "hint": "초성: ㅇㄷㅇ"},
        {"lyrics": "우리만의 ___ 비밀이야", "answer": "여름은", "hint": "계절 이름"},
        {"lyrics": "노을빛 젖어드는 ___ 해변", "answer": "석양", "hint": "해 질 녘 지는 해"}
    ],
    "Sky Runner": [
        {"lyrics": "Fly high, you and I, Fly high in the ___", "answer": "sky", "hint": "하늘 (영어)"},
        {"lyrics": "We are sky runners, we'll never ___", "answer": "fall", "hint": "쓰러지다/떨어지다 (영어)"},
        {"lyrics": "구름 위를 달리는 ___ 발걸음", "answer": "가벼운", "hint": "무겁지 않은"}
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
if "show_hint" not in st.session_state:
    st.session_state.show_hint = False

# Header
st.markdown("""
<div class="header-card">
    <h1>🍀 fromis_9 가사맞추기</h1>
    <p>지정된 11개 인기곡 가사 맞추기 퀴즈!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### 🎵 곡 선택")
song_options = ["✨ 전체 랜덤 모드"] + list(ALL_SONG_DATA.keys())
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

if "last_mode" not in st.session_state or st.session_state.last_mode != selected_song:
    st.session_state.last_mode = selected_song
    st.session_state.current_q_index = 0
    st.session_state.show_hint = False
    if selected_song == "✨ 전체 랜덤 모드":
        st.session_state.random_queue = generate_all_questions()

if selected_song == "✨ 전체 랜덤 모드":
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
st.markdown("<p style='text-align: center; color: #555555; font-weight: 600;'>가사의 빈칸 '___' 에 들어갈 단어는?</p>", unsafe_allow_html=True)
st.markdown(f'<div class="lyrics-box">"{current_q["lyrics"]}"</div>', unsafe_allow_html=True)

# Form 구조
with st.form(key=f"quiz_form_{st.session_state.current_q_index}"):
    user_input = st.text_input("정답 입력", placeholder="정답을 입력하고 Enter 또는 [정답 확인]을 누르세요")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        submit_btn = st.form_submit_button("정답 확인 ✨")
    with col_btn2:
        hint_btn = st.form_submit_button("힌트 보기 💡")

if hint_btn:
    st.session_state.show_hint = True

if st.session_state.show_hint:
    st.info(f"🔑 **힌트**: {current_q['hint']}")

if submit_btn:
    if user_input.strip() == "":
        st.warning("가사를 입력해주세요!")
    else:
        norm_user = normalize_string(user_input)
        norm_answer = normalize_string(current_q["answer"])
        
        if norm_user == norm_answer:
            st.session_state.combo += 1
            added_score = 10 + (st.session_state.combo * 2)
            st.session_state.score += added_score
            st.success(f"🎉 **정답입니다!** (+{added_score}점 / 🔥 {st.session_state.combo} 콤보!)")
            st.balloons()
        else:
            st.session_state.combo = 0
            st.error(f"아쉬워요! 정답은 **'{current_q['answer']}'** 입니다.")

st.markdown('</div>', unsafe_allow_html=True)

# Bottom Controls
col_prev, col_next = st.columns(2)

with col_prev:
    if st.button("🔄 리셋"):
        st.session_state.score = 0
        st.session_state.combo = 0
        st.session_state.current_q_index = 0
        st.session_state.show_hint = False
        if selected_song == "✨ 전체 랜덤 모드":
            st.session_state.random_queue = generate_all_questions()
        st.rerun()

with col_next:
    if st.button("다음 문제로 ➡️"):
        st.session_state.current_q_index += 1
        st.session_state.show_hint = False
        st.rerun()
