import streamlit as st
import streamlit.components.v1 as components
import mediapipe as mp
import numpy as np
from PIL import Image
import json

# 1. 페이지 설정 (와이드 레이아웃)
st.set_page_config(page_title="Virtual Avatar Motion Quest 🎮", page_icon="👾", layout="wide")

# MediaPipe Pose 모듈 준비
mp_pose = mp.solutions.pose

# 2. 레이아웃 분할 (왼쪽: 관절 캐릭터 게임 / 오른쪽: 컨트롤 패널)
col_game, col_panel = st.columns([2.2, 1])

landmarks_json = "null"

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
    st.info("사진을 올리면 **AI가 관절을 스캔**하여 바닥에 고정된 관절 캐릭터를 생성합니다! **클릭하여 점프**하세요.")
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        img_array = np.array(image)
        
        with mp_pose.Pose(static_image_mode=True, model_complexity=1) as pose:
            results = pose.process(img_array)
            if results.pose_landmarks:
                lm_list = []
                for lm in results.pose_landmarks.landmark:
                    lm_list.append({"x": lm.x, "y": lm.y, "visibility": lm.visibility})
                landmarks_json = json.dumps(lm_list)
                st.success("✨ 3D 관절 스캔 완료!")
            else:
                st.warning("⚠️ 관절을 감지하지 못해 기본 관절 캐릭터로 등록되었습니다.")
        
        st.image(image, use_container_width=True)
    else:
        st.warning("👈 먼저 인물 사진을 업로드해 주세요!")

with col_game:
    st.markdown("### 🕹️ VIRTUAL IDOL ARCADE STAGE")
    
    has_image = "true" if uploaded_file is not None else "false"
    
    raw_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body { 
            background-color: #0f3460; 
            color: #ffffff; 
            text-align: center; 
            font-family: 'Courier New', Courier, monospace; 
            margin: 0; 
            padding: 0;
        }
        .game-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        canvas { 
            background: #1a1a2e; 
            border: 3px solid #00fff5; 
            border-radius: 12px; 
            box-shadow: 0 0 25px rgba(0, 255, 245, 0.4);
            cursor: pointer;
        }
    </style>
    </head>
    <body>
        <div class="game-container">
            <canvas id="gameCanvas" width="650" height="400"></canvas>
        </div>

        <script>
            const canvas = document.getElementById("gameCanvas");
            const ctx = canvas.getContext("2d");

            let hasImage = HAS_IMAGE_PLACEHOLDER;
            let poseLandmarks = LANDMARKS_DATA_PLACEHOLDER;

            // 캐릭터 고정 위치 (바닥 기준)
            let charBaseY = 320;
            let isJumping = false;
            let jumpVelocity = 0;
            let jumpHeight = 0;
            let obstacleX = 700;
            let score = 0;

            // 마우스 움직임 인식 제거 -> 오직 클릭으로만 점프 트리거
            canvas.addEventListener("click", function() {
                if (!hasImage) return;
                if (!isJumping) {
                    isJumping = true;
                    jumpVelocity = -14; // 점프 힘
                }
            });

            const POSE_CONNECTIONS = [
                [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
                [11, 23], [12, 24], [23, 24], [23, 25], [24, 26], [25, 27], [26, 28]
            ];

            function drawPoseCharacter(x, y, landmarks) {
                ctx.strokeStyle = "SKIN_COLOR_PLACEHOLDER";
                ctx.fillStyle = "SKIN_COLOR_PLACEHOLDER";
                ctx.lineWidth = 3;
                ctx.shadowColor = "SKIN_COLOR_PLACEHOLDER";
                ctx.shadowBlur = 10;

                if (landmarks && landmarks.length > 0) {
                    const scale = 110;
                    
                    POSE_CONNECTIONS.forEach(function(pair) {
                        const i = pair[0];
                        const j = pair[1];
                        const pt1 = landmarks[i];
                        const pt2 = landmarks[j];
                        if (pt1 && pt2 && pt1.visibility > 0.3 && pt2.visibility > 0.3) {
                            ctx.beginPath();
                            ctx.moveTo(x + (pt1.x - 0.5) * scale, y + (pt1.y - 0.5) * scale);
                            ctx.lineTo(x + (pt2.x - 0.5) * scale, y + (pt2.y - 0.5) * scale);
                            ctx.stroke();
                        }
                    });

                    const nose = landmarks[0];
                    if (nose) {
                        ctx.beginPath();
                        ctx.arc(x + (nose.x - 0.5) * scale, y + (nose.y - 0.5) * scale - 10, 14, 0, Math.PI * 2);
                        ctx.fill();
                    }

                    landmarks.forEach(function(lm, idx) {
                        if ([11,12,13,14,15,16,23,24,25,26,27,28].indexOf(idx) !== -1 && lm.visibility > 0.3) {
                            ctx.beginPath();
                            ctx.arc(x + (lm.x - 0.5) * scale, y + (lm.y - 0.5) * scale, 4, 0, Math.PI * 2);
                            ctx.fillStyle = "#ffffff";
                            ctx.fill();
                            ctx.fillStyle = "SKIN_COLOR_PLACEHOLDER";
                        }
                    });
                } else {
                    ctx.beginPath(); ctx.arc(x, y - 30, 12, 0, Math.PI * 2); ctx.fill();
                    ctx.beginPath(); ctx.moveTo(x, y - 18); ctx.lineTo(x, y + 15); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(x - 15, y - 8); ctx.lineTo(x + 15, y - 8); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(x, y + 15); ctx.lineTo(x - 12, y + 35); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(x, y + 15); ctx.lineTo(x + 12, y + 35); ctx.stroke();
                }
                ctx.shadowBlur = 0;
            }

            function update() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                ctx.strokeStyle = "#16213e";
                ctx.lineWidth = 1;
                for(let i=0; i<canvas.width; i+=40) {
                    ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
                }

                // 바닥선 (Y = 360)
                ctx.strokeStyle = "#ff007f";
                ctx.lineWidth = 5;
                ctx.beginPath(); ctx.moveTo(0, 360); ctx.lineTo(650, 360); ctx.stroke();

                if (!hasImage) {
                    ctx.fillStyle = "#ff007f";
                    ctx.font = "bold 20px 'Courier New'";
                    ctx.textAlign = "center";
                    ctx.fillText("⚠️ WAITING FOR CHARACTER IMAGE", canvas.width / 2, canvas.height / 2 - 15);
                    ctx.fillStyle = "#00fff5";
                    ctx.font = "14px 'Courier New'";
                    ctx.fillText("Upload a photo on the right panel to start game!", canvas.width / 2, canvas.height / 2 + 20);
                } else {
                    // 점프 물리 연산
                    if (isJumping) {
                        jumpHeight += jumpVelocity;
                        jumpVelocity += 0.8; // 중력
                        if (jumpHeight >= 0) {
                            jumpHeight = 0;
                            isJumping = false;
                        }
                    }

                    obstacleX -= 6;
                    if (obstacleX < -40) {
                        obstacleX = 700;
                        score += 100;
                    }

                    // 장애물
                    ctx.fillStyle = "#ffdd59";
                    ctx.shadowColor = "#ffdd59";
                    ctx.shadowBlur = 10;
                    ctx.fillRect(obstacleX, 310, 35, 50);
                    ctx.shadowBlur = 0;

                    let renderY = charBaseY + jumpHeight;
                    drawPoseCharacter(120, renderY, poseLandmarks);

                    ctx.fillStyle = "#00fff5";
                    ctx.font = "bold 20px 'Courier New'";
                    ctx.textAlign = "left";
                    ctx.fillText("SCORE: " + score, 30, 40);

                    ctx.fillStyle = "#ffffff";
                    ctx.font = "14px 'Courier New'";
                    ctx.fillText("🖱️ Click to Jump!", 460, 40);
                }

                requestAnimationFrame(update);
            }

            update();
        </script>
    </body>
    </html>
    """

    game_html = raw_html.replace("HAS_IMAGE_PLACEHOLDER", has_image)
    game_html = game_html.replace("LANDMARKS_DATA_PLACEHOLDER", landmarks_json)
    game_html = game_html.replace("SKIN_COLOR_PLACEHOLDER", skin_color)

    components.html(game_html, height=430)
