import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils import shuffle_vocab
import os

# Google Sheets 연결 설정
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
KEY_FILE = os.path.join(os.path.dirname(__file__), 'key', 'credentials.json')
SPREADSHEET_ID = '1nlA5L-ttu7eqdJozYGxgXceQhxKg53e2QKh5GzLsDR4'
SHEET_NAME = '시트1'

@st.cache_data(ttl=600)
def load_data_from_sheet():
    try:
        creds = None
        # 1. Try loading from Streamlit secrets (for deployment)
        if 'gcp_service_account' in st.secrets:
            secret_value = st.secrets['gcp_service_account']
            if isinstance(secret_value, dict):
                creds = ServiceAccountCredentials.from_json_keyfile_dict(secret_value, SCOPE)
            else:
                # If it's a string (e.g., raw JSON), parse it
                import json
                creds_dict = json.loads(secret_value)
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        
        # 2. Fallback to local file (for local development)
        elif os.path.exists(KEY_FILE):
            creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE, SCOPE)
        
        if not creds:
             st.error("GCP credentials not found. Please set 'gcp_service_account' in Streamlit secrets or provide 'key/credentials.json' locally.")
             return None

        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"구글 스프레드시트 연결 오류: {e}")
        return None

def run():
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="title-text">📅 구글 시트 모드</h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">날짜를 선택하여 저장된 단어를 불러옵니다.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 데이터 로드
    with st.spinner('구글 스프레드시트에서 데이터를 불러오는 중...'):
        df = load_data_from_sheet()

    if df is not None and not df.empty:
        # Day 컬럼 확인 및 고유값 추출
        if 'Day' in df.columns:
            days = sorted(df['Day'].unique())
            selected_day = st.selectbox("학습할 Day를 선택하세요", days)

            if st.button("🔀 불러오기 및 섞기", key="fnew_shuffle_btn"):
                # 선택된 Day의 데이터 필터링
                day_data = df[df['Day'] == selected_day]
                
                word_pairs = []
                for _, row in day_data.iterrows():
                    word = str(row.get('Word', '')).strip()
                    meaning = str(row.get('Meaning', '')).strip()
                    if word and meaning:
                        word_pairs.append([word, meaning])
                
                if len(word_pairs) < 5:
                    st.error(f"Day {selected_day}에 저장된 단어가 부족합니다 (최소 5개 필요).")
                else:
                    with st.spinner('✨ 데이터를 섞는 중...'):
                        shuffled = shuffle_vocab(word_pairs)
                        if shuffled:
                            st.session_state['fnew_shuffled_result'] = shuffled
                        else:
                            st.session_state['fnew_shuffled_result'] = None
                            st.error("⚠️ 조건을 만족하는 조합을 찾지 못했습니다.")
        else:
            st.error("'Day' 컬럼을 찾을 수 없습니다. 시트 헤더를 확인해주세요.")
    
    # 결과 표시 (feature_new 전용 세션 상태 사용)
    if 'fnew_shuffled_result' in st.session_state and st.session_state['fnew_shuffled_result']:
        st.success("✨성공적으로 불러와서 섞었습니다!")
        shuffled_items = st.session_state['fnew_shuffled_result']
        
        st.markdown("### 📋 섞인 결과")
        result_html = ""
        for item in shuffled_items:
            result_html += f'<div class="shuffled-item">{item["val"]}</div>'
        st.markdown(result_html, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.checkbox("📊 표 형식으로 보기", key="fnew_view_table"):
            table_data = []
            for item in shuffled_items:
                if item['type'] == 'W':
                    table_data.append({"영단어 (English)": item['val'], "뜻 (Meaning)": ""})
                else:
                    table_data.append({"영단어 (English)": "", "뜻 (Meaning)": item['val']})
            
            table_df = pd.DataFrame(table_data)
            table_df.index = table_df.index + 1
            st.table(table_df)
