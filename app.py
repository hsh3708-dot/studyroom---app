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

# 모바일 UI 커스텀 CSS (글자 색상 검정색 & 두껍게 설정)
st.markdown("""
<style>
    .seat-card-used {
        background-color: #FFEEDD;
        border: 2px solid #FF5555;
        border-radius: 8px;
        padding: 8px;
        text-align: center;
        margin-bottom: 6px;
        color: #000000 !important;
        font-weight: bold !important;
    }
    .seat-card-empty {
        background-color: #E8F5E9;
        border: 2px solid #4CAF50;
        border-radius: 8px;
        padding: 8px;
        text-align: center;
        margin-bottom: 6px;
        color: #000000 !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# 성별 좌석 이름 변환 함수
def get_display_seat_name(seat_id):
    if "-" in seat_id:  # 자유석 (1-1 ~ 4-4)
        return f"자유석 {seat_id}"
    
    try:
        num = int(seat_id)
        if (1 <= num <= 9) or (24 <= num <= 43):
            return f"남자{num}"
        else:
            return f"여자{num}"
    except:
        return f"{seat_id}번"

# --- 구글 시트에서 실시간 좌석 상태 불러오기 함수 ---
def fetch_realtime_seats():
    jeongdok = [str(i) for i in range(1, 72)]
    # 자유석 1-1 ~ 4-4 (총 16석) 키값 일치시킴
    study = [f"{t}-{i}" for t in range(1, 5) for i in range(1, 5)]
    seats_data = {s: {"status": "빈자리", "user": "", "time": ""} for s in (jeongdok + study)}
    
    try:
        response = requests.get(WEB_APP_URL, timeout=5)
        if response.status_code == 200:
            db_seats = response.json()
            for seat_id, info in db_seats.items():
                if seat_id in seats_data:
                    seats_data[seat_id] = info
    except Exception as e:
        pass
        
    return seats_data

# 항상 접속 시 최신 DB 상태 불러오기
st.session_state.seats = fetch_realtime_seats()

# --- 화면 헤더 ---
st.title("📚 2026학년도 하계 방학 좌석 신청")
st.markdown("<p style='font-size: 20px; font-weight: bold; color: #555555;'>먼저 본인의 학번과 이름을 입력한 후, 아래 배치도에서 좌석을 클릭하세요.</p>", unsafe_allow_html=True)

# --- 상단: 입/퇴실 처리 키오스크 폼 ---
st.markdown("---")
col_header_1, col_header_2 = st.columns([4, 1])
with col_header_1:
    st.subheader("📱 입실 / 퇴실 처리하기")
with col_header_2:
    if st.button("🔄 실시간 현황 새로고침", use_container_width=True):
        st.rerun()

# 🔔 세션 알림 메시지 출력
if 'msg_type' in st.session_state and 'msg_text' in st.session_state:
    if st.session_state.msg_type == "success":
        st.success(st.session_state.msg_text)
    elif st.session_state.msg_type == "error":
        st.error(st.session_state.msg_text)
    elif st.session_state.msg_type == "warning":
        st.warning(st.session_state.msg_text)
    elif st.session_state.msg_type == "info":
        st.info(st.session_state.msg_text)
    del st.session_state.msg_type
    del st.session_state.msg_text

with st.form("check_form", clear_on_submit=False):
    col1, col2, col3 = st.columns([2, 1.5, 1])
    
    with col1:
        student_name = st.text_input("학번 및 이름 입력(띄어쓰기 없이)", placeholder="예: 10224하선훈")
    
    with col2:
        seat_options = []
        for seat_id, info in st.session_state.seats.items():
            disp_name = get_display_seat_name(seat_id)
            if info["status"] == "빈자리":
                seat_options.append(f"{seat_id} [{disp_name}] (🟢 선택 가능)")
            else:
                seat_options.append(f"{seat_id} [{disp_name}] (🔴 {info['user']} 사용 중)")
                
        selected_option = st.selectbox("좌석 선택", seat_options)
        selected_seat_id = selected_option.split(" ")[0]
        
    with col3:
        action = st.radio("구분", ["입실 🟢", "퇴실 🔴"], horizontal=True)

    submit_btn = st.form_submit_button("확인 및 등록하기", use_container_width=True)

    if submit_btn:
        input_user = student_name.strip()
        
        if not input_user:
            st.session_state.msg_type = "error"
            st.session_state.msg_text = "⚠️ 학번과 이름을 정확히 입력해주세요!"
            st.rerun()
        else:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_seat_info = st.session_state.seats.get(selected_seat_id, {"status": "빈자리", "user": ""})
            status_text = "입실" if "입실" in action else "퇴실"
            disp_name = get_display_seat_name(selected_seat_id)
            
            # --- 1. 입실 처리 로직 ---
            if status_text == "입실":
                if current_seat_info["status"] == "사용중":
                    st.session_state.msg_type = "error"
                    st.session_state.msg_text = f"❌ [{disp_name}] 좌석은 이미 '{current_seat_info['user']}' 학생이 사용 중입니다!"
                    st.rerun()
                else:
                    try:
                        payload = {
                            "timestamp": now_str,
                            "student_id": input_user,
                            "seat_no": selected_seat_id,
                            "status": status_text
                        }
                        requests.post(WEB_APP_URL, json=payload, timeout=5)
                    except Exception as e:
                        pass
                        
                    st.session_state.msg_type = "success"
                    st.session_state.msg_text = f"🎉 **{input_user}**님, **[{disp_name}]** 좌석 입실 처리되었습니다! (입실시각: {now_str})"
                    st.rerun()

            # --- 2. 퇴실 처리 로직 ---
            elif status_text == "퇴실":
                if current_seat_info["status"] == "빈자리":
                    st.session_state.msg_type = "warning"
                    st.session_state.msg_text = f"⚠️ [{disp_name}] 좌석은 이미 빈자리입니다."
                    st.rerun()
                
                elif current_seat_info["user"].strip() != input_user:
                    st.session_state.msg_type = "error"
                    st.session_state.msg_text = f"❌ 퇴실 실패: [{disp_name}] 좌석은 현재 '**{current_seat_info['user']}**' 학생이 사용 중입니다. 본인이 사용 중인 좌석만 퇴실할 수 있습니다!"
                    st.rerun()
                
                else:
                    try:
                        payload = {
                            "timestamp": now_str,
                            "student_id": input_user,
                            "seat_no": selected_seat_id,
                            "status": status_text
                        }
                        requests.post(WEB_APP_URL, json=payload, timeout=5)
                    except Exception as e:
                        pass
                        
                    st.session_state.msg_type = "info"
                    st.session_state.msg_text = f"🚪 **{input_user}**님, **[{disp_name}]** 좌석 퇴실 처리되었습니다. 이용해 주셔서 감사합니다!"
                    st.rerun()

# --- 하단: 실시간 모바일 최적화 좌석 현황판 ---
st.markdown("---")
st.subheader("🖥️ 실시간 좌석 현황판")
st.caption("🟢 선택 가능 (빈자리) | 🔴 선택 불가 (사용 중)")

# 1. 정독실 구역 (1~71번)
st.markdown("### 📖 정독석 구역 (1∼9, 24∼43 = 남자 / 10∼23, 44∼71 = 여자)")

NUM_COLS = 5
jeongdok_list = [str(i) for i in range(1, 72)]
grid_cols = st.columns(NUM_COLS)

for idx, seat_key in enumerate(jeongdok_list):
    seat_info = st.session_state.seats.get(seat_key, {"status": "빈자리", "user": ""})
    col_idx = idx // 15 if idx // 15 < NUM_COLS else NUM_COLS - 1
    disp_name = get_display_seat_name(seat_key)
    
    with grid_cols[col_idx]:
        if seat_info["status"] == "사용중":
            st.markdown(f"<div class='seat-card-used'><b>{disp_name}</b><br>🔴 사용중<br>({seat_info['user']})</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='seat-card-empty'><b>{disp_name}</b><br>🟢 가능<br>(빈자리)</div>", unsafe_allow_html=True)

# 2. 자유석 구역 (1-1 ~ 4-4, 총 16석)
st.markdown("---")
st.markdown("### ✏️ 자유석 구역 (16석)")

study_list = [f"{t}-{i}" for t in range(1, 5) for i in range(1, 5)]
study_cols = st.columns(4)

for idx, seat_key in enumerate(study_list):
    seat_info = st.session_state.seats.get(seat_key, {"status": "빈자리", "user": ""})
    col_idx = idx // 4
    disp_name = get_display_seat_name(seat_key)
    
    with study_cols[col_idx]:
        if seat_info["status"] == "사용중":
            st.markdown(f"<div class='seat-card-used'><b>{disp_name}</b><br>🔴 사용중<br>({seat_info['user']})</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='seat-card-empty'><b>{disp_name}</b><br>🟢 가능<br>(빈자리)</div>", unsafe_allow_html=True)
