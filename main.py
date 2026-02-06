import streamlit as st
import random

def shuffle_vocab(word_pairs):
    items = []
    for i, (word, meaning) in enumerate(word_pairs):
        items.append({'val': word, 'type': 'W', 'id': i})
        items.append({'val': meaning, 'type': 'M', 'id': i})

    max_attempts = 2000 
    
    for _ in range(max_attempts):
        random.shuffle(items)
        result = []
        temp_pool = items[:]
        success = True
        
        while temp_pool:
            found_candidate = False
            # 매번 풀을 섞어서 다양한 조합 시도
            random.shuffle(temp_pool)
            
            for candidate in temp_pool:
                # 조건 1: 영단어 연속 최대 3개
                if candidate['type'] == 'W':
                    if len(result) >= 3 and all(r['type'] == 'W' for r in result[-3:]):
                        continue
                
                # 조건 2: 뜻 연속 최대 2개
                if candidate['type'] == 'M':
                    if len(result) >= 2 and all(r['type'] == 'M' for r in result[-2:]):
                        continue
                
                # 조건 3: 단어와 그 뜻은 최소 3개 이상 떨어져 있어야 함 (인덱스 차이 4 이상)
                # 현재 위치에 넣었을 때, 마지막 3개 중에 같은 id가 있으면 안됨
                last_ids = [r['id'] for r in result[-3:]]
                if candidate['id'] in last_ids:
                    continue
                
                result.append(candidate)
                temp_pool.remove(candidate)
                found_candidate = True
                break
            
            if not found_candidate:
                success = False
                break
        
        if success:
            return result
    return None

# UI 설정
st.set_page_config(
    page_title="Vocab Shuffler",
    page_icon="📚",
    layout="centered"
)

# Premium Style Injection
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

# UI Header
st.markdown('<div class="header-container">', unsafe_allow_html=True)
st.markdown('<h1 class="title-text">📚 Vocab Shuffler</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">영단어와 뜻을 무작위로 섞어 효율적인 학습 리스트를 만듭니다.</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar or Intro info
with st.expander("ℹ️ 섞기 규칙 안내"):
    st.markdown("""
    - **영단어(W)**: 연속 최대 3개까지만 배열
    - **뜻(M)**: 연속 최대 2개까지만 배열
    - **연관 쌍**: 단어와 그 뜻은 최소 3칸 이상 떨어짐
    """)

# 세션 상태 초기화
if 'shuffled_result' not in st.session_state:
    st.session_state['shuffled_result'] = None

# 입력 섹션
with st.container():
    input_text = st.text_area("단어와 뜻을 입력하세요", 
                             placeholder="apple 사과, 청사과\nbanana 바나나\ncherry 체리...",
                             height=300,
                             label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🔀 무작위 섞기 실행", key="shuffle_btn"):
    if not input_text.strip():
        st.warning("단어를 입력해주세요.")
    else:
        lines = input_text.strip().split('\n')
        word_pairs = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 공백(스페이스, 탭 등)을 기준으로 첫 번째만 분리
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                word_pairs.append([parts[0].strip(), parts[1].strip()])
            else:
                for delimiter in [':', '-', ',']:
                    if delimiter in line:
                        word_pairs.append([p.strip() for p in line.split(delimiter, 1)])
                        break
        
        if len(word_pairs) < 5:
            st.error("조건을 만족시키기 위해 최소 5개 이상의 단어 쌍이 필요합니다.")
        else:
            with st.spinner('✨ 최적의 조합을 생성하는 중...'):
                shuffled = shuffle_vocab(word_pairs)
                if shuffled:
                    st.session_state['shuffled_result'] = shuffled
                else:
                    st.session_state['shuffled_result'] = None
                    st.error("⚠️ 조건을 만족하는 조합을 찾지 못했습니다. 단어를 더 추가해보세요.")

# 결과가 세션 상태에 있는 경우 표시
if st.session_state['shuffled_result']:
    st.success("✨성공적으로 섞었습니다!")
    shuffled_items = st.session_state['shuffled_result']
    
    # 결과 출력 섹션
    st.markdown("### 📋 섞인 결과")
    
    # 가독성을 높인 리스트 뷰
    result_html = ""
    for item in shuffled_items:
        result_html += f'<div class="shuffled-item">{item["val"]}</div>'
    st.markdown(result_html, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 표 형식으로 보기 토글
    if st.checkbox("📊 표 형식으로 보기"):
        import pandas as pd
        
        # 순서대로 테이블 데이터 생성
        table_data = []
        for item in shuffled_items:
            if item['type'] == 'W':
                table_data.append({
                    "영단어 (English)": item['val'],
                    "뜻 (Meaning)": ""
                })
            else:
                table_data.append({
                    "영단어 (English)": "",
                    "뜻 (Meaning)": item['val']
                })
        
        df = pd.DataFrame(table_data)
        
        # 인덱스를 1부터 시작하도록 설정
        df.index = df.index + 1
        st.table(df)
