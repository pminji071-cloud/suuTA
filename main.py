import streamlit as st
import numpy as np
import mediapipe as mp
from PIL import Image, ImageDraw
import random

# 1. 페이지 설정 및 게임 스타일 CSS 주입
st.set_page_config(page_title="Virtual Avatar Motion Quest 🎮", page_icon="👾", layout="wide")

# 귀엽고 심플한 픽셀/게임 스타일 Custom CSS
st.markdown("""
    <style>
    /* 전체 배경: 어두운 레트로 아케이드 톤 */
    .stApp {
        background-color: #1a1a2e;
        color: #e94560;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* 사이드바 스타일링 */
    section[data-testid="stSidebar"] {
        background-color: #16213e !important;
        border-right: 2px solid #0f3460;
    }

    /* 제목 스타일 (게임 퀘스트 느낌) */
    .game-title {
        font-size: 2.3rem;
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

    /* 게임 카드 용기 */
    .game-card {
        background-color: #16213e;
        border: 2px solid #e94560;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.3);
    }

    /* 점수판 스타일 */
    .score-box {
        font-size: 1.5rem;
        color: #ffdd59;
        background-color: #0f3460;
        padding: 10px;
        border-radius: 8px;
        border: 2px solid #ffdd59;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 게임 메인 타이틀 (A옵션: 회사명 제외 버전)
st.markdown('<div class="game-title">👾 Virtual Avatar Motion Capture Quest v1.0 👾</div>', unsafe_allow_html=True)

# 3. MediaPipe Face Mesh 호출 (버전 호환용 안전 코드)
try:
    mp_face_mesh = mp.solutions.face_mesh
except AttributeError:
    from mediapipe.python.solutions import face_mesh as mp_face_mesh

# 4. 사이드바 - 캐릭터 장비 및 테마 선택 (게임 컨셉)
st.sidebar.title("🎮 PLAYER MENU")
st.sidebar.subheader("🛡️ 렌더링 스킨 선택")
color_mode = st.sidebar.radio("네온 레이저 컬러", ["⚡ 사이버 그린", "💖 네온 핑크", "🌀 하이퍼 블루", "🔥 아케이드 옐로우"])

color_dict = {
    "⚡ 사이버 그린": (0, 255, 127),
    "💖 네온 핑크": (255, 20, 147),
    "🌀 하이퍼 블루": (0, 238, 255),
    "🔥 아케이드 옐로우": (255, 215, 0)
}

show_mesh = st.sidebar.checkbox("3D Mesh 렌더링 활성화", value=True)
line_width = st.sidebar.slider("레이저 선 두께", 1, 3, 1)

# 5. 게임 퀘스트 영역
st.write("### 📜 **QUEST:** 얼굴 이미지를 업로드하여 3D 버추얼 아바타 모션 관절을 스캔하세요!")

uploaded_file = st.file_uploader("🖼️ Character Image Upload (.jpg / .png)", type=["jpg", "jpeg", "png"])

if uploaded_file is None:
    st.info("👈 플레이어님! 이미지를 업로드하면 3D 트래킹 분석 및 점수가 측정됩니다.")
else:
    image = Image.open(uploaded_file).convert("RGB")
    width, height = image.size
    img_array = np.array(image)

    # MediaPipe 연산
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5) as face_mesh:

        results = face_mesh.process(img_array)
        annotated_image = image.copy()
        draw = ImageDraw.Draw(annotated_image)

        landmark_count = 0

        if results.multi_face_landmarks and show_mesh:
            selected_color = color_dict[color_mode]
            
            for face_landmarks in results.multi_face_landmarks:
                landmark_count = len(face_landmarks.landmark)
                connections = mp_face_mesh.FACEMESH_TESSELATION
                for connection in connections:
                    pt1 = face_landmarks.landmark[connection[0]]
                    pt2 = face_landmarks.landmark[connection[1]]

                    x1, y1 = int(pt1.x * width), int(pt1.y * height)
                    x2, y2 = int(pt2.x * width), int(pt2.y * height)

                    draw.line([(x1, y1), (x2, y2)], fill=selected_color, width=line_width)

        # 6. 결과 및 게임 보상 결과 출력
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="game-card">', unsafe_allow_html=True)
            st.subheader("📸 원본 스캔 완료")
            st.image(image, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="game-card">', unsafe_allow_html=True)
            st.subheader("🎭 3D 모션 캡처 렌더링")
            st.image(annotated_image, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # 7. 게임 스타일 랭킹 & 스코어보드
        st.write("---")
        if results.multi_face_landmarks:
            st.balloons()  # 승리 축하 효과!
            score = random.randint(90, 99)
            
            st.markdown(f"""
            <div class="score-box">
                🏆 <b>QUEST CLEAR!</b><br>
                - 감지된 관절(Landmarks): <b>{landmark_count} 개</b><br>
                - 모션 싱크율: <b>{score}.8% (S등급)</b><br>
                - 획득한 칭호: <b>[전설의 버추얼 아티스트 🎨]</b>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ QUEST FAILED: 이미지에서 관절을 스캔하지 못했습니다. 명확한 인물 사진으로 다시 시도하세요!")
