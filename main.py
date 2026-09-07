import streamlit as st
import random

# Page Config
st.set_page_config(
    page_title="Vitamin Flo: fromis_9 Song Quiz",
    page_icon="🍋",
    layout="centered"
)

# Custom CSS for 'Vitamin Me' Aesthetic (Bright, Fresh, Pastel)
st.markdown("""
<style>
    /* Main Background & Text Color */
    .stApp {
        background-color: #FFFDF0;
        color: #2D3142;
        font-family: 'Pretendard', sans-serif;
    }
    
    /* Header Card */
    .header-card {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 99%, #FECFEF 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0px 8px 16px rgba(255, 154, 158, 0.2);
        margin-bottom: 2rem;
        color: white;
    }
    .header-card h1 {
        color: #FFFFFF !important;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    /* Quiz Card Container */
    .quiz-card {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 24px;
        border: 2px solid #FFE5EC;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.03);
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .lyrics-box {
        background-color: #FFF0F3;
        padding: 1.5rem;
        border-radius: 16px;
        font-size: 1.25rem;
        font-weight: 600;
        color: #FF4D6D;
        line-height: 1.8;
        margin: 1rem 0;
        letter-spacing: 0.5px;
    }

    /* Buttons Style */
    .stButton>button {
        background: linear-gradient(135deg, #FF85A1 0%, #FFA6C1 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 10px rgba(255, 133, 161, 0.3);
        transition: all 0.2s ease-in-out;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(255, 133, 161, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# 퀴즈 데이터베이스 (추가 가능)
SONG_DATA = {
    "Supersonic": [
        {"lyrics": "속도를 높여 더 ___ 너에게 가고 있어", "answer": "빠르게", "hint": "ㅂㄹㄱ"},
        {"lyrics": "Hit me up when you need some ___", "answer": "energy", "hint": "에너지"},
        {"lyrics": "너의 맘속으로 ___", "answer": "Supersonic", "hint": "곡 제목과 동일!"}
    ],
    "DM": [
        {"lyrics": "좋아해 너를 ___ 말해 버릴까", "answer": "솔직하게", "hint": "ㅅㅈㅎㄱ"},
        {"lyrics": "Doesn't matter ___ 숨길 수가 없는걸", "answer": "where", "hint": "장소를 뜻하는 영어"},
        {"lyrics": "내 맘을 전해줘 ___", "answer": "DM", "hint": "인스타 다이렉트 메시지"}
    ],
    "WE GO": [
        {"lyrics": "바람을 따라 ___ 나를 던져봐", "answer": "몸을", "hint": "ㅁㅇ"},
        {"lyrics": "Come on and ___ with me", "answer": "WE GO", "hint": "곡 제목"},
        {"lyrics": "망설이지 마 ___", "answer": "Right now", "hint": "지금 당장 (영어)"}
    ],
    "LOVE BOMB": [
        {"lyrics": "터진 듯해 ___ LOVE BOMB", "answer": "내 맘속에", "hint": "ㄴ ㅁㅅㅇ"},
        {"lyrics": "어쩌나 터져 버린 ___", "answer": "LOVE BOMB", "hint": "곡 제목"},
        {"lyrics": "조금씩 타들어 가 ___", "answer": "심장에", "hint": "ㅅㅈㅇ"}
    ]
}

# Session State 초기화
if "score" not in st.session_state:
    st.session_state.score = 0
if "current_q" not in st.session_state:
    st.session_state.current_q = 0

# Header
st.markdown("""
<div class="header-card">
    <h1>🍋 Vitamin Flo</h1>
    <p>프로미스나인 가사 맞추기 비타민 퀴즈</p>
</div>
""", unsafe_allow_html=True)

# 곡 선택 Sidebar
st.sidebar.title("🎵 곡 선택")
selected_song = st.sidebar.selectbox("플레이할 곡을 골라주세요!", list(SONG_DATA.keys()))

# 선택한 곡에 따라 퀴즈 세팅
quiz_list = SONG_DATA[selected_song]

# Main Quiz Interface
st.markdown(f"### 🎧 현재 곡: **{selected_song}**")

# 진행 상황 바
progress = (st.session_state.current_q + 1) / len(quiz_list)
st.progress(progress)

q_data = quiz_list[st.session_state.current_q]

st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
st.markdown(f"**Question {st.session_state.current_q + 1}**")
st.markdown(f'<div class="lyrics-box">"{q_data["lyrics"]}"</div>', unsafe_allow_html=True)

# 사용자 입력
user_answer = st.text_input("빈칸에 들어갈 가사는 무엇일까요?", key=f"q_{st.session_state.current_q}")

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("힌트 보기 💡"):
        st.info(f"힌트: {q_data['hint']}")

with col2:
    if st.button("정답 확인 ✨"):
        if user_answer.strip().lower() == q_data["answer"].lower():
            st.success("🎉 정답입니다! 톡톡 튀는 비타민 충전 완료!")
            st.session_state.score += 10
        else:
            st.error(f"아쉬워요! 정답은 **'{q_data['answer']}'** 입니다.")

st.markdown('</div>', unsafe_allow_html=True)

# 다음 문제 / 리셋 버튼
st.divider()
c1, c2 = st.columns(2)
with c1:
    if st.button("다음 문제로 ➡️"):
        if st.session_state.current_q < len(quiz_list) - 1:
            st.session_state.current_q += 1
            st.rerun()
        else:
            st.balloons()
            st.success(f"🏆 모든 문제를 풀었습니다! 최종 점수: {st.session_state.score}점")
            
with c2:
    if st.button("처음부터 다시하기 🔄"):
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.rerun()
