import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ⚠️ 본인의 구글 앱스 스크립트 웹 앱 URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyNRaRIwOmIKOOZh6-2aLIya4ZjQUlinv8lXkSyuUMn9hhcxlQ0tTOwAm62JH2TvVoDWw/exec"

st.set_page_config(
    page_title="2026 자기주도학습실 좌석 배치도",
    page_icon="📚",
    layout="wide"
)

# 좌석 버튼 커스텀 스타일
st.markdown("""
<style>
    div.stButton > button {
        padding: 6px 2px !important;
        font-size: 13px !important;
        font-weight: bold !important;
        margin-bottom: 2px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📚 2026학년도 하계 방학 좌석 신청")
st.markdown("<p style='font-size: 20px; font-weight: bold; color: #555555;'>먼저 본인의 학번과 이름을 입력한 후, 아래 배치도에서 좌석을 클릭하세요.</p>", unsafe_allow_html=True)

# --- 구글 시트에서 최신 좌석 상태 불러오기 함수 ---
def fetch_realtime_seats():
    # 전체 좌석 목록 초기화 (87석)
    jeongdok = [str(i) for i in range(1, 72)]
    study = [f"{t}-{i}" for t in range(1, 5) for i in range(1, 5)]
    default_seats = {s: {"status": "빈자리", "user": ""} for s in (jeongdok + study)}
    
    try:
        # 구글 시트에 누적된 최신 데이터 요청
        response = requests.get(WEB_APP_URL, timeout=5)
        if response.status_code == 200:
            db_seats = response.json()
            for seat_id, info in db_seats.items():
                if seat_id in default_seats:
                    default_seats[seat_id] = info
    except Exception as e:
        pass
        
    return default_seats

# 실시간 DB 데이터 로드
st.session_state.seats = fetch_realtime_seats()

# --- 1. 상단: 학생 정보 입력란 ---
st.markdown("---")
col_input, col_refresh = st.columns([4, 1])

with col_input:
    student_name = st.text_input("👤 학번 및 이름 입력 (필수)", placeholder="예: 10224 하선훈", key="user_input_name")

with col_refresh:
    st.write(" ")
    st.write(" ")
    if st.button("🔄 현황 새로고침", use_container_width=True):
        st.rerun()

if not student_name.strip():
    st.info("💡 **안내:** 위 입력창에 학번과 이름을 먼저 입력하셔야 좌석 선택(입/퇴실)이 가능합니다.")
else:
    st.success(f"✏️ **[{student_name}]** 학생으로 설정되었습니다. 아래 배치도에서 원하시는 좌석을 클릭하세요!")

st.markdown("---")

# --- 2. 좌석 클릭 시 즉시 입/퇴실 처리 함수 ---
def handle_seat_click(seat_id):
    current_user = st.session_state.user_input_name.strip()
    
    if not current_user:
        st.error("⚠️ 학번과 이름을 상단 입력창에 먼저 입력해 주세요!")
        return

    info = st.session_state.seats.get(seat_id, {"status": "빈자리", "user": ""})
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 빈자리 클릭 ➔ 입실 처리
    if info["status"] == "빈자리":
        payload = {"timestamp": now_str, "student_id": current_user, "seat_no": seat_id, "status": "입실"}
        try:
            requests.post(WEB_APP_URL, json=payload)
            st.toast(f"🎉 [{seat_id}]번 좌석 입실 완료! ({current_user})", icon="🟢")
        except:
            st.error("전송 실패. 다시 시도해주세요.")

    # 사용중 좌석 클릭 ➔ 퇴실 처리
    else:
        payload = {"timestamp": now_str, "student_id": current_user, "seat_no": seat_id, "status": "퇴실"}
        try:
            requests.post(WEB_APP_URL, json=payload)
            st.toast(f"🚪 [{seat_id}]번 좌석 퇴실 완료되었습니다.", icon="🔴")
        except:
            st.error("전송 실패. 다시 시도해주세요.")

# --- 3. 좌석 버튼 랜더링 함수 ---
def render_seat(seat_id):
    info = st.session_state.seats.get(seat_id, {"status": "빈자리", "user": ""})
    is_used = (info["status"] == "사용중")
    label = f"{seat_id}\n🔴{info['user']}" if is_used else f"{seat_id}\n🟢가능"
    
    if st.button(label, key=f"btn_{seat_id}", use_container_width=True):
        handle_seat_click(seat_id)
        st.rerun()

# --- 4. 상단 시설 안내 ---
top_1, top_2, top_3, top_4, top_5 = st.columns([1.5, 4, 2, 4, 1.5])
with top_1: st.success("🚪 입구 / 정수기 / 감독석")
with top_2: st.markdown("<h4 style='text-align: center;'>🚶‍♂️ 통로</h4>", unsafe_allow_html=True)
with top_3: st.info("🛗 엘리베이터")
with top_4: st.markdown("<h4 style='text-align: center;'>🚶‍♂️ 통로</h4>", unsafe_allow_html=True)
with top_5: st.success("🚪 입구")

st.markdown("---")

# --- 5. 메인 배치도 영역 ---
col_sec1, col_sec2, col_sec3, col_sec4 = st.columns([2.5, 3, 2.5, 4])

# [구역 1] 서측 라인 (1~23번)
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

# [구역 2] 남학생 외부 구역 (24~43번)
with col_sec2:
    st.markdown("#### 🟩 남학생 구역 (24~43)")
    st.caption("🏛️ 기둥")
    
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
        
    st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)
    
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

    st.markdown("---")

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

    st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

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

# [구역 3] 스터디 테이블 (1-1 ~ 4-4)
with col_sec3:
    st.markdown("#### ✏️ 스터디 테이블 (16석)")
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

    st.markdown("---")

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

# [구역 4] 여학생 외부 구역 (44~71번)
with col_sec4:
    st.markdown("#### 🟧 여학생 구역 (44~71)")
    st.caption("🏛️ 기둥")
    
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

    st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

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

    st.markdown("---")

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

    st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

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

# --- 6. 하단 시설 ---
st.markdown("---")
st.success("🪟 **창문 (하늘공원 방향)**")
