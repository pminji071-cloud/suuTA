import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정 (와이드 레이아웃)
st.set_page_config(page_title="Virtual Idol Arcade 🎮", layout="wide")

# 2. 메인 화면과 우측 패널 레이아웃 구성 (왼쪽: 게임 / 오른쪽: 업로드 및 설정)
col_game, col_panel = st.columns([2, 1])

with col_panel:
    st.markdown("### 🎮 PLAYER CONFIG")
    st.write("---")
    
    # 사진 업로드 칸
    uploaded_file = st.file_uploader("🖼️ 캐릭터 사진 업로드 (.jpg / .png)", type=["jpg", "png"])
    
    skin_color = st.selectbox(
        "⚡ 네온 레이저 컬러 선택", 
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
    st.info("우측에 캐릭터 사진을 업로드하면 게임이 시작됩니다! 마우스로 높낮이를 조종하고 클릭하여 점프하세요.")
    
    # 사진 업로드 여부에 따라 JavaScript에 전달할 상태값 결정
    has_avatar = "true" if uploaded_file is not None else "false"
    
    if uploaded_file is not None:
        st.success("✨ 커스텀 아바타 장착 완료!")
        st.image(uploaded_file, use_container_width=True)
    else:
        st.warning("👈 먼저 캐릭터 사진을 업로드해 주세요!")

with col_game:
    # 타이틀 없이 바로 게임 스테이지 출력
    st.markdown("### 🕹️ VIRTUAL IDOL ARCADE STAGE")
    
    # HTML5 Canvas 게임 (사진 업로드 전용 대기 화면 + 플레이 로직 분기)
    game_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
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
            box-shadow: 0 0 25px rgba(0, 255, 245, 0.4);
            cursor: pointer;
        }}
    </style>
    </head>
    <body>
        <div class="game-container">
            <canvas id="gameCanvas" width="650" height="400"></canvas>
        </div>
        <script>
            const canvas = document.getElementById("gameCanvas");
            const ctx = canvas.getContext("2d");

            let hasAvatar = {has_avatar};
            let charY = 250;
            let targetY = 250;
            let isJumping = false;
            let jumpVelocity = 0;

            // 마우스 움직임 이벤트 (아바타가 있을 때만 작동)
            canvas.addEventListener("mousemove", function(e) {{
                if (!hasAvatar) return;
                const rect = canvas.getBoundingClientRect();
                targetY = e.clientY - rect.top;
                if(targetY < 50) targetY = 50;
                if(targetY > 330) targetY = 330;
            }});

            // 마우스 클릭 점프 이벤트 (아바타가 있을 때만 작동)
            canvas.addEventListener("click", function() {{
                if (!hasAvatar) return;
                if (!isJumping) {{
                    isJumping = true;
                    jumpVelocity = -12;
                }}
            }});

            let obstacleX = 700;
            let score = 0;
            let jumpHeight = 0;

            function update() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // 배경 그리드 라인
                ctx.strokeStyle = "#16213e";
                ctx.lineWidth = 1;
                for(let i=0; i<canvas.width; i+=40) {{
                    ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
                }}

                // 바닥 라인
                ctx.strokeStyle = "#ff007f";
                ctx.lineWidth = 5;
                ctx.beginPath();
                ctx.moveTo(0, 360);
                ctx.lineTo(650, 360);
                ctx.stroke();

                if (!hasAvatar) {{
                    // 1. 사진이 없을 때 대기 화면 출력
                    ctx.fillStyle = "#ff007f";
                    ctx.font = "bold 20px 'Courier New'";
                    ctx.textAlign = "center";
                    ctx.fillText("⚠️ WAITING FOR CHARACTER UPLOAD", canvas.width / 2, canvas.height / 2 - 15);
                    
                    ctx.fillStyle = "#00fff5";
                    ctx.font = "14px 'Courier New'";
                    ctx.fillText("Please upload a character image on the right panel!", canvas.width / 2, canvas.height / 2 + 20);
                }} else {{
                    // 2. 사진이 업로드되었을 때 게임 실행
                    if (!isJumping) {{
                        charY += (targetY - charY) * 0.15;
                    }} else {{
                        jumpHeight += jumpVelocity;
                        jumpVelocity += 0.8; // 중력
                        if (jumpHeight >= 0) {{
                            jumpHeight = 0;
                            isJumping = false;
                        }}
                    }}

                    // 장애물 이동
                    obstacleX -= 6;
                    if (obstacleX < -40) {{
                        obstacleX = 700;
                        score += 100;
                    }}

                    // 장애물 렌더링
                    ctx.fillStyle = "#ffdd59";
                    ctx.shadowColor = "#ffdd59";
                    ctx.shadowBlur = 10;
                    ctx.fillRect(obstacleX, 310, 35, 50);
                    ctx.shadowBlur = 0;

                    // 플레이어 아바타 렌더링
                    ctx.fillStyle = "{skin_color}";
                    ctx.shadowColor = "{skin_color}";
                    ctx.shadowBlur = 15;
                    let renderY = charY + jumpHeight;
                    ctx.beginPath();
                    ctx.arc(120, renderY, 22, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.shadowBlur = 0;

                    // 아바타 눈 표정
                    ctx.fillStyle = "#1a1a2e";
                    ctx.fillRect(112, renderY - 6, 5, 5);
                    ctx.fillRect(123, renderY - 6, 5, 5);

                    // 스코어 및 안내 문구
                    ctx.
