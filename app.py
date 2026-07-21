import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ⚠️ 본인의 구글 앱스 스크립트 웹 앱 URL을 입력하세요!
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyNRaRIwOmIKOOZh6-2aLIya4ZjQUlinv8lXkSyuUMn9hhcxlQ0tTOwAm62JH2TvVoDWw/exec"

# 페이지 세팅
st.set_page_config(
    page_title="2026 자기주도학습실 좌석 관리",
    page_icon="📚",
    layout="wide"
)

st.title("📚 2026학년도 자기주도학습실 실시간 좌석 배치도")
st.caption("입구 / 정수기 / 창문 위치를 확인하고 원하시는 좌석을 배치도에서 직접 선택해주세요.")

# --- 세션 상태 초기화 ---
if 'seats' not in st.session_state:
    # 1~71 정독실 + 스터디테이블 (1-1~1-4, 2-1~2-4, 3-1~3-4, 4-1~4-4)
    jeongdok = [str(i) for i in range(1, 72)]
    study = [f"{t}-{i}" for t in range(1, 5) for i in range(1, 5)]
    all_seats = jeongdok + study
    st.session_state.seats = {s: {"status": "빈자리", "user": "", "time": ""} for s in all_seats}

if 'selected_seat' not in st.session_state:
    st.session_state.selected_seat = None

# --- 좌석 클릭 함수 ---
def select_seat(seat_id):
    st.session_state.selected_seat = seat_id

# --- 상단: 선택한 좌석 입/퇴실 처리 키오스크 ---
st.markdown("---")
if st.session_state.selected_seat:
    s_id = st.session_state.selected_seat
    s_info = st.session_state.seats[s_id]
    
    st.info(f"📍 **현재 선택한 좌석: [{s_id}]번** | 상태: **{s_info['status']}** " + (f"({s_info['user']})" if s_info['user'] else ""))
    
    with st.form("check_in_out_form"):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            student_name = st.text_input("학번 및 이름 입력", value=s_info['user'] if s_info['status'] == "사용중" else "", placeholder="예: 20101 홍길동")
        with col2:
            in_btn = st.form_submit_button("🟢 입실 처리", use_container_width=True)
        with col3:
            out_btn = st.form_submit_button("🔴 퇴실 처리", use_container_width=True)

        if in_btn:
            if not student_name.strip():
                st.error("학번과 이름을 입력해주세요!")
            elif s_info["status"] == "사용중":
                st.error(f"{s_id}번 좌석은 이미 '{s_info['user']}' 학생이 사용 중입니다.")
            else:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.seats[s_id] = {"status": "사용중", "user": student_name, "time": now_str}
                # 구글 시트 전송
                try:
                    payload = {"timestamp": now_str, "student_id": student_name, "seat_no": s_id, "status": "입실"}
                    requests.post(WEB_APP_URL, json=payload)
                except:
                    pass
                st.success(f"🎉 {student_name}님, [{s_id}]번 좌석 입실 완료!")
                st.session_state.selected_seat = None
                st.rerun()

        if out_btn:
            if s_info["status"] == "빈자리":
                st.warning(f"{s_id}번 좌석은 이미 빈자리입니다.")
            else:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.seats[s_id] = {"status": "빈자리", "user": "", "time": now_str}
                # 구글 시트 전송
                try:
                    payload = {"timestamp": now_str, "student_id": student_name, "seat_no": s_id, "status": "퇴실"}
                    requests.post(WEB_APP_URL, json=payload)
                except:
                    pass
                st.info(f"🚪 [{s_id}]번 좌석 퇴실 완료!")
                st.session_state.selected_seat = None
                st.rerun()
else:
    st.warning("👉 아래 **배치도에서 원하시는 좌석 버튼**을 클릭하면 입실/퇴실을 진행할 수 있습니다.")

st.markdown("---")

# Helper 함수: 좌석 버튼 그리기
def render_seat_button(seat_id):
    info = st.session_state.seats.get(seat_id, {"status": "빈자리", "user": ""})
    is_used = (info["status"] == "사용중")
    label = f"{seat_id}\n(🔴{info['user']})" if is_used else f"{seat_id}\n(🟢가능)"
    
    # 스티커/버튼 형태
    if st.button(label, key=f"btn_{seat_id}", use_container_width=True):
        select_seat(seat_id)
        st.rerun()

# --- 자습실 배치도 시각화 ---

# 1. 입구 및 안내 구역
col_left_top, col_right_top = st.columns([1, 4])
with col_left_top:
    st.success("🚪 **출입문 / 입구**")
    st.info("🚰 **정수기 / 감독석**")
with col_right_top:
    st.write("🚶‍♂️ **메인 통로 / 엘리베이터 방향**")

st.markdown("---")

# 2. 메인 좌석 구역 (배치도 레이아웃)
st.subheader("📍 자습실 전체 좌석 배치도")

col_a, col_b, col_c, col_d = st.columns([2, 2, 3, 3])

with col_a:
    st.markdown("#### 🟦 서측 라인 (1~23)")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("남학생 구역")
        for i in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            render_seat_button(str(i))
    with c2:
        st.caption("여학생 구역")
        for i in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]:
            render_seat_button(str(i))

with col_b:
    st.markdown("#### 🟩 중앙 블록 A (24~43)")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("24~33번")
        for i in range(24, 34):
            render_seat_button(str(i))
    with c2:
        st.caption("34~43번")
        for i in range(34, 44):
            render_seat_button(str(i))

with col_c:
    st.markdown("#### ✏️ 스터디 테이블 (16석)")
    st.caption("자유 자율학습석 구역")
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        st.write("**테이블 1 & 3**")
        for t in ["1-1", "1-2", "1-3", "1-4", "3-1", "3-2", "3-3", "3-4"]:
            render_seat_button(t)
    with s_col2:
        st.write("**테이블 2 & 4**")
        for t in ["2-1", "2-2", "2-3", "2-4", "4-1", "4-2", "4-3", "4-4"]:
            render_seat_button(t)

with col_d:
    st.markdown("#### 🟨 동측 블록 B (44~71)")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("44~57번")
        for i in range(44, 58):
            render_seat_button(str(i))
    with c2:
        st.caption("58~71번")
        for i in range(58, 72):
            render_seat_button(str(i))

# 3. 창가 구역 안내
st.markdown("---")
st.info("🪟 **창문 구역 (하늘공원 방향)**")
