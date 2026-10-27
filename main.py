import streamlit as st
import numpy as np
import mediapipe as mp
from PIL import Image, ImageDraw
import io
import random

# 1. 페이지 설정 및 밝고 화사한 아케이드 게임 스타일 CSS 주입
st.set_page_config(page_title="Virtual Avatar Motion Quest 🎮", page_icon="👾", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #2d3748;
        font-family: 'Courier New', Courier, monospace;
    }
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 2px solid #e2e8f0;
    }
    .game-title {
        font-size: 2.2rem;
        font-weight: bold;
        color: #ffffff;
        text-shadow: 2px 2px #4a5568;
        text-align: center;
        padding: 10px;
        border: 3px dashed #3182ce;
        border-radius: 15px;
        background-color: #4299e1;
        margin-bottom: 25px;
    }
    .game-card {
        background-color: #ffffff;
        border: 2px solid #cbd5e0;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    .score-box {
        font-size: 1.4rem;
        color: #2b6cb0;
        background-color: #ebf8ff;
        padding: 12px;
        border-radius: 8px;
        border: 2px solid #90cdf4;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 메인 타이틀
st.markdown('<div class="game-title">👾 Virtual Idol Motion Capture Quest 👾</div>', unsafe_allow_html=True)

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

# 5. 안내 문구 및 이미지 업로더
st.write("### 📜 **QUEST:** 인물 사진을 업로드하여 3D 전신 관절(얼굴, 목, 몸, 손)을 스캔하세요!")

uploaded_file = st.file_uploader("🖼️ Character Image Upload (.jpg / .png)", type=["jpg", "jpeg", "png"])

if uploaded_file is None:
    st.info("👈 플레이어님! 인물 사진을 업로드하면 전신 3D 관절 모션 트래킹 분석이 시작됩니다.")
else:
    selected_color = color_dict[color_mode]
    
    # 이미지 바이너리 데이터를 안전하게 읽어와서 PIL 이미지로 변환
    image_bytes = uploaded_file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = image.size
    img_array = np.array(image)

    # 6. Holistic 전신 연산 세션 실행
    with mp_holistic.Holistic(
        static_image_mode=True,
        model_complexity=1,
        refine_face_landmarks=True) as holistic:

        results = holistic.process(img_array)
        annotated_image = image.copy()
        draw = ImageDraw.Draw(annotated_image)

        total_landmarks = 0

        # 관절 및 선 렌더링 함수
        def draw_detailed_connections(landmarks, connections, draw_points=False):
            added_count = 0
            if landmarks and show_mesh:
                added_count = len(landmarks.landmark)
                for conn in connections:
                    pt1 = landmarks.landmark[conn[0]]
                    pt2 = landmarks.landmark[conn[1]]

                    x1, y1 = int(pt1.x * width), int(pt1.y * height)
                    x2, y2 = int(pt2.x * width), int(pt2.y * height)

                    draw.line([(x1, y1), (x2, y2)], fill=selected_color, width=line_width)

                if draw_points:
                    r = line_width + 1
                    for lm in landmarks.landmark:
                        cx, cy = int(lm.x * width), int(lm.y * height)
                        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(255, 255, 255), outline=selected_color)

            return added_count

        # A. 얼굴 468개 메쉬
        total_landmarks += draw_detailed_connections(results.face_landmarks, mp_holistic.FACEMESH_TESSELATION, draw_points=False)
        
        # B. 신체 뼈대
        total_landmarks += draw_detailed_connections(results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, draw_points=True)
        
        # C. 양손
        total_landmarks += draw_detailed_connections(results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, draw_points=True)
        total_landmarks += draw_detailed_connections(results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, draw_points=True)

        # D. 목 관절(Neck Joint) 수동 연결 (얼굴 턱 - 어깨 중앙)
        if results.face_landmarks and results.pose_landmarks and show_mesh:
            chin = results.face_landmarks.landmark[152]
            chin_x, chin_y = int(chin.x * width), int(chin.y * height)

            l_shoulder = results.pose_landmarks.landmark[11]
            r_shoulder = results.pose_landmarks.landmark[12]

            neck_base_x = int(((l_shoulder.x + r_shoulder.x) / 2) * width)
            neck_base_y = int(((l_shoulder.y + r_shoulder.y) / 2) * height)

            draw.line([(chin_x, chin_y), (neck_base_x, neck_base_y)], fill=selected_color, width=line_width)
            draw.line([(neck_base_x, neck_base_y), (int(l_shoulder.x * width), int(l_shoulder.y * height))], fill=selected_color, width=line_width)
            draw.line([(neck_base_x, neck_base_y), (int(r_shoulder.x * width), int(r_shoulder.y * height))], fill=selected_color, width=line_width)

        # 7. 화면 출력 (좌우 비교 카드)
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
            score = random.randint(95, 99)
            
            st.markdown(f"""
            <div class="score-box">
                🏆 <b>FULL-BODY RIGGING SCAN CLEAR!</b><br>
                - 스캔된 총 3D 관절(Landmarks): <b>{total_landmarks} 개</b> (얼굴 + 목 + 몸 + 손)<br>
                - 모션 트래킹 싱크율: <b>{score}.8% (S+등급)</b><br>
                - 획득 칭호: <b>[버추얼 아이돌 수석 테크니컬 아티스트 🎤]</b>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ QUEST FAILED: 인물의 관절을 스캔하지 못했습니다. 얼굴과 상체가 잘 나온 사진으로 다시 시도하세요!")
