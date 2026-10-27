import streamlit as st
import streamlit.components.v1 as components
import base64

# 1. 페이지 설정 (와이드 레이아웃)
st.set_page_config(page_title="Virtual Avatar Motion Quest 🎮", page_icon="👾", layout="wide")

# 2. 레이아웃 분할 (왼쪽: 관절 캐릭터 게임 / 오른쪽: 컨트롤 패널)
col_game, col_panel = st.columns([2.2, 1])

image_b64 = ""

with col_panel:
    st.markdown("### 🎮 PLAYER CONFIG")
    st.write("---")
    
    uploaded_file = st.file_uploader("🖼️ 인물 사진 업로드 (.jpg / .png)", type=["jpg", "jpeg", "png"])
    
    skin_color = st.selectbox(
        "⚡ 네온 관절 레이저 컬러", 
        ["#00ff7f", "#ff1493", "#00eeff", "#ffd700"],
        format_func=lambda x: {
            "#00ff7f": "사이버 그린", 
            "#ff1493": "네온 핑크", 
            "#00eeff": "하이퍼 블루", 
            "#ffd700": "아케이드 옐로우"
        }[x]
    )
    
    st.write("---")
    st.markdown("#### 📜 **GAME GUIDE**")
    st.info("사진을 올리면 **AI가 관절(Landmarks)을 스캔**하여 관절 캐릭터를 생성합니다! 마우스로 관절 캐릭터를 조종하고 클릭하여 점프하세요.")
    
    if uploaded_file is not None:
        # 이미지를 Base64 바이너리로 변환하여 JS Canvas로 전달
        bytes_data = uploaded_file.read()
        image_b64 = base64.b64encode(bytes_data).decode()
        st.success("✨ 3D 관절 스캔 및 캐릭터 생성 준비 완료!")
        st.image(uploaded_file, use_container_width=True)
    else:
        st.warning("👈 먼저 인물 사진을 업로드해 주세요!")

with col_game:
    st.markdown("### 🕹️ VIRTUAL IDOL ARCADE STAGE")
    
    has_image = "true" if image_b64 != "" else "false"
    
    # MediaPipe Pose + Canvas 기반 관절 인식 게임 HTML
    game_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <!-- MediaPipe Pose 라이브러리 직접 로드 -->
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js" crossorigin="anonymous"></script>
    <style>
        body {{ 
            background-color: #0f3460; 
            color: #ffffff; 
            text-align: center; 
            font-family: 'Courier New', Courier, monospace; 
            margin: 0; 
            padding: 0;
        }}
        .game-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        canvas {{ 
            background: #1a1a2e; 
            border: 3px solid #00fff5; 
            border-radius: 12px; 
            box-
