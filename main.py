import streamlit as st
import numpy as np
import mediapipe as mp
from PIL import Image, ImageDraw
import random

# 1. 페이지 설정 및 게임 스타일 CSS 주입
st.set_page_config(page_title="Virtual Avatar Full-Body Quest 🎮", page_icon="👾", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #1a1a2e;
        color: #e94560;
        font-family: 'Courier New', Courier, monospace;
    }
    section[data-testid="stSidebar"] {
        background-color: #16213e !important;
        border-right: 2px solid #0f3460;
    }
    .game-title {
        font-size: 2.2rem;
        font-weight: bold;
        color: #00fff5;
        text-shadow: 3px 3px #ff007f;
        text-align: center;
        padding: 10px;
        border: 3px dashed #00fff5;
        border-radius: 15px;
        background-color: #0f3460;
        margin-bottom: 25px;
    }
    .game-card {
        background-color: #16213e;
        border: 2px solid #e94560;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.3);
    }
    .score-box {
        font-size: 1.4rem;
        color: #ffdd59;
        background-color: #0f3460;
        padding: 12px;
        border-radius: 8px;
        border: 2px solid #ffdd59;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 메인 타이틀
st.markdown('<div class="game-title">👾 Virtual Idol Full-Body Motion Capture Quest 👾</div>', unsafe_allow_html=True)

# 3. MediaPipe Holistic (전신 모듈) 호출
mp_holistic = mp.solutions.holistic

# 4. 사이드바 - 메뉴
st.sidebar.title("🎮 PLAYER MENU")
st.sidebar.subheader("🛡️ 렌더링 스킨 선택")
color_mode = st.sidebar.radio("네온 레이저 컬러", ["⚡ 사이버 그린", "💖 네온 핑크", "🌀 하이퍼 블루", "🔥 아케이드 옐로우"])

color_dict = {
    "⚡ 사이버 그린": (0, 255, 127),
    "💖 네온 핑크": (255, 20, 147),
    "🌀 하이퍼 블루": (0, 238, 255),
    "🔥 아케이드 옐로우": (255, 215, 0)
}

show_mesh = st.sidebar.checkbox("3D 관절 Wireframe 활성화", value=True)
line_width = st.sidebar.slider("레이저 선 두께", 1, 4, 2)

# 5. 안내 문구
st.write("### 📜 **QUEST:** 인물 사진(상반신/전신)을 업로드하여 아바타 3D 관절을 스캔하세요!")

uploaded_file = st.file_uploader("🖼️ Character Image Upload (.jpg / .png)", type=["jpg", "jpeg", "png"])

if uploaded_file is None:
    st.info("👈 플레이어님! 인물 사진을 업로드하면 전신 3D 관절(얼굴, 몸, 손) 분석이 시작됩니다.")
else:
    image = Image.open(uploaded_file).convert("RGB")
    width, height = image.size
    img_array = np.array(image)

    # 6. Holistic 전신 연산 세션 실행
    with mp_holistic.Holistic(
        static_image_mode=True,
        model_complexity=2,
        refine_face_landmarks=True) as holistic:

        results = holistic.process(img_array)
        annotated_image = image.copy()
        draw = ImageDraw.Draw(annotated_image)

        total_landmarks = 0
        selected_color = color_dict[color_mode]

        # 픽셀 좌표 변환 및 선 그리기 함수 (개선된 구조)
        def draw_connections(landmarks, connections):
            added_count = 0
            if landmarks and show_mesh:
                added_count = len(landmarks.landmark)
                for conn in connections:
                    pt1 = landmarks.landmark[conn[0]]
                    pt2 = landmarks.landmark[conn[1]]

                    x1, y1 = int(pt1.x * width), int(pt1.y * height)
                    x2, y2 = int(pt2.x * width), int(pt2.y * height)

                    draw.line([(x1, y1), (x2, y2)], fill=selected_color, width=line_width)
            return added_count

        # A. 얼굴, 몸, 손 각각 그려주면서 개수 누적
        total_landmarks += draw_connections(results.face_landmarks, mp_holistic.FACEMESH_TESSELATION)
        total_landmarks += draw_connections(results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
        total_landmarks += draw_connections(results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        total_landmarks += draw_connections(results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

        # 7. 화면 출력
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="game-card">', unsafe_allow_html=True)
            st.subheader("📸 원본 인물 스캔")
            st.image(image, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="game-card">', unsafe_allow_html=True)
            st.subheader("🎭 전신 3D 모션 캡처 렌더링")
            st.image(annotated_image, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # 8. 결과 스코어보드
        st.write("---")
        if results.pose_landmarks or results.face_landmarks:
            st.balloons()
            score = random.randint(93, 99)
            
            st.markdown(f"""
            <div class="score-box">
                🏆 <b>FULL-BODY SCAN CLEAR!</b><br>
                - 스캔된 총 3D 관절(Landmarks): <b>{total_landmarks} 개</b> (얼굴 + 몸 + 손가락)<br>
                - 모션 트래킹 싱크율: <b>{score}.5% (S+등급)</b><br>
                - 획득 칭호: <b>[버추얼 아이돌 메인 TA 🎤]</b>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ QUEST FAILED: 관절을 스캔하지 못했습니다. 인물이 명확한 사진으로 시도하세요!")
