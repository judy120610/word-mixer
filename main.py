import streamlit as st
import feature_1
import feature_new

# UI 설정
st.set_page_config(
    page_title="Vocab Shuffler",
    page_icon="📚",
    layout="centered"
)

# Premium Style Injection (공통 스타일)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px);
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        padding: 15px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.3) !important;
        height: 50px;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(118, 75, 162, 0.4) !important;
    }

    .shuffled-item {
        padding: 10px 15px;
        margin-bottom: 8px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #764ba2;
        font-weight: 400;
        color: #333;
    }

    .header-container {
        text-align: center;
        padding: 2rem 0;
    }

    .title-text {
        font-weight: 600;
        font-size: 2.5rem;
        color: #2D3436;
        margin-bottom: 0.5rem;
    }

    .subtitle-text {
        font-weight: 300;
        color: #636E72;
        margin-bottom: 2rem;
    }
    
    .status-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        border: 1px solid #eef;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.title("메뉴 선택")
    page = st.radio("기능을 선택하세요:", ["직접 입력 모드", "구글 시트 모드(Word Master 하이스트 전용)"])
    
    st.markdown("---")
    with st.expander("ℹ️ 섞기 규칙 안내"):
        st.markdown("""
        - **영단어(W)**: 연속 최대 3개까지만 배열
        - **뜻(M)**: 연속 최대 2개까지만 배열
        - **연관 쌍**: 단어와 그 뜻은 최소 3칸 이상 떨어짐
        """)

# Page Routing
if page == "직접 입력 모드":
    feature_1.run()
elif page == "구글 시트 모드":
    feature_new.run()
