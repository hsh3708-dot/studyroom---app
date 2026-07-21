import streamlit as st
import pandas as pd
from datetime import datetime

# 페이지 디자인 세팅 (스터디카페 키오스크 느낌)
st.set_page_config(
    page_title="2026 자기주도학습실 좌석 관리",
    page_icon="📚",
    layout="wide"
)

st.title("📚 2026학년도 자기주도학습실 좌석 현황판")
st.markdown("입구에서 QR 코드를 스캔한 후 **본인 학번/이름**을 입력하고 **원하는 좌석**을 선택해 입실/퇴실해 주세요.")

# --- 데이터 관리 (세션 메모리 관리) ---
# 전체 87석 (정독실 1~71, 스터디테이블 1~16)
if 'seats' not in st.session_state:
    all_seats = [str(i) for i in range(1, 72)] + [f"스터디-{i}" for i in range(1, 17)]
    st.session_state.seats = {s: {"status": "빈자리", "user": "", "time": ""} for s in all_seats}

# --- 상단: 입/퇴실 처리 키오스크 폼 ---
st.markdown("---")
st.subheader("📱 입실 / 퇴실 처리하기")

with st.form("check_form", clear_on_submit=False):
    col1, col2, col3 = st.columns([2, 1.5, 1])
    
    with col1:
        student_name = st.text_input("학번 및 이름 입력", placeholder="예: 20101 홍길동")
    
    with col2:
        # 드롭다운에서 선택 가능 여부 표기
        seat_options = []
        for seat_id, info in st.session_state.seats.items():
            if info["status"] == "빈자리":
                seat_options.append(f"{seat_id} (🟢 선택 가능)")
            else:
                seat_options.append(f"{seat_id} (🔴 {info['user']} 사용 중)")
                
        selected_option = st.selectbox("좌석 선택", seat_options)
        selected_seat_id = selected_option.split(" ")[0]  # 좌석 번호만 추출
        
    with col3:
        action = st.radio("구분", ["입실 🟢", "퇴실 🔴"], horizontal=True)

    submit_btn = st.form_submit_button("확인 및 등록하기", use_container_width=True)

    if submit_btn:
        if not student_name.strip():
            st.error("⚠️ 학번과 이름을 정확히 입력해주세요!")
        else:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_seat_info = st.session_state.seats[selected_seat_id]
            
            if "입실" in action:
                if current_seat_info["status"] == "사용중":
                    st.error(f"❌ {selected_seat_id}번 좌석은 이미 '{current_seat_info['user']}' 학생이 사용 중입니다!")
                else:
                    st.session_state.seats[selected_seat_id] = {
                        "status": "사용중",
                        "user": student_name,
                        "time": now_str
                    }
                    st.success(f"🎉 **{student_name}**님, **{selected_seat_id}**번 좌석 입실 완료! ({now_str})")
                    st.rerun()

            elif "퇴실" in action:
                if current_seat_info["status"] == "빈자리":
                    st.warning(f"⚠️ {selected_seat_id}번 좌석은 이미 빈자리입니다.")
                else:
                    st.session_state.seats[selected_seat_id] = {
                        "status": "빈자리",
                        "user": "",
                        "time": now_str
                    }
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
        # 사용 중인 좌석 (선택 불가 / 빨간색 블록)
        col.error(f"**석 {seat_key}**\n\n🔴 사용중\n\n({seat_info['user']})")
    else:
        # 이용 가능한 좌석 (선택 가능 / 초록색 블록)
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
