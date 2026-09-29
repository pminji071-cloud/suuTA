import streamlit as st
import numpy as np
import mediapipe as mp
from PIL import Image, ImageDraw

# MediaPipe 모듈을 안전하게 직접 불러오기 (AttributeError 방지)
try:
    import mediapipe.python.solutions.face_mesh as mp_face_mesh
except AttributeError:
    mp_face_mesh = mp.solutions.face_mesh

# 1. 페이지 설정 및 타이틀
st.set_page_config(page_title="Virtual Motion Capture TA Tool", page_icon="🎭")
st.title("🎭 버추얼 모션 캡처 & 그래픽 파이프라인 툴")
st.caption("TA/TD 진로 탐구: VLAST 버추얼 파이프라인 기반 3D Face Landmarks 추적 및 그래픽스 렌더링")

# 2. 사이드바 - TA/아티스트용 파이프라인 옵션
st.sidebar.header("⚙️ 모션 캡처 파이프라인 옵션")
show_mesh = st.sidebar.checkbox("3D 모션 캡처 랜드마크 표시", value=True)
color_option = st.sidebar.selectbox("선 그래픽 색상 모드", ["네온 그린", "버추얼 시안", "핫 핑크"])

# 아티스트용 색상 매핑 딕셔너리 (RGB)
color_dict = {
    "네온 그린": (0, 255, 0),
    "버추얼 시안": (0, 255, 255),
    "핫 핑크": (255, 20, 147)
}

# 3. 메인 - 파일 업로드 예외 처리
uploaded_file = st.file_uploader("모션 캡처를 진행할 인물 사진을 업로드하세요 (JPG, PNG)", type=["jpg", "jpeg", "png"])

# 예외 처리 1: 파일이 업로드되지 않았을 때
if uploaded_file is None:
    st.info("👈 왼쪽 사이드바 옵션을 설정하고, 분석할 인물 이미지를 업로드해 주세요.")
else:
    # 이미지 불러오기 및 해상도 추출
    image = Image.open(uploaded_file).convert("RGB")
    width, height = image.size
    img_array = np.array(image)

    # MediaPipe 모션 추적 연산 (얼굴 468개 랜드마크 추출)
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5) as face_mesh:

        results = face_mesh.process(img_array)
        annotated_image = image.copy()
        draw = ImageDraw.Draw(annotated_image)

        # 랜드마크(모션 키포인트) 시각화 렌더링
        if results.multi_face_landmarks and show_mesh:
            selected_color = color_dict[color_option]
            
            for face_landmarks in results.multi_face_landmarks:
                # 랜드마크 간 연결선 추출 및 PIL 렌더링
                connections = mp_face_mesh.FACEMESH_TESSELATION
                for connection in connections:
                    start_idx = connection[0]
                    end_idx = connection[1]
                    
                    pt1 = face_landmarks.landmark[start_idx]
                    pt2 = face_landmarks.landmark[end_idx]

                    # 정규화된 좌표(0~1)를 실제 이미지 픽셀 좌표로 변환
                    x1, y1 = int(pt1.x * width), int(pt1.y * height)
                    x2, y2 = int(pt2.x * width), int(pt2.y * height)

                    draw.line([(x1, y1), (x2, y2)], fill=selected_color, width=1)

        # 예외 처리 2: 인물 얼굴이 감지되지 않았을 때
        elif not results.multi_face_landmarks:
            st.warning("⚠️ 이미지에서 얼굴 관절(Landmarks)을 찾을 수 없습니다. 인물이 명확한 사진을 올려주세요.")

    # 4. 화면 레이아웃 - 원본 vs 3D 렌더링 비교
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📷 원본 인물 이미지")
        st.image(image, use_container_width=True)
        
    with col2:
        st.subheader("🎭 3D 모션 캡처 렌더링")
        st.image(annotated_image, use_container_width=True)
