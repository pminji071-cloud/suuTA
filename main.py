import streamlit as st
import numpy as np
import mediapipe as mp
from PIL import Image, ImageDraw
import cv2
import tempfile
import random

# 1. 페이지 설정 및 게임 스타일 CSS 주입
st.set_page_config(page_title="Virtual Avatar Motion Quest 🎮", page_icon="👾", layout="wide")

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

# 5. 안내 문구 및 통합 파일 업로더
st.write("### 📜 **QUEST:** 이미지 또는 동영상(.mp4)을 업로드하여 3D 관절을 스캔하세요!")

uploaded_file = st.file_uploader("🖼️ / 📹 Character Image or Video Upload", type=["jpg", "jpeg", "png", "mp4", "mov", "avi"])

if uploaded_file is None:
    st.info("👈 플레이어님! 사진이나 동영상을 업로드하면 3D 관절 모션 트래킹이 시작됩니다.")
else:
    file_type = uploaded_file.name.split(".")[-1].lower()
    selected_color = color_dict[color_mode]

    # 관절 그리기를 위한 공통 함수
    def process_and_draw(image_input, results, w, h):
        annotated = image_input.copy()
        draw = ImageDraw.Draw(annotated)
        total_cnt = 0

        def draw_detailed(landmarks, connections, draw_points=False):
            cnt = 0
            if landmarks and show_mesh:
                cnt = len(landmarks.landmark)
                for conn in connections:
                    pt1 = landmarks.landmark[conn[0]]
                    pt2 = landmarks.landmark[conn[1]]
                    x1, y1 = int(pt1.x * w), int(pt1.y * h)
                    x2, y2 = int(pt2.x * w), int(pt2.y * h)
                    draw.line([(x1, y1), (x2, y2)], fill=selected_color, width=line_width)

                if draw_points:
                    r = line_width + 1
                    for lm in landmarks.landmark:
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(255, 255, 255), outline=selected_color)
            return cnt

        total_cnt += draw_detailed(results.face_landmarks, mp_holistic.FACEMESH_TESSELATION, draw_points=False)
        total_cnt += draw_detailed(results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, draw_points=True)
        total_cnt += draw_detailed(results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, draw_points=True)
        total_cnt += draw_detailed(results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, draw_points=True)

        if results.face_landmarks and results.pose_landmarks and show_mesh:
            chin = results.face_landmarks.landmark[152]
            chin_x, chin_y = int(chin.x * w), int(chin.y * h)
            l_s = results.pose_landmarks.landmark[11]
            r_s = results.pose_landmarks.landmark[12]
            neck_x = int(((l_s.x + r_s.x) / 2) * w)
            neck_y = int(((l_s.y + r_s.y) / 2) * h)

            draw.line([(chin_x, chin_y), (neck_x, neck_y)], fill=selected_color, width=line_width)
            draw.line([(neck_x, neck_y), (int(l_s.x * w), int(l_s.y * h))], fill=selected_color, width=line_width)
            draw.line([(neck_x, neck_y), (int(r_s.x * w), int(r_s.y * h))], fill=selected_color, width=line_width)

        return annotated, total_cnt

    # A. 이미지 파일 처리 (.jpg, .png 등)
    if file_type in ["jpg", "jpeg", "png"]:
        image = Image.open(uploaded_file).convert("RGB")
        width, height = image.size
        img_array = np.array(image)

        with mp_holistic.Holistic(
            static_image_mode=True,
            model_complexity=1,
            refine_face_landmarks=True) as holistic:

            results = holistic.process(img_array)
            annotated_image, total_landmarks = process_and_draw(image, results, width, height)

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

            st.write("---")
            if results.pose_landmarks or results.face_landmarks:
                st.balloons()
                score = random.randint(93, 99)
                st.markdown(f"""
                <div class="score-box">
                    🏆 <b>IMAGE SCAN CLEAR!</b><br>
                    - 스캔된 총 3D 관절(Landmarks): <b>{total_landmarks} 개</b><br>
                    - 모션 트래킹 싱크율: <b>{score}.5% (S+등급)</b><br>
                    - 획득 칭호: <b>[버추얼 아이돌 메인 TA 🎤]</b>
                </div>
                """, unsafe_allow_html=True)

    # B. 동영상 파일 처리 (.mp4, .mov 등)
    elif file_type in ["mp4", "mov", "avi"]:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())

        cap = cv2.VideoCapture(tfile.name)
        st_frame = st.empty()

        with mp_holistic.Holistic(
            static_image_mode=False, # 동영상 연속 추적
            model_complexity=1,
            smooth_landmarks=True,
            refine_face_landmarks=True) as holistic:

            st.warning("🎬 동영상 모션 캡처가 진행 중입니다. 잠시만 기다려주세요...")

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # BGR -> RGB 변환
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb)
                h, w, _ = frame.shape

                results = holistic.process(frame_rgb)
                annotated_frame, _ = process_and_draw(pil_img, results, w, h)

                # 화면 프레임 실시간 업데이트
                st_frame.image(annotated_frame, use_container_width=True)

            cap.release()
            st.success("🎉 동영상 모션 캡처가 완료되었습니다!")
