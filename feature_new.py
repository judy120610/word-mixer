import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from utils import shuffle_vocab
import os
import json
import re

# Google Sheets 연결 설정
# gspread 6.0.0 이상에서는 scope가 자동으로 처리되지만, 명시적으로 설정
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
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
                creds = Credentials.from_service_account_info(secret_value, scopes=SCOPES)
            else:
                # If it's a string (e.g., raw JSON), parse it
                try:
                    creds_dict = json.loads(secret_value)
                    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
                except json.JSONDecodeError:
                    st.error("Failed to parse GCP credentials from secrets. Ensure it is valid JSON.")
                    return None
        
        # 2. Fallback to local file (for local development)
        elif os.path.exists(KEY_FILE):
             creds = Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
        
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
    st.markdown('<h2 class="title-text">📅 Word Master 하이스트 전용</h2>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">날짜를 선택하여 저장된 단어를 불러옵니다.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 데이터 로드
    with st.spinner('구글 스프레드시트에서 데이터를 불러오는 중...'):
        df = load_data_from_sheet()

    if df is None:
        return

    if df.empty:
        st.warning("⚠️ 구글 시트에서 데이터를 불러왔지만 내용이 없습니다. 시트에 데이터가 있는지 확인해주세요.")
        return

    # Day 컬럼 확인 및 고유값 추출
    if 'Day' in df.columns:
        # Handle mixed data types and sorting
        unique_days = df['Day'].unique()
        # Filter out empty values
        unique_days = [d for d in unique_days if pd.notna(d) and str(d).strip() != '']
        
        def smart_sort_key(val):
            s = str(val)
            # Find numbers in the string (e.g., "Day 1" -> 1)
            nums = re.findall(r'\d+', s)
            if nums:
                return int(nums[0])
            # If valid integer
            try:
                return int(s)
            except ValueError:
                # Fallback: return infinity so they go to end, or just 0
                return float('inf')

        try:
            days = sorted(unique_days, key=smart_sort_key)
        except Exception:
            days = sorted(unique_days, key=lambda x: str(x))
            
        selected_days = st.multiselect("학습할 Day를 선택하세요 (최대 3개)", days, max_selections=3)

        if st.button("🔀 불러오기 및 섞기", key="fnew_shuffle_btn"):
            if not selected_days:
                st.warning("최소 하나의 Day를 선택해주세요.")
            else:
                # 선택된 Day의 데이터 필터링
                day_data = df[df['Day'].isin(selected_days)]
            
                word_pairs = []
                for _, row in day_data.iterrows():
                    word = str(row.get('Word', '')).strip()
                    meaning = str(row.get('Meaning', '')).strip()
                    if word and meaning:
                        word_pairs.append([word, meaning])
            
                if len(word_pairs) < 5:
                    st.error(f"선택한 Day {selected_days}에 저장된 단어가 부족합니다 (합계 최소 5개 필요).")
                else:
                    with st.spinner('✨ 데이터를 섞는 중...'):
                        shuffled = shuffle_vocab(word_pairs)
                        if shuffled:
                            st.session_state['fnew_shuffled_result'] = shuffled
                        else:
                            st.session_state['fnew_shuffled_result'] = None
                            st.error("⚠️ 조건을 만족하는 조합을 찾지 못했습니다.")
    else:
        st.error(f"⚠️ 'Day' 컬럼을 찾을 수 없습니다. (발견된 컬럼: {list(df.columns)})")
        st.info("구글 시트의 첫 번째 행(Header)에 'Day', 'Word', 'Meaning'이 정확히 입력되어 있는지 확인해주세요.")
    
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
