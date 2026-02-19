import streamlit as st
from streamlit_autorefresh import st_autorefresh

# 앱이 열려 있을 때 15분마다 자동으로 새로고침하여 연결을 유지함
st_autorefresh(interval=15 * 60 * 1000, key="keepalive")

st.title("24/7 가동 중인 앱")
st.write("이 앱은 6시간마다 GitHub Actions로부터 신호를 받고 있습니다.")
