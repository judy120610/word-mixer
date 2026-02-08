import streamlit as st
import pandas as pd
from utils import shuffle_vocab

def run():
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="title-text">📝 직접 입력 모드</h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">단어와 뜻을 직접 입력하여 학습 리스트를 만듭니다.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 세션 상태 초기화 (feature_1 전용)
    if 'f1_shuffled_result' not in st.session_state:
        st.session_state['f1_shuffled_result'] = None

    # 입력 섹션
    with st.container():
        input_text = st.text_area("단어와 뜻을 입력하세요", 
                                 placeholder="apple 사과, 청사과\nbanana 바나나\ncherry 체리...",
                                 height=300,
                                 label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔀 무작위 섞기 실행", key="f1_shuffle_btn"):
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
                        st.session_state['f1_shuffled_result'] = shuffled
                    else:
                        st.session_state['f1_shuffled_result'] = None
                        st.error("⚠️ 조건을 만족하는 조합을 찾지 못했습니다. 단어를 더 추가해보세요.")

    # 결과가 세션 상태에 있는 경우 표시
    if st.session_state['f1_shuffled_result']:
        st.success("✨성공적으로 섞었습니다!")
        shuffled_items = st.session_state['f1_shuffled_result']
        
        # 결과 출력 섹션
        st.markdown("### 📋 섞인 결과")
        
        # 가독성을 높인 리스트 뷰
        result_html = ""
        for item in shuffled_items:
            result_html += f'<div class="shuffled-item">{item["val"]}</div>'
        st.markdown(result_html, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 표 형식으로 보기 토글
        if st.checkbox("📊 표 형식으로 보기", key="f1_view_table"):
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
