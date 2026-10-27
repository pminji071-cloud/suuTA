import streamlit as st
import streamlit.components.v1 as components

# 1. 페이지 설정 (와이드 레이아웃)
st.set_page_config(page_title="Virtual Idol Arcade 🎮", layout="wide")

# 2. 메인 화면과 우측 사이드/패널 레이아웃 구성 (왼쪽: 게임 / 오른쪽: 업로드 및 설정)
col_game, col_panel = st.columns([2, 1])

with col_panel:
    st.markdown("### 🎮 PLAYER CONFIG")
    st.write("---")
    
    # 사진 업로드 칸을 오른쪽으로 배치
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
    st.info("마우스를 위아래로 움직여 캐릭터의 높낮이를 조종하고, **화면을 클릭**하면 장애물을 뛰어넘습니다!")
    
    if uploaded_file is not None:
        st.success("✨ 커스텀 아바타 장착 완료!")
        st.image(uploaded_file, use_container_width=True)
    else:
        st.warning("👈 사진을 업로드하면 나만의 아바타 스킨이 적용됩니다.")

with col_game:
    # 제목 없이 바로 게임 존부터 시작
    st.markdown("### 🕹️ VIRTUAL IDOL ARCADE STAGE")
    
    # HTML5 Canvas 기반 마우스 인터랙티브 미니게임 (JavaScript)
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

            let charY = 250;
            let targetY = 250;
            let isJumping = false;
            let jumpVelocity = 0;

            // 마우스 움직임으로 캐릭터 높낮이 조종
            canvas.addEventListener("mousemove", function(e) {{
                const rect = canvas.getBoundingClientRect();
                targetY = e.clientY - rect.top;
                if(targetY < 50) targetY = 50;
                if(targetY > 330) targetY = 330;
            }});

            // 마우스 클릭 시 점프
            canvas.addEventListener("click", function() {{
                if (!isJumping) {{
                    isJumping = true;
                    jumpVelocity = -12;
                }}
            }});

            let obstacleX = 700;
            let score = 0;
            let jumpHeight = 0;

            function update() {{
                // 마우스 위치 부드럽게 추적
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

                // 렌더링
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // 배경 그리드 라인 (아케이드 감성)
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

                // 장애물 (네온 박스)
                ctx.fillStyle = "#ffdd59";
                ctx.shadowColor = "#ffdd59";
                ctx.shadowBlur = 10;
                ctx.fillRect(obstacleX, 310, 35, 50);
                ctx.shadowBlur = 0; // 초기화

                // 플레이어 아바타 (마우스로 조종하는 네온 캐릭터)
                ctx.fillStyle = "{skin_color}";
                ctx.shadowColor = "{skin_color}";
                ctx.shadowBlur = 15;
                let renderY = charY + jumpHeight;
                ctx.beginPath();
                ctx.arc(120, renderY, 22, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;

                // 캐릭터 눈 표정
                ctx.fillStyle = "#1a1a2e";
                ctx.fillRect(112, renderY - 6, 5, 5);
                ctx.fillRect(123, renderY - 6, 5, 5);

                // 스코어 및 안내 텍스트
                ctx.fillStyle = "#00fff5";
                ctx.font = "bold 20px 'Courier New'";
                ctx.fillText("SCORE: " + score, 30, 40);

                ctx.fillStyle = "#ffffff";
                ctx.font = "14px 'Courier New'";
                ctx.fillText("🖱️ Move Mouse to Float | Click to Jump", 330, 40);

                requestAnimationFrame(update);
            }}

            update();
        </script>
    </body>
    </html>
    """
    
    # 웹 앱 내부에 게임 화면 임베드
    components.html(game_html, height=430)
