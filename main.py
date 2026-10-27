import streamlit as st
import streamlit.components.v1 as components
import mediapipe as mp
import numpy as np
from PIL import Image
import json

# 1. 페이지 설정 (와이드 레이아웃 & 타이틀 설정)
st.set_page_config(page_title="내 뼈다귀가 멈추지 않아! 🦴🎮", page_icon="🐾", layout="wide")

# 세션 상태(Session State)에 업로드된 사진 기록 저장소 초기화
if "saved_avatars" not in st.session_state:
    st.session_state.saved_avatars = []

# MediaPipe Pose 모듈 준비
mp_pose = mp.solutions.pose

# 2. 레이아웃 분할 (왼쪽: 대화면 게임 / 오른쪽: 귀여운 파스텔톤 패널)
col_game, col_panel = st.columns([3.5, 1])

landmarks_json = "null"
uploaded_file = None

with col_panel:
    st.markdown("""
        <style>
            .stButton>button {
                border-radius: 20px;
                background-color: #ffb7b2;
                color: #fff;
                font-weight: bold;
                border: none;
            }
            .stButton>button:hover {
                background-color: #ff9aa2;
                color: #fff;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### 🐾 아바타 보관함")
    if len(st.session_state.saved_avatars) > 0:
        st.caption(f"총 {len(st.session_state.saved_avatars)}개 보관 중!")
        for idx, avatar in enumerate(st.session_state.saved_avatars):
            with st.expander(f"✨ #{idx+1} {avatar['name'][:10]}..."):
                st.image(avatar['image'], use_container_width=True)
        
        if st.button("🗑️ 보관함 비우기"):
            st.session_state.saved_avatars = []
            st.rerun()
    else:
        st.info("아직 저장된 아바타가 없어요!")
    
    st.write("---")
    st.markdown("### 🎨 플레이어 설정")
    uploaded_file = st.file_uploader("🖼️ 내 사진 업로드 (.jpg / .png)", type=["jpg", "jpeg", "png"])
    
    skin_color = st.selectbox(
        "✨ 네온 관절 컬러", 
        ["#ff9aa2", "#ffb7b2", "#ffdac1", "#e2f0cb", "#b5ead7", "#c7ceea"],
        format_func=lambda x: {
            "#ff9aa2": "코랄 핑크", 
            "#ffb7b2": "피치 블라섬", 
            "#ffdac1": "버터 옐로우", 
            "#e2f0cb": "민트 그린", 
            "#b5ead7": "소다 블루", 
            "#c7ceea": "라벤더 퍼플"
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
            background-color: #1e1e2f; 
            color: #f8fafc; 
            text-align: center; 
            font-family: 'Quicksand', 'Nunito', 'Courier New', sans-serif; 
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
            background: #232336; 
            border: 4px solid #ffb7b2; 
            border-radius: 24px; 
            box-shadow: 0 10px 30px rgba(255, 183, 178, 0.2);
            cursor: pointer;
        }
    </style>
    </head>
    <body>
        <div class="game-container">
            <!-- 둥글고 귀여운 테두리의 대화면 캔버스 (1100x580) -->
            <canvas id="gameCanvas" width="1100" height="580"></canvas>
        </div>

        <script>
            const canvas = document.getElementById("gameCanvas");
            const ctx = canvas.getContext("2d");

            let hasImage = HAS_IMAGE_PLACEHOLDER;
            let poseLandmarks = LANDMARKS_DATA_PLACEHOLDER;

            let charBaseY = 490;
            let charX = 180;
            
            let jumpCount = 0;
            const maxJumps = 2;
            let isCrouching = false;
            let jumpVelocity = 0;
            let jumpHeight = 0;
            
            let obstacleX = 1150;
            let obstacleWidth = 45;
            let obstacleHeight = 55;
            let obstacleY = 475;
            let obstacleSpeed = 5;
            let obstacleShape = "crystal";
            let obstacleColor = "#ff9aa2";
            
            let score = 0;
            let isPaused = false;
            let isGameOver = false;
            let isCountdown = false;
            let countdownValue = 3;
            let countdownTimer = null;

            const caligoShapes = ["crystal", "spike", "core", "blade"];
            const caligoColors = ["#ff9aa2", "#ffb7b2", "#ffdac1", "#e2f0cb", "#b5ead7", "#c7ceea"];

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
                obstacleWidth = Math.floor(35 + Math.random() * 30);
                obstacleHeight = Math.floor(35 + Math.random() * 40);
                
                obstacleSpeed = calculateSpeed();

                const isAir = Math.random() < 0.35;
                if (isAir) {
                    obstacleY = 340 + Math.random() * 60;
                } else {
                    obstacleY = 530 - obstacleHeight;
                }

                obstacleX = 1100 + Math.random() * 400;
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
                    jumpVelocity = -14;
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
                    if (mouseX >= 450 && mouseX <= 650 && mouseY >= 280 && mouseY <= 320) {
                        startCountdown();
                    }
                    else if (mouseX >= 450 && mouseX <= 650 && mouseY >= 340 && mouseY <= 380) {
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
                ctx.lineWidth = 4;
                ctx.lineCap = "round";
                ctx.shadowColor = "SKIN_COLOR_PLACEHOLDER";
                ctx.shadowBlur = 8;

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
                        ctx.arc(x + (nose.x - 0.5) * scale, offsetY + y + (nose.y - 0.5) * scale - 10, 16, 0, Math.PI * 2);
                        ctx.fill();
                    }

                    landmarks.forEach(function(lm, idx) {
                        if ([11,12,13,14,15,16,23,24,25,26,27,28].indexOf(idx) !== -1 && lm.visibility > 0.3) {
                            ctx.beginPath();
                            ctx.arc(x + (lm.x - 0.5) * scale, offsetY + y + (lm.y - 0.5) * scale, 5, 0, Math.PI * 2);
                            ctx.fillStyle = "#ffffff";
                            ctx.fill();
                            ctx.fillStyle = "SKIN_COLOR_PLACEHOLDER";
                        }
                    });
                } else {
                    let cy = crouching ? y + 15 : y;
                    ctx.beginPath(); ctx.arc(x, cy - 30, 14, 0, Math.PI * 2); ctx.fill();
                    ctx.beginPath(); ctx.moveTo(x, cy - 16); ctx.lineTo(x, cy + 15); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(x - 15, cy - 8); ctx.lineTo(x + 15, cy - 8); ctx.stroke();
                }
                ctx.shadowBlur = 0;
            }

            function drawObstacle() {
                ctx.fillStyle = obstacleColor;
                ctx.shadowColor = "#ffdac1";
                ctx.shadowBlur = 10;

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
                ctx.stroke();
                ctx.shadowBlur = 0;
            }

            function drawGorgeousBackground(themeLevel) {
                if (themeLevel === 0) {
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 580);
                    bgGrad.addColorStop(0, "#1e1e2f");
                    bgGrad.addColorStop(0.5, "#2a2a40");
                    bgGrad.addColorStop(1, "#3b3b58");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.fillStyle = "rgba(255, 222, 215, 0.5)";
                    let stars = [ [70,50], [180,100], [330,40], [450,130], [560,70], [680,150], [820,55], [100,210], [400,260], [650,220], [900,90], [1000,180] ];
                    stars.forEach(s => { ctx.fillRect(s[0], s[1], 3, 3); });
                } else if (themeLevel === 1) {
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 580);
                    bgGrad.addColorStop(0, "#4a3b5c");
                    bgGrad.addColorStop(0.5, "#6b4c7a");
                    bgGrad.addColorStop(1, "#b57186");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.fillStyle = "rgba(42, 42, 64, 0.4)";
                    ctx.fillRect(0, 380, 1100, 200);
                } else if (themeLevel === 2) {
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 580);
                    bgGrad.addColorStop(0, "#3a6073");
                    bgGrad.addColorStop(0.5, "#ffb7b2");
                    bgGrad.addColorStop(1, "#ffdac1");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
                    ctx.beginPath();
                    ctx.arc(150, 240, 60, 0, Math.PI * 2);
                    ctx.arc(210, 220, 80, 0, Math.PI * 2);
                    ctx.arc(270, 245, 55, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.beginPath();
                    ctx.arc(850, 280, 70, 0, Math.PI * 2);
                    ctx.arc(930, 255, 90, 0, Math.PI * 2);
                    ctx.fill();
                } else if (themeLevel === 3) {
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 580);
                    bgGrad.addColorStop(0, "#2b5876");
                    bgGrad.addColorStop(1, "#4e4376");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.fillStyle = "rgba(255, 255, 255, 0.12)";
                    ctx.beginPath(); ctx.arc(250, 360, 160, Math.PI, 0, false); ctx.fill();
                    ctx.beginPath(); ctx.arc(850, 400, 200, Math.PI, 0, false); ctx.fill();
                } else if (themeLevel === 4) {
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 580);
                    bgGrad.addColorStop(0, "#232526");
                    bgGrad.addColorStop(1, "#414345");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.fillStyle = "#888899";
                    ctx.beginPath(); ctx.arc(900, 140, 70, 0, Math.PI * 2); ctx.fill();
                    ctx.strokeStyle = "rgba(255, 255, 255, 0.4)";
                    ctx.lineWidth = 6;
                    ctx.beginPath(); ctx.ellipse(900, 140, 115, 30, 0.3, 0, Math.PI * 2); ctx.stroke();
                } else {
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 580);
                    bgGrad.addColorStop(0, "#1f1c2c");
                    bgGrad.addColorStop(1, "#928dab");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.fillStyle = "#2a2640";
                    ctx.fillRect(80, 300, 120, 280);
                    ctx.fillRect(850, 240, 140, 340);
                }
            }

            function update() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                let themeLevel = Math.floor(score / 1000) % 6;
                drawGorgeousBackground(themeLevel);

                ctx.strokeStyle = "#ffb7b2";
                ctx.lineWidth = 4;
                ctx.beginPath(); ctx.moveTo(0, 530); ctx.lineTo(1100, 530); ctx.stroke();

                if (!hasImage) {
                    ctx.fillStyle = "#ffb7b2";
                    ctx.font = "bold 22px 'Quicksand', sans-serif";
                    ctx.textAlign = "center";
                    ctx.fillText("🐾 오른쪽 패널에서 내 사진을 업로드해 주세요!", canvas.width / 2, canvas.height / 2 - 15);
                    ctx.fillStyle = "#b5ead7";
                    ctx.font = "15px 'Quicksand', sans-serif";
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

                    const themeNames = ["✨ 포근한 밤", "🌸 몽환 숲", "☁️ 노을 바다", "🌊 오션 파스텔", "🪐 별빛 행성", "🏰 판타지 성"];
                    ctx.fillStyle = "#f8fafc";
                    ctx.font = "bold 15px 'Quicksand', sans-serif";
                    ctx.textAlign = "left";
                    ctx.fillText("⭐ SCORE: " + score + " [" + themeNames[themeLevel] + "]", 25, 40);

                    ctx.fillStyle = "#b5ead7";
                    ctx.font = "13px 'Quicksand', sans-serif";
                    ctx.fillText("⌨️ Space(x2): 2단점프 | Ctrl: 숙이기 | ESC: 일시정지", 430, 40);

                    if (isGameOver) {
                        ctx.fillStyle = "rgba(30, 30, 47, 0.92)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#ffb7b2";
                        ctx.font = "bold 40px 'Quicksand', sans-serif";
                        ctx.textAlign = "center";
                        ctx.fillText("GAME OVER 🐾", canvas.width / 2, canvas.height / 2 - 30);

                        ctx.fillStyle = "#b5ead7";
                        ctx.font = "20px 'Quicksand', sans-serif";
                        ctx.fillText("Final Score: " + score, canvas.width / 2, canvas.height / 2 + 15);

                        ctx.fillStyle = "#f8fafc";
                        ctx.font = "16px 'Quicksand', sans-serif";
                        ctx.fillText("클릭 또는 스페이스바로 다시 시작!", canvas.width / 2, canvas.height / 2 + 70);
                    }

                    if (isPaused) {
                        ctx.fillStyle = "rgba(30, 30, 47, 0.9)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#ffb7b2";
                        ctx.font = "bold 34px 'Quicksand', sans-serif";
                        ctx.textAlign = "center";
                        ctx.fillText("GAME PAUSED ⏸️", canvas.width / 2, 170);

                        ctx.fillStyle = "#b5ead7";
                        ctx.fillRect(450, 280, 200, 45);
                        ctx.fillStyle = "#1e1e2f";
                        ctx.font = "bold 16px 'Quicksand', sans-serif";
                        ctx.fillText("▶ 이어서 하기", canvas.width / 2, 308);

                        ctx.fillStyle = "#ffdac1";
                        ctx.fillRect(450, 345, 200, 45);
                        ctx.fillStyle = "#1e1e2f";
                        ctx.fillText("🔄 처음으로", canvas.width / 2, 373);
                    }

                    if (isCountdown) {
                        ctx.fillStyle = "rgba(30, 30, 47, 0.9)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#ffdac1";
                        ctx.font = "bold 80px 'Quicksand', sans-serif";
                        ctx.textAlign = "center";
                        ctx.shadowColor = "#ffdac1";
                        ctx.shadowBlur = 15;
                        ctx.fillText(countdownValue, canvas.width / 2, canvas.height / 2 + 25);
                        ctx.shadowBlur = 0;

                        ctx.fillStyle = "#b5ead7";
                        ctx.font = "20px 'Quicksand', sans-serif";
                        ctx.fillText("준비하세요!", canvas.width / 2, canvas.height / 2 - 70);
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

    components.html(game_html, height=610)
