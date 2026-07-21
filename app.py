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

# 좌석 버튼 커스텀 스타일 (실제 도면 모양에 맞춤)
st.markdown("""
<style>
    div.stButton > button {
        padding: 4px 2px !important;
        font-size: 13px !important;
        font-weight: bold !important;
        margin-bottom: 2px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📚 2026학년도 하계 방학 좌석 신청")
st.caption("좌석 배치도를 참고하여, 좌석을 직접 클릭한 후 입/퇴실을 꼭 진행하세요.")

# --- 데이터 초기화 ---
if 'seats' not in st.session_state:
    jeongdok = [str(i) for i in range(1, 72)]
    study = [f"{t}-{i}" for t in range(1, 5) for i in range(1, 5)]
    st.session_state.seats = {s: {"status": "빈자리", "user": "", "time": ""} for s in (jeongdok + study)}

if 'selected_seat' not in st.session_state:
    st.session_state.selected_seat = None

def select_seat(seat_id):
    st.session_state.selected_seat = seat_id

def render_seat(seat_id):
    info = st.session_state.seats.get(seat_id, {"status": "빈자리", "user": ""})
    is_used = (info["status"] == "사용중")
    label = f"{seat_id}\n🔴{info['user']}" if is_used else f"{seat_id}\n🟢가능"
    
    if st.button(label, key=f"btn_{seat_id}", use_container_width=True):
        select_seat(seat_id)
        st.rerun()

# --- 상단: 입/퇴실 등록 키오스크 폼 ---
if st.session_state.selected_seat:
    s_id = st.session_state.selected_seat
    s_info = st.session_state.seats[s_id]
    
    st.info(f"📍 **선택된 좌석: [{s_id}]** | 현재 상태: **{s_info['status']}** " + (f"({s_info['user']})" if s_info['user'] else ""))
    
    with st.form("check_in_out_form"):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            student_name = st.text_input("학번 및 이름 입력", value=s_info['user'] if s_info['status'] == "사용중" else "", placeholder="예: 10224 하선훈")
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
                except: pass
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
                except: pass
                st.info(f"🚪 [{s_id}]번 좌석 퇴실 완료!")
                st.session_state.selected_seat = None
                st.rerun()
else:
    st.warning("👉 아래 **배치도에서 원하시는 좌석 버튼**을 직접 클릭하세요.")

st.markdown("---")

# --- 1. 상단 출입구 및 통로 시설 ---
top_1, top_2, top_3, top_4, top_5 = st.columns([1.5, 4, 2, 4, 1.5])
with top_1: st.success("🚪 입구 / 정수기 / 감독석")
with top_2: st.markdown("<h4 style='text-align: center;'>🚶‍♂️ 통로</h4>", unsafe_allow_html=True)
with top_3: st.info("🛗 엘리베이터")
with top_4: st.markdown("<h4 style='text-align: center;'>🚶‍♂️ 통로</h4>", unsafe_allow_html=True)
with top_5: st.success("🚪 입구")

st.markdown("---")

# --- 2. 메인 배치도 영역 (도면 100% 반영) ---
# 영역 비율: [서측(1~23)] [남학생(24~43)] [스터디] [여학생(44~71)]
col_sec1, col_sec2, col_sec3, col_sec4 = st.columns([2.5, 3, 2.5, 4])

# ==========================================
# [구역 1] 서측 라인 (1~23번)
# ==========================================
with col_sec1:
    st.markdown("#### 🟦 서측 라인 (1~23)")
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    
    with c1:
        st.caption("남")
        for i in range(1, 6): render_seat(str(i))
    with c2:
        st.caption("남")
        for i in range(6, 10): render_seat(str(i))
    with c3:
        st.caption("여")
        for i in range(10, 17): render_seat(str(i))
    with c4:
        st.caption("여")
        for i in range(17, 24): render_seat(str(i))

# ==========================================
# [구역 2] 남학생 외부 구역 (24~43번)
# ==========================================
with col_sec2:
    st.markdown("#### 🟩 남학생 구역 (24~43)")
    
    # 🏛️ 상단 기둥
    st.caption("🏛️ 기둥")
    
    # Block 1: [24, 25] | [26, 27, 28]
    b1_c1, b1_c2 = st.columns([2, 3])
    with b1_c1:
        rc1, rc2 = st.columns(2)
        with rc1: render_seat("24")
        with rc2: render_seat("25")
    with b1_c2:
        rc1, rc2, rc3 = st.columns(3)
        with rc1: render_seat("26")
        with rc2: render_seat("27")
        with rc3: render_seat("28")
        
    st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True) # 가로 통로
    
    # Block 2: [29, 30] | [31, 32, 33]
    b2_c1, b2_c2 = st.columns([2, 3])
    with b2_c1:
        rc1, rc2 = st.columns(2)
        with rc1: render_seat("29")
        with rc2: render_seat("30")
    with b2_c2:
        rc1, rc2, rc3 = st.columns(3)
        with rc1: render_seat("31")
        with rc2: render_seat("32")
        with rc3: render_seat("33")

    st.markdown("---") # 메인 중앙 가로 통로

    # Block 3: [34, 35] | [36, 37, 38]
    b3_c1, b3_c2 = st.columns([2, 3])
    with b3_c1:
        rc1, rc2 = st.columns(2)
        with rc1: render_seat("34")
        with rc2: render_seat("35")
    with b3_c2:
        rc1, rc2, rc3 = st.columns(3)
        with rc1: render_seat("36")
        with rc2: render_seat("37")
        with rc3: render_seat("38")

    st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True) # 가로 통로

    # Block 4: [39, 40] | [41, 42, 43]
    b4_c1, b4_c2 = st.columns([2, 3])
    with b4_c1:
        rc1, rc2 = st.columns(2)
        with rc1: render_seat("39")
        with rc2: render_seat("40")
    with b4_c2:
        rc1, rc2, rc3 = st.columns(3)
        with rc1: render_seat("41")
        with rc2: render_seat("42")
        with rc3: render_seat("43")

# ==========================================
# [구역 3] 스터디 테이블 (1-1 ~ 4-4)
# ==========================================
with col_sec3:
    st.markdown("#### ✏️ 스터디 테이블 (16석)")
    
    # 테이블 1 & 2 상단
    st.caption("테이블 1 & 2")
    t12_c1, t12_c2 = st.columns(2)
    with t12_c1:
        r1, r2 = st.columns(2)
        with r1: render_seat("1-1"); render_seat("1-3")
        with r2: render_seat("1-2"); render_seat("1-4")
    with t12_c2:
        r1, r2 = st.columns(2)
        with r1: render_seat("2-1"); render_seat("2-3")
        with r2: render_seat("2-2"); render_seat("2-4")

    st.markdown("---") # 메인 중앙 가로 통로

    # 테이블 3 & 4 하단
    st.caption("테이블 3 & 4")
    t34_c1, t34_c2 = st.columns(2)
    with t34_c1:
        r1, r2 = st.columns(2)
        with r1: render_seat("3-1"); render_seat("3-3")
        with r2: render_seat("3-2"); render_seat("3-4")
    with t34_c2:
        r1, r2 = st.columns(2)
        with r1: render_seat("4-1"); render_seat("4-3")
        with r2: render_seat("4-2"); render_seat("4-4")

# ==========================================
# [구역 4] 여학생 외부 구역 (44~71번)
# ==========================================
with col_sec4:
    st.markdown("#### 🟧 여학생 구역 (44~71)")
    
    # 🏛️ 상단 기둥
    st.caption("🏛️ 기둥")
    
    # Block 1: [44,45,46,47] | [48,49,50]
    gb1_c1, gb1_c2 = st.columns([4, 3])
    with gb1_c1:
        r1, r2, r3, r4 = st.columns(4)
        with r1: render_seat("44")
        with r2: render_seat("45")
        with r3: render_seat("46")
        with r4: render_seat("47")
    with gb1_c2:
        r1, r2, r3 = st.columns(3)
        with r1: render_seat("48")
        with r2: render_seat("49")
        with r3: render_seat("50")

    st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True) # 가로 통로

    # Block 2: [51,52,53,54] | [55,56,57]
    gb2_c1, gb2_c2 = st.columns([4, 3])
    with gb2_c1:
        r1, r2, r3, r4 = st.columns(4)
        with r1: render_seat("51")
        with r2: render_seat("52")
        with r3: render_seat("53")
        with r4: render_seat("54")
    with gb2_c2:
        r1, r2, r3 = st.columns(3)
        with r1: render_seat("55")
        with r2: render_seat("56")
        with r3: render_seat("57")

    st.markdown("---") # 메인 중앙 가로 통로

    # Block 3: [58,59,60,61] | [62,63,64]
    gb3_c1, gb3_c2 = st.columns([4, 3])
    with gb3_c1:
        r1, r2, r3, r4 = st.columns(4)
        with r1: render_seat("58")
        with r2: render_seat("59")
        with r3: render_seat("60")
        with r4: render_seat("61")
    with gb3_c2:
        r1, r2, r3 = st.columns(3)
        with r1: render_seat("62")
        with r2: render_seat("63")
        with r3: render_seat("64")

    st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True) # 가로 통로

    # Block 4: [65,66,67,68] | [69,70,71]
    gb4_c1, gb4_c2 = st.columns([4, 3])
    with gb4_c1:
        r1, r2, r3, r4 = st.columns(4)
        with r1: render_seat("65")
        with r2: render_seat("66")
        with r3: render_seat("67")
        with r4: render_seat("68")
    with gb4_c2:
        r1, r2, r3 = st.columns(3)
        with r1: render_seat("69")
        with r2: render_seat("70")
        with r3: render_seat("71")

# --- 3. 하단 창가 구조 ---
st.markdown("---")
st.success("🪟 **창문 (하늘공원 방향)**")
