import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ⚠️ 본인의 구글 앱스 스크립트 웹 앱 URL을 입력하세요!
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyNRaRIwOmIKOOZh6-2aLIya4ZjQUlinv8lXkSyuUMn9hhcxlQ0tTOwAm62JH2TvVoDWw/exec"

st.set_page_config(
    page_title="2026 자기주도학습실 좌석 배치도",
    page_icon="📚",
    layout="wide"
)

st.title("📚 2026학년도 자기주도학습실 실시간 좌석 현황")
st.caption("실제 자습실 배치도와 동일한 화면입니다. 원하시는 좌석 버튼을 클릭하여 입/퇴실을 진행해 주세요.")

# --- 세션 상태 초기화 ---
if 'seats' not in st.session_state:
    jeongdok = [str(i) for i in range(1, 72)]
    study = [f"{t}-{i}" for t in range(1, 5) for i in range(1, 5)]
    all_seats = jeongdok + study
    st.session_state.seats = {s: {"status": "빈자리", "user": "", "time": ""} for s in all_seats}

if 'selected_seat' not in st.session_state:
    st.session_state.selected_seat = None

def select_seat(seat_id):
    st.session_state.selected_seat = seat_id

def render_seat(seat_id):
    info = st.session_state.seats.get(seat_id, {"status": "빈자리", "user": ""})
    is_used = (info["status"] == "사용중")
    
    # 좌석 유형 구분 (스터디 vs 정독실)
    display_id = f"S{seat_id}" if "-" in seat_id else f"{seat_id}번"
    label = f"{display_id}\n🔴{info['user']}" if is_used else f"{display_id}\n🟢가능"
    
    if st.button(label, key=f"btn_{seat_id}", use_container_width=True):
        select_seat(seat_id)
        st.rerun()

# --- 상단: 입/퇴실 등록 키오스크 ---
st.markdown("---")
if st.session_state.selected_seat:
    s_id = st.session_state.selected_seat
    s_info = st.session_state.seats[s_id]
    
    st.info(f"📍 **선택된 좌석: [{s_id}]번** | 상태: **{s_info['status']}** " + (f"({s_info['user']})" if s_info['user'] else ""))
    
    with st.form("check_in_out_form"):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            student_name = st.text_input("학번 및 이름 입력", value=s_info['user'] if s_info['status'] == "사용중" else "", placeholder="예: 20101 홍길동")
        with col2:
            in_btn = st.form_submit_button("🟢 입실하기", use_container_width=True)
        with col3:
            out_btn = st.form_submit_button("🔴 퇴실하기", use_container_width=True)

        if in_btn:
            if not student_name.strip():
                st.error("학번과 이름을 입력해주세요!")
            elif s_info["status"] == "사용중":
                st.error(f"{s_id}번 좌석은 이미 '{s_info['user']}' 학생이 사용 중입니다.")
            else:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.seats[s_id] = {"status": "사용중", "user": student_name, "time": now_str}
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
                try:
                    payload = {"timestamp": now_str, "student_id": student_name, "seat_no": s_id, "status": "퇴실"}
                    requests.post(WEB_APP_URL, json=payload)
                except:
                    pass
                st.info(f"🚪 [{s_id}]번 좌석 퇴실 완료!")
                st.session_state.selected_seat = None
                st.rerun()
else:
    st.warning("👉 아래 **배치도에서 원하시는 좌석 버튼**을 클릭하면 입/퇴실을 할 수 있습니다.")

st.markdown("---")

# --- REAL 배치도 시각화 (PDF 1:1 구현) ---

# 1. 자습실 입구 및 상단 시설
top_c1, top_c2, top_c3 = st.columns([2, 5, 2])
with top_c1:
    st.error("🚪 **출입문 / 입구**")
    st.info("🚰 **정수기 / 감독석**")
with top_c2:
    st.markdown("### 🚶‍♂️ 메인 통로 (엘리베이터 방향)")
with top_c3:
    st.error("🚪 **출입문**")

st.markdown("---")

# 2. 본관 배치 메인 그리드 (5개 세로 구역)
# [좌측 1~23] [중앙 24~43] [스터디테이블] [우측 44~71]
c_left, c_mid_1, c_study, c_mid_2 = st.columns([2, 2, 3, 3])

# --- [좌측 구역: 1~23번 (남/여 구역)] ---
with c_left:
    st.markdown("#### 🟦 남, 여 내부 구역 (1~23)")
    l_c1, l_c2 = st.columns(2)
    with l_c1:
        st.caption("남학생 내부")
        for i in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            render_seat(str(i))
    with l_c2:
        st.caption("여학생 내부")
        for i in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]:
            render_seat(str(i))

# --- [남학생 외부 구역 A: 24~43번] ---
with c_mid_1:
    st.markdown("#### 🟩 중앙 지정석 (24~43)")
    m1_c1, m1_c2 = st.columns(2)
    with m1_c1:
        st.caption("24~33번 라인")
        for i in range(24, 34):
            render_seat(str(i))
    with m1_c2:
        st.caption("34~43번 라인")
        for i in range(34, 44):
            render_seat(str(i))

# --- [중앙 스터디 테이블 16석: 1-1~4-4] ---
with c_study:
    st.markdown("#### ✏️ 스터디 테이블 (16석)")
    st.caption("자유 자율학습 공간")
    
    st.write("**[테이블 1]**")
    t1_c1, t1_c2 = st.columns(2)
    with t1_c1: render_seat("1-1"); render_seat("1-3")
    with t1_c2: render_seat("1-2"); render_seat("1-4")
    
    st.write("**[테이블 2]**")
    t2_c1, t2_c2 = st.columns(2)
    with t2_c1: render_seat("2-1"); render_seat("2-3")
    with t2_c2: render_seat("2-2"); render_seat("2-4")
    
    st.write("**[테이블 3]**")
    t3_c1, t3_c2 = st.columns(2)
    with t3_c1: render_seat("3-1"); render_seat("3-3")
    with t3_c2: render_seat("3-2"); render_seat("3-4")
    
    st.write("**[테이블 4]**")
    t4_c1, t4_c2 = st.columns(2)
    with t4_c1: render_seat("4-1"); render_seat("4-3")
    with t4_c2: render_seat("4-2"); render_seat("4-4")

# --- [여학생 외부 구: 44~71번] ---
with c_mid_2:
    st.markdown("#### 🟨 동측 지정석 (44~71)")
    m2_c1, m2_c2 = st.columns(2)
    with m2_c1:
        st.caption("44~57번 라인")
        for i in range(44, 58):
            render_seat(str(i))
    with m2_c2:
        st.caption("58~71번 라인")
        for i in range(58, 72):
            render_seat(str(i))

# 3. 하단 창가 구조
st.markdown("---")
st.success("🪟 **창문 구역 (하늘공원 방향)** | 🏛️ 기둥 위치 고려됨")
