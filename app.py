import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ⚠️ 본인의 구글 앱스 스크립트 웹 앱 URL을 붙여넣으세요!
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyNRaRIwOmIKOOZh6-2aLIya4ZjQUlinv8lXkSyuUMn9hhcxlQ0tTOwAm62JH2TvVoDWw/exec"

# 페이지 디자인 세팅
st.set_page_config(
    page_title="2026 자기주도학습실 좌석 관리",
    page_icon="📚",
    layout="wide"
)

# --- [핵심] 구글 시트에서 실시간 좌석 상태 불러오기 함수 ---
def fetch_realtime_seats():
    # 기본 87개 좌석 데이터 구조 세팅
    jeongdok = [str(i) for i in range(1, 72)]
    study = [f"스터디-{i}" for i in range(1, 17)]
    seats_data = {s: {"status": "빈자리", "user": "", "time": ""} for s in (jeongdok + study)}
    
    try:
        # 구글 앱스 스크립트(GET)를 통해 구글 시트의 최신 현황 수신
        response = requests.get(WEB_APP_URL, timeout=5)
        if response.status_code == 200:
            db_seats = response.json()
            for seat_id, info in db_seats.items():
                if seat_id in seats_data:
                    seats_data[seat_id] = info
    except Exception as e:
        pass  # 통신 에러 발생 시 기본값 유지
        
    return seats_data

# 페이지 진입 시 항상 구글 시트의 최신 데이터로 실시간 상태 업데이트
st.session_state.seats = fetch_realtime_seats()

# --- 화면 헤더 ---
st.title("📚 2026학년도 자기주도학습실 좌석 현황판")
st.markdown("입구에서 QR 코드를 스캔한 후 **본인 학번/이름**을 입력하고 **원하는 좌석**을 선택해 입실/퇴실해 주세요.")

# --- 상단: 입/퇴실 처리 키오스크 폼 ---
st.markdown("---")
col_header_1, col_header_2 = st.columns([4, 1])
with col_header_1:
    st.subheader("📱 입실 / 퇴실 처리하기")
with col_header_2:
    # 실시간 현황 수동 수신 버튼
    if st.button("🔄 실시간 현황 새로고침", use_container_width=True):
        st.rerun()

with st.form("check_form", clear_on_submit=False):
    col1, col2, col3 = st.columns([2, 1.5, 1])
    
    with col1:
        student_name = st.text_input("학번 및 이름 입력", placeholder="예: 20101 홍길동")
    
    with col2:
        seat_options = []
        for seat_id, info in st.session_state.seats.items():
            if info["status"] == "빈자리":
                seat_options.append(f"{seat_id} (🟢 선택 가능)")
            else:
                seat_options.append(f"{seat_id} (🔴 {info['user']} 사용 중)")
                
        selected_option = st.selectbox("좌석 선택", seat_options)
        selected_seat_id = selected_option.split(" ")[0]
        
    with col3:
        action = st.radio("구분", ["입실 🟢", "퇴실 🔴"], horizontal=True)

    submit_btn = st.form_submit_button("확인 및 등록하기", use_container_width=True)

    if submit_btn:
        if not student_name.strip():
            st.error("⚠️ 학번과 이름을 정확히 입력해주세요!")
        else:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_seat_info = st.session_state.seats[selected_seat_id]
            
            status_text = "입실" if "입실" in action else "퇴실"
            
            if status_text == "입실":
                if current_seat_info["status"] == "사용중":
                    st.error(f"❌ {selected_seat_id}번 좌석은 이미 '{current_seat_info['user']}' 학생이 사용 중입니다!")
                else:
                    # 구글 스프레드시트로 기록 전송 (POST)
                    try:
                        payload = {
                            "timestamp": now_str,
                            "student_id": student_name,
                            "seat_no": selected_seat_id,
                            "status": status_text
                        }
                        requests.post(WEB_APP_URL, json=payload, timeout=5)
                    except Exception as e:
                        pass
                        
                    st.success(f"🎉 **{student_name}**님, **{selected_seat_id}**번 좌석 입실 완료! ({now_str})")
                    st.rerun()

            elif status_text == "퇴실":
                if current_seat_info["status"] == "빈자리":
                    st.warning(f"⚠️ {selected_seat_id}번 좌석은 이미 빈자리입니다.")
                else:
                    # 구글 스프레드시트로 기록 전송 (POST)
                    try:
                        payload = {
                            "timestamp": now_str,
                            "student_id": student_name,
                            "seat_no": selected_seat_id,
                            "status": status_text
                        }
                        requests.post(WEB_APP_URL, json=payload, timeout=5)
                    except Exception as e:
                        pass
                        
                    st.info(f"🚪 **{selected_seat_id}**번 좌석 퇴실 처리되었습니다. 이용해 주셔서 감사합니다.")
                    st.rerun()

# --- 하단: 실시간 스터디카페 좌석 현황판 ---
st.markdown("---")
st.subheader("🖥️ 실시간 좌석 배치도")
st.caption("🟢 선택 가능 (빈자리) | 🔴 선택 불가 (사용 중)")

# 1. 정독실 구역 (1~71번)
st.markdown("### 📖 정독실 구역 (71석)")
cols_jeongdok = st.columns(10)
for i in range(1, 72):
    seat_key = str(i)
    seat_info = st.session_state.seats[seat_key]
    col = cols_jeongdok[(i - 1) % 10]
    
    if seat_info["status"] == "사용중":
        col.error(f"**석 {seat_key}**\n\n🔴 사용중\n\n({seat_info['user']})")
    else:
        col.success(f"**석 {seat_key}**\n\n🟢 가능\n\n(빈자리)")

# 2. 스터디 테이블 구역 (1~16번)
st.markdown("---")
st.markdown("### ✏️ 스터디 테이블 구역 (16석)")
cols_study = st.columns(8)
for i in range(1, 17):
    seat_key = f"스터디-{i}"
    seat_info = st.session_state.seats[seat_key]
    col = cols_study[(i - 1) % 8]
    
    if seat_info["status"] == "사용중":
        col.error(f"**{i}**\n\n🔴 사용중\n\n({seat_info['user']})")
    else:
        col.success(f"**{i}**\n\n🟢 가능\n\n(빈자리)")
