import streamlit as st
import streamlit.components.v1 as components
import mediapipe as mp
import numpy as np
from PIL import Image
import json

# 1. 페이지 설정 (와이드 레이아웃 & 타이틀 설정)
st.set_page_config(page_title="내 뼈다귀가 멈추지 않아! 🦴🎮", page_icon="👾", layout="wide")

# 세션 상태(Session State)에 업로드된 사진 기록 저장소 초기화
if "saved_avatars" not in st.session_state:
    st.session_state.saved_avatars = []

# MediaPipe Pose 모듈 준비
mp_pose = mp.solutions.pose

# 2. 레이아웃 분할 (왼쪽: 대화면 게임 / 오른쪽: 컨트롤 및 보관함 패널)
col_game, col_panel = st.columns([3, 1])

landmarks_json = "null"

# 임시 변수 정의
uploaded_file = None

with col_game:
    st.markdown("### 🦴 내 뼈다귀가 멈추지 않아! (RUNNING BONES)")

with col_panel:
    st.markdown("### 📁 아바타 보관함 (Archive)")
    if len(st.session_state.saved_avatars) > 0:
        st.caption(f"총 {len(st.session_state.saved_avatars)}개 저장됨")
        for idx, avatar in enumerate(st.session_state.saved_avatars):
            with st.expander(f"📌 #{idx+1} {avatar['name'][:10]}..."):
                st.image(avatar['image'], use_container_width=True)
        
        if st.button("🗑️ 보관함 비우기"):
            st.session_state.saved_avatars = []
            st.rerun()
    else:
        st.info("저장된 아바타 없음")
    
    st.write("---")
    st.markdown("### 🎮 CONFIG")
    uploaded_file = st.file_uploader("🖼️ 사진 업로드 (.jpg / .png)", type=["jpg", "jpeg", "png"])
    
    skin_color = st.selectbox(
        "⚡ 네온 관절 컬러", 
        ["#00ff7f", "#ff1493", "#00eeff", "#ffd700"],
        format_func=lambda x: {
            "#00ff7f": "사이버 그린", 
            "#ff1493": "네온 핑크", 
            "#00eeff": "하이퍼 블루", 
            "#ffd700": "아케이드 옐로우"
        }[x]
    )

# 사진 처리 및 관절 스캔
if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    
    if uploaded_file.name not in [item["name"] for item in st.session_state.saved_avatars]:
        st.session_state.saved_avatars.append({
            "name": uploaded_file.name,
            "image": image
        })
    
    img_array = np.array(image)
    with mp_pose.Pose(static_image_mode=True, model_complexity=1) as pose:
        results = pose.process(img_array)
        if results.pose_landmarks:
            lm_list = []
            for lm in results.pose_landmarks.landmark:
                lm_list.append({"x": lm.x, "y": lm.y, "visibility": lm.visibility})
            landmarks_json = json.dumps(lm_list)

with col_game:
    has_image = "true" if uploaded_file is not None else "false"
    
    raw_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body { 
            background-color: #0f172a; 
            color: #e2e8f0; 
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
            background: #0f172a; 
            border: 2px solid #334155; 
            border-radius: 12px; 
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.6);
            cursor: pointer;
        }
    </style>
    </head>
    <body>
        <div class="game-container">
            <!-- 대화면으로 확대된 게임 캔버스 (900x480) -->
            <canvas id="gameCanvas" width="900" height="480"></canvas>
        </div>

        <script>
            const canvas = document.getElementById("gameCanvas");
            const ctx = canvas.getContext("2d");

            let hasImage = HAS_IMAGE_PLACEHOLDER;
            let poseLandmarks = LANDMARKS_DATA_PLACEHOLDER;

            let charBaseY = 400;
            let charX = 150;
            
            let jumpCount = 0;
            const maxJumps = 2;
            let isCrouching = false;
            let jumpVelocity = 0;
            let jumpHeight = 0;
            
            let obstacleX = 950;
            let obstacleWidth = 40;
            let obstacleHeight = 55;
            let obstacleY = 390;
            let obstacleSpeed = 5;
            let obstacleShape = "crystal";
            let obstacleColor = "#f43f5e";
            
            let score = 0;
            let isPaused = false;
            let isGameOver = false;
            let isCountdown = false;
            let countdownValue = 3;
            let countdownTimer = null;

            const caligoShapes = ["crystal", "spike", "core", "blade"];
            const caligoColors = ["#f43f5e", "#ec4899", "#a855f7", "#38bdf8", "#fbbf24", "#34d399"];

            function calculateSpeed() {
                let base = 5.0 + Math.random() * 1.5;
                
                if (score >= 2200) {
                    let extraTiers = Math.floor((score - 2200) / 400) + 1;
                    return base + 3.2 + (extraTiers * 0.5);
                } else if (score >= 1800) {
                    return base + 2.6;
                } else if (score >= 1200) {
                    return base + 1.8;
                } else if (score >= 600) {
                    return base + 1.0;
                } else {
                    return base;
                }
            }

            function resetObstacle() {
                obstacleWidth = Math.floor(30 + Math.random() * 35);
                obstacleHeight = Math.floor(35 + Math.random() * 45);
                
                obstacleSpeed = calculateSpeed();

                const isAir = Math.random() < 0.35;
                if (isAir) {
                    obstacleY = 280 + Math.random() * 50;
                } else {
                    obstacleY = 440 - obstacleHeight;
                }

                obstacleX = 900 + Math.random() * 400;
                obstacleShape = caligoShapes[Math.floor(Math.random() * caligoShapes.length)];
                obstacleColor = caligoColors[Math.floor(Math.random() * caligoColors.length)];
            }

            function startCountdown() {
                isPaused = false;
                isCountdown = true;
                countdownValue = 3;

                if (countdownTimer) clearInterval(countdownTimer);

                countdownTimer = setInterval(function() {
                    countdownValue--;
                    if (countdownValue <= 0) {
                        clearInterval(countdownTimer);
                        isCountdown = false;
                    }
                }, 1000);
            }

            function triggerJump() {
                if (!hasImage || isPaused || isCountdown || isGameOver || isCrouching) return;
                
                if (jumpCount < maxJumps) {
                    jumpCount++;
                    jumpVelocity = -13;
                }
            }

            canvas.addEventListener("click", function(e) {
                if (!hasImage) return;

                const rect = canvas.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;

                if (isGameOver) {
                    isGameOver = false;
                    score = 0;
                    resetObstacle();
                    jumpHeight = 0;
                    jumpCount = 0;
                    isCrouching = false;
                    return;
                }

                if (isPaused) {
                    if (mouseX >= 350 && mouseX <= 550 && mouseY >= 250 && mouseY <= 290) {
                        startCountdown();
                    }
                    else if (mouseX >= 350 && mouseX <= 550 && mouseY >= 310 && mouseY <= 350) {
                        score = 0;
                        resetObstacle();
                        jumpHeight = 0;
                        jumpCount = 0;
                        isCrouching = false;
                        isPaused = false;
                        isCountdown = false;
                        if (countdownTimer) clearInterval(countdownTimer);
                    }
                    return;
                }

                triggerJump();
            });

            window.addEventListener("keydown", function(e) {
                if (!hasImage) return;

                if (e.code === "Space") {
                    e.preventDefault();
                    if (isGameOver) {
                        isGameOver = false;
                        score = 0;
                        resetObstacle();
                        jumpHeight = 0;
                        jumpCount = 0;
                        isCrouching = false;
                        return;
                    }
                    triggerJump();
                }

                if (e.code === "ControlLeft" || e.code === "ControlRight") {
                    e.preventDefault();
                    if (jumpCount === 0 && !isPaused && !isCountdown && !isGameOver) {
                        isCrouching = true;
                    }
                }

                if (e.key === "Escape" && !isGameOver) {
                    if (isPaused) {
                        startCountdown();
                    } else {
                        isPaused = true;
                        if (countdownTimer) clearInterval(countdownTimer);
                        isCountdown = false;
                    }
                }
            });

            window.addEventListener("keyup", function(e) {
                if (e.code === "ControlLeft" || e.code === "ControlRight") {
                    isCrouching = false;
                }
            });

            const POSE_CONNECTIONS = [
                [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
                [11, 23], [12, 24], [23, 24], [23, 25], [24, 26], [25, 27], [26, 28]
            ];

            function drawPoseCharacter(x, y, landmarks, crouching) {
                ctx.strokeStyle = "SKIN_COLOR_PLACEHOLDER";
                ctx.fillStyle = "SKIN_COLOR_PLACEHOLDER";
                ctx.lineWidth = 3;
                ctx.shadowColor = "SKIN_COLOR_PLACEHOLDER";
                ctx.shadowBlur = 6;

                let scale = crouching ? 75 : 130;
                let offsetY = crouching ? 40 : 0;

                if (landmarks && landmarks.length > 0) {
                    POSE_CONNECTIONS.forEach(function(pair) {
                        const i = pair[0];
                        const j = pair[1];
                        const pt1 = landmarks[i];
                        const pt2 = landmarks[j];
                        if (pt1 && pt2 && pt1.visibility > 0.3 && pt2.visibility > 0.3) {
                            ctx.beginPath();
                            ctx.moveTo(x + (pt1.x - 0.5) * scale, offsetY + y + (pt1.y - 0.5) * scale);
                            ctx.lineTo(x + (pt2.x - 0.5) * scale, offsetY + y + (pt2.y - 0.5) * scale);
                            ctx.stroke();
                        }
                    });

                    const nose = landmarks[0];
                    if (nose) {
                        ctx.beginPath();
                        ctx.arc(x + (nose.x - 0.5) * scale, offsetY + y + (nose.y - 0.5) * scale - 10, 15, 0, Math.PI * 2);
                        ctx.fill();
                    }

                    landmarks.forEach(function(lm, idx) {
                        if ([11,12,13,14,15,16,23,24,25,26,27,28].indexOf(idx) !== -1 && lm.visibility > 0.3) {
                            ctx.beginPath();
                            ctx.arc(x + (lm.x - 0.5) * scale, offsetY + y + (lm.y - 0.5) * scale, 4, 0, Math.PI * 2);
                            ctx.fillStyle = "#ffffff";
                            ctx.fill();
                            ctx.fillStyle = "SKIN_COLOR_PLACEHOLDER";
                        }
                    });
                } else {
                    let cy = crouching ? y + 15 : y;
                    ctx.beginPath(); ctx.arc(x, cy - 30, 12, 0, Math.PI * 2); ctx.fill();
                    ctx.beginPath(); ctx.moveTo(x, cy - 18); ctx.lineTo(x, cy + 15); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(x - 15, cy - 8); ctx.lineTo(x + 15, cy - 8); ctx.stroke();
                }
                ctx.shadowBlur = 0;
            }

            function drawObstacle() {
                ctx.fillStyle = obstacleColor;
                ctx.shadowColor = "#ffffff";
                ctx.shadowBlur = 12;

                if (obstacleShape === "crystal") {
                    ctx.beginPath();
                    ctx.moveTo(obstacleX + obstacleWidth / 2, obstacleY);
                    ctx.lineTo(obstacleX + obstacleWidth, obstacleY + obstacleHeight * 0.4);
                    ctx.lineTo(obstacleX + obstacleWidth / 2, obstacleY + obstacleHeight);
                    ctx.lineTo(obstacleX, obstacleY + obstacleHeight * 0.4);
                    ctx.closePath();
                    ctx.fill();
                } else if (obstacleShape === "spike") {
                    ctx.beginPath();
                    ctx.moveTo(obstacleX + obstacleWidth / 2, obstacleY);
                    ctx.lineTo(obstacleX + obstacleWidth, obstacleY + obstacleHeight);
                    ctx.lineTo(obstacleX, obstacleY + obstacleHeight);
                    ctx.closePath();
                    ctx.fill();
                } else if (obstacleShape === "core") {
                    let radius = obstacleWidth / 2;
                    ctx.beginPath();
                    ctx.arc(obstacleX + radius, obstacleY + radius, radius, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = "#ffffff";
                    ctx.beginPath();
                    ctx.arc(obstacleX + radius, obstacleY + radius, radius * 0.35, 0, Math.PI * 2);
                    ctx.fill();
                } else if (obstacleShape === "blade") {
                    let cx = obstacleX + obstacleWidth / 2;
                    let cy = obstacleY + obstacleHeight / 2;
                    let size = obstacleWidth / 2;
                    ctx.beginPath();
                    ctx.moveTo(cx, cy - size);
                    ctx.lineTo(cx + size * 0.5, cy - size * 0.5);
                    ctx.lineTo(cx + size, cy);
                    ctx.lineTo(cx + size * 0.5, cy + size * 0.5);
                    ctx.lineTo(cx, cy + size);
                    ctx.lineTo(cx - size * 0.5, cy + size * 0.5);
                    ctx.lineTo(cx - size, cy);
                    ctx.lineTo(cx - size * 0.5, cy - size * 0.5);
                    ctx.closePath();
                    ctx.fill();
                }

                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 2;
                if (obstacleShape === "crystal") {
                    ctx.beginPath();
                    ctx.moveTo(obstacleX + obstacleWidth / 2, obstacleY);
                    ctx.lineTo(obstacleX + obstacleWidth, obstacleY + obstacleHeight * 0.4);
                    ctx.lineTo(obstacleX + obstacleWidth / 2, obstacleY + obstacleHeight);
                    ctx.lineTo(obstacleX, obstacleY + obstacleHeight * 0.4);
                    ctx.closePath();
                    ctx.stroke();
                }
                ctx.shadowBlur = 0;
            }

            function drawGorgeousBackground(themeLevel) {
                if (themeLevel === 0) {
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 440);
                    bgGrad.addColorStop(0, "#090d16");
                    bgGrad.addColorStop(0.5, "#1e1b4b");
                    bgGrad.addColorStop(1, "#172554");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.fillStyle = "rgba(226, 232, 240, 0.4)";
                    let stars = [ [70,50], [180,100], [330,40], [450,130], [560,70], [680,150], [820,55], [100,210], [400,260], [650,220] ];
                    stars.forEach(s => { ctx.fillRect(s[0], s[1], 2, 2); });
                } else if (themeLevel === 1) {
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 440);
                    bgGrad.addColorStop(0, "#25316d");
                    bgGrad.addColorStop(0.5, "#57417e");
                    bgGrad.addColorStop(1, "#b57186");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.fillStyle = "rgba(15, 23, 42, 0.3)";
                    ctx.fillRect(0, 300, 900, 140);
                } else if (themeLevel === 2) {
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 440);
                    bgGrad.addColorStop(0, "#1d4ed8");
                    bgGrad.addColorStop(0.5, "#f59e0b");
                    bgGrad.addColorStop(1, "#b45309");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
                    ctx.beginPath();
                    ctx.arc(150, 200, 60, 0, Math.PI * 2);
                    ctx.arc(210, 180, 80, 0, Math.PI * 2);
                    ctx.arc(270, 205, 55, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.beginPath();
                    ctx.arc(680, 240, 70, 0, Math.PI * 2);
                    ctx.arc(760, 215, 90, 0, Math.PI * 2);
                    ctx.fill();
                } else if (themeLevel === 3) {
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 440);
                    bgGrad.addColorStop(0, "#0369a1");
                    bgGrad.addColorStop(1, "#0c4a6e");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.fillStyle = "rgba(255, 255, 255, 0.1)";
                    ctx.beginPath(); ctx.arc(250, 280, 160, Math.PI, 0, false); ctx.fill();
                    ctx.beginPath(); ctx.arc(700, 320, 200, Math.PI, 0, false); ctx.fill();
                } else if (themeLevel === 4) {
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 440);
                    bgGrad.addColorStop(0, "#18181b");
                    bgGrad.addColorStop(1, "#3f3f46");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.fillStyle = "#52525b";
                    ctx.beginPath(); ctx.arc(720, 120, 70, 0, Math.PI * 2); ctx.fill();
                    ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
                    ctx.lineWidth = 6;
                    ctx.beginPath(); ctx.ellipse(720, 120, 115, 30, 0.3, 0, Math.PI * 2); ctx.stroke();
                } else {
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 440);
                    bgGrad.addColorStop(0, "#020617");
                    bgGrad.addColorStop(1, "#0f172a");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.fillStyle = "#1e293b";
                    ctx.fillRect(80, 220, 120, 220);
                    ctx.fillRect(680, 180, 140, 260);
                }
            }

            function update() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                let themeLevel = Math.floor(score / 1000) % 6;
                drawGorgeousBackground(themeLevel);

                ctx.strokeStyle = "#475569";
                ctx.lineWidth = 4;
                ctx.beginPath(); ctx.moveTo(0, 440); ctx.lineTo(900, 440); ctx.stroke();

                if (!hasImage) {
                    ctx.fillStyle = "#f43f5e";
                    ctx.font = "bold 22px 'Courier New'";
                    ctx.textAlign = "center";
                    ctx.fillText("⚠️ 오른쪽 패널에서 인물 사진을 업로드해 주세요!", canvas.width / 2, canvas.height / 2 - 15);
                    ctx.fillStyle = "#38bdf8";
                    ctx.font = "15px 'Courier New'";
                    ctx.fillText("Upload a photo to start RUNNING BONES!", canvas.width / 2, canvas.height / 2 + 25);
                } else {
                    if (!isPaused && !isCountdown && !isGameOver) {
                        if (jumpCount > 0) {
                            jumpHeight += jumpVelocity;
                            jumpVelocity += 0.75;
                            
                            if (jumpHeight >= 0) {
                                jumpHeight = 0;
                                jumpCount = 0;
                                jumpVelocity = 0;
                            }
                        }

                        obstacleX -= obstacleSpeed;
                        if (obstacleX < -60) {
                            resetObstacle();
                            score += 100;
                        }

                        let charCurrentY = charBaseY + jumpHeight;
                        let charHeadY = isCrouching ? charCurrentY - 20 : charCurrentY - 50;
                        let charLeft = charX - 14;
                        let charRight = charX + 14;

                        let obsLeft = obstacleX;
                        let obsRight = obstacleX + obstacleWidth;
                        let obsTop = obstacleY;
                        let obsBottom = obstacleY + obstacleHeight;

                        if (
                            charRight > obsLeft &&
                            charLeft < obsRight &&
                            charCurrentY > obsTop &&
                            charHeadY < obsBottom
                        ) {
                            isGameOver = true;
                        }
                    }

                    drawObstacle();

                    let renderY = charBaseY + jumpHeight;
                    drawPoseCharacter(charX, renderY, poseLandmarks, isCrouching);

                    const themeNames = ["🌌 성운 우주", "🌊 노을빛 호수", "☁️ 하늘 위 구름", "🌊 심해 오션", "🪐 외계 행성", "🏰 다크 요새"];
                    ctx.fillStyle = "#e2e8f0";
                    ctx.font = "bold 14px 'Courier New'";
                    ctx.textAlign = "left";
                    ctx.fillText("SCORE: " + score + " [" + themeNames[themeLevel] + "]", 20, 35);

                    ctx.fillStyle = "#94a3b8";
                    ctx.font = "12px 'Courier New'";
                    ctx.fillText("⌨️ Space(x2):2단점프 | Ctrl:숙이기 | ESC:일시정지", 380, 35);

                    if (isGameOver) {
                        ctx.fillStyle = "rgba(15, 23, 42, 0.92)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#f43f5e";
                        ctx.font = "bold 36px 'Courier New'";
                        ctx.textAlign = "center";
                        ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 25);

                        ctx.fillStyle = "#38bdf8";
                        ctx.font = "18px 'Courier New'";
                        ctx.fillText("Final Score: " + score, canvas.width / 2, canvas.height / 2 + 15);

                        ctx.fillStyle = "#94a3b8";
                        ctx.font = "15px 'Courier New'";
                        ctx.fillText("Click or Space to restart", canvas.width / 2, canvas.height / 2 + 60);
                    }

                    if (isPaused) {
                        ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#f43f5e";
                        ctx.font = "bold 30px 'Courier New'";
                        ctx.textAlign = "center";
                        ctx.fillText("GAME PAUSED", canvas.width / 2, 140);

                        ctx.fillStyle = "#0284c7";
                        ctx.fillRect(350, 250, 200, 40);
                        ctx.fillStyle = "#ffffff";
                        ctx.font = "bold 16px 'Courier New'";
                        ctx.fillText("▶ 이어서 재생", canvas.width / 2, 275);

                        ctx.fillStyle = "#475569";
                        ctx.fillRect(350, 310, 200, 40);
                        ctx.fillStyle = "#ffffff";
                        ctx.fillText("🔄 처음으로", canvas.width / 2, 335);
                    }

                    if (isCountdown) {
                        ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#38bdf8";
                        ctx.font = "bold 70px 'Courier New'";
                        ctx.textAlign = "center";
                        ctx.shadowColor = "#38bdf8";
                        ctx.shadowBlur = 12;
                        ctx.fillText(countdownValue, canvas.width / 2, canvas.height / 2 + 20);
                        ctx.shadowBlur = 0;

                        ctx.fillStyle = "#94a3b8";
                        ctx.font = "18px 'Courier New'";
                        ctx.fillText("GET READY...", canvas.width / 2, canvas.height / 2 - 60);
                    }
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

    components.html(game_html, height=510)
