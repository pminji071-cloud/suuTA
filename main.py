import streamlit as st
import streamlit.components.v1 as components
import mediapipe as mp
import numpy as np
from PIL import Image
import json

# 1. 페이지 설정 (와이드 레이아웃)
st.set_page_config(page_title="Virtual Avatar Motion Quest 🎮", page_icon="👾", layout="wide")

# 세션 상태(Session State)에 업로드된 사진 기록 저장소 초기화
if "saved_avatars" not in st.session_state:
    st.session_state.saved_avatars = []

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
    st.info("사진을 올리면 **AI가 관절을 스캔**하여 관절 캐릭터를 생성합니다! **1,000점마다 아름답고 다채로운 실사풍 테마 배경**으로 자동 전환됩니다. Space 2단점프와 Ctrl 숙이기로 장애물을 피하세요.")
    
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
        
        st.success("✨ 3D 관절 스캔 완료 & 아카이브 저장!")
        st.image(image, use_container_width=True)
    else:
        st.warning("👈 먼저 인물 사진을 업로드해 주세요!")

    st.write("---")
    st.markdown("### 📁 나의 아바타 보관함 (Archive)")
    if len(st.session_state.saved_avatars) > 0:
        st.caption(f"총 {len(st.session_state.saved_avatars)}개의 아바타가 저장되어 있습니다.")
        for idx, avatar in enumerate(st.session_state.saved_avatars):
            with st.expander(f"📌 {avatar['name']} (#{idx+1})"):
                st.image(avatar['image'], use_container_width=True)
        
        if st.button("🗑️ 보관함 비우기"):
            st.session_state.saved_avatars = []
            st.rerun()
    else:
        st.info("아직 저장된 캐릭터 사진이 없습니다. 사진을 업로드해 보세요!")

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

            let charBaseY = 320;
            let charX = 120;
            
            let jumpCount = 0;
            const maxJumps = 2;
            let isCrouching = false;
            let jumpVelocity = 0;
            let jumpHeight = 0;
            
            let obstacleX = 700;
            let obstacleWidth = 35;
            let obstacleHeight = 50;
            let obstacleY = 310;
            let obstacleSpeed = 6;
            let obstacleShape = "rect";
            let obstacleColor = "#ffdd59";
            
            let score = 0;
            let isPaused = false;
            let isGameOver = false;
            let isCountdown = false;
            let countdownValue = 3;
            let countdownTimer = null;

            const shapeList = ["rect", "circle", "triangle", "star"];
            const colorList = ["#ffdd59", "#ff007f", "#00fff5", "#ff5722", "#9c27b0", "#e91e63", "#76ff03"];

            function resetObstacle() {
                obstacleWidth = Math.floor(20 + Math.random() * 35);
                obstacleHeight = Math.floor(25 + Math.random() * 45);
                obstacleSpeed = 5 + Math.random() * 6;

                const isAir = Math.random() < 0.35;
                if (isAir) {
                    obstacleY = 230 + Math.random() * 40;
                } else {
                    obstacleY = 360 - obstacleHeight;
                }

                obstacleX = 650 + Math.random() * 350;
                obstacleShape = shapeList[Math.floor(Math.random() * shapeList.length)];
                obstacleColor = colorList[Math.floor(Math.random() * colorList.length)];
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
                    jumpVelocity = -12;
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
                    if (mouseX >= 225 && mouseX <= 425 && mouseY >= 210 && mouseY <= 250) {
                        startCountdown();
                    }
                    else if (mouseX >= 225 && mouseX <= 425 && mouseY >= 270 && mouseY <= 310) {
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
                ctx.shadowBlur = 10;

                let scale = crouching ? 65 : 110;
                let offsetY = crouching ? 35 : 0;

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
                        ctx.arc(x + (nose.x - 0.5) * scale, offsetY + y + (nose.y - 0.5) * scale - 10, 14, 0, Math.PI * 2);
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
                ctx.shadowColor = obstacleColor;
                ctx.shadowBlur = 12;

                if (obstacleShape === "rect") {
                    ctx.fillRect(obstacleX, obstacleY, obstacleWidth, obstacleHeight);
                } else if (obstacleShape === "circle") {
                    let radius = obstacleWidth / 2;
                    ctx.beginPath();
                    ctx.arc(obstacleX + radius, obstacleY + radius, radius, 0, Math.PI * 2);
                    ctx.fill();
                } else if (obstacleShape === "triangle") {
                    ctx.beginPath();
                    ctx.moveTo(obstacleX + obstacleWidth / 2, obstacleY);
                    ctx.lineTo(obstacleX, obstacleY + obstacleHeight);
                    ctx.lineTo(obstacleX + obstacleWidth, obstacleY + obstacleHeight);
                    ctx.closePath();
                    ctx.fill();
                } else if (obstacleShape === "star") {
                    let cx = obstacleX + obstacleWidth / 2;
                    let cy = obstacleY + obstacleHeight / 2;
                    let outerRadius = obstacleHeight / 2;
                    let innerRadius = outerRadius / 2;
                    ctx.beginPath();
                    for (let i = 0; i < 5; i++) {
                        ctx.lineTo(cx + Math.cos((18 + i * 72) * Math.PI / 180) * outerRadius, cy - Math.sin((18 + i * 72) * Math.PI / 180) * outerRadius);
                        ctx.lineTo(cx + Math.cos((54 + i * 72) * Math.PI / 180) * innerRadius, cy - Math.sin((54 + i * 72) * Math.PI / 180) * innerRadius);
                    }
                    ctx.closePath();
                    ctx.fill();
                }
                ctx.shadowBlur = 0;
            }

            // 실사풍 고품질 그래픽 배경 렌더링 함수
            function drawGorgeousBackground(themeLevel) {
                if (themeLevel === 0) {
                    // 🌌 0~999점: 밤하늘 우주 (반짝이는 은하수와 별무리)
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 360);
                    bgGrad.addColorStop(0, "#03001e");
                    bgGrad.addColorStop(0.5, "#7303c0");
                    bgGrad.addColorStop(1, "#ec38bc");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.fillStyle = "#ffffff";
                    let stars = [ [50,40], [120,90], [230,30], [340,110], [420,60], [510,130], [600,45], [80,180], [290,220], [480,190] ];
                    stars.forEach(s => {
                        ctx.fillRect(s[0], s[1], 2, 2);
                    });
                } else if (themeLevel === 1) {
                    // ⛰️ 1,000~1,999점: 웅장한 첩첩산중
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 360);
                    bgGrad.addColorStop(0, "#2c3e50");
                    bgGrad.addColorStop(1, "#f1f2f6");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    // 먼 산 능선
                    ctx.fillStyle = "#4b6584";
                    ctx.beginPath(); ctx.moveTo(0, 360); ctx.lineTo(120, 180); ctx.lineTo(280, 360); ctx.fill();
                    ctx.beginPath(); ctx.moveTo(200, 360); ctx.lineTo(380, 130); ctx.lineTo(580, 360); ctx.fill();
                    // 가까운 산 능선
                    ctx.fillStyle = "#38adae";
                    ctx.beginPath(); ctx.moveTo(0, 360); ctx.lineTo(180, 220); ctx.lineTo(400, 360); ctx.fill();
                    ctx.beginPath(); ctx.moveTo(350, 360); ctx.lineTo(520, 190); ctx.lineTo(650, 360); ctx.fill();
                } else if (themeLevel === 2) {
                    // 🌊 2,000~2,999점: 에메랄드빛 환상 바다
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 360);
                    bgGrad.addColorStop(0, "#00c6ff");
                    bgGrad.addColorStop(1, "#0072ff");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    // 수평선 및 파도 결
                    ctx.fillStyle = "rgba(255, 255, 255, 0.25)";
                    ctx.beginPath(); ctx.arc(150, 240, 120, Math.PI, 0, false); ctx.fill();
                    ctx.beginPath(); ctx.arc(480, 280, 160, Math.PI, 0, false); ctx.fill();
                } else if (themeLevel === 3) {
                    // ☁️ 3,000~3,999점: 몽환적인 일몰 하늘과 뭉게구름
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 360);
                    bgGrad.addColorStop(0, "#ff7e5f");
                    bgGrad.addColorStop(0.6, "#feb47b");
                    bgGrad.addColorStop(1, "#ffcc70");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    // 대형 뭉게구름
                    ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
                    ctx.beginPath();
                    ctx.arc(120, 140, 45, 0, Math.PI * 2);
                    ctx.arc(165, 125, 55, 0, Math.PI * 2);
                    ctx.arc(210, 145, 40, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.beginPath();
                    ctx.arc(460, 180, 50, 0, Math.PI * 2);
                    ctx.arc(510, 165, 60, 0, Math.PI * 2);
                    ctx.fill();
                } else if (themeLevel === 4) {
                    // 🪐 4,000~4,999점: 신비로운 외계 행성과 성운
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 360);
                    bgGrad.addColorStop(0, "#1f1c2c");
                    bgGrad.addColorStop(1, "#928dab");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    // 대형 행성 및 고리
                    ctx.fillStyle = "#ff512f";
                    ctx.beginPath(); ctx.arc(500, 110, 65, 0, Math.PI * 2); ctx.fill();
                    ctx.strokeStyle = "rgba(255, 255, 255, 0.6)";
                    ctx.lineWidth = 5;
                    ctx.beginPath(); ctx.ellipse(500, 110, 105, 30, 0.4, 0, Math.PI * 2); ctx.stroke();
                } else {
                    // 🏰 5,000점 이상: 판타지 마법의 성 야경
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 360);
                    bgGrad.addColorStop(0, "#141e30");
                    bgGrad.addColorStop(1, "#243b55");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    // 성 실루엣
                    ctx.fillStyle = "#0b132b";
                    ctx.fillRect(60, 180, 90, 180);
                    ctx.fillRect(480, 150, 110, 210);
                    ctx.beginPath(); ctx.moveTo(60, 180); ctx.lineTo(105, 110); ctx.lineTo(150, 180); ctx.fill();
                    ctx.beginPath(); ctx.moveTo(480, 150); ctx.lineTo(535, 80); ctx.lineTo(590, 150); ctx.fill();

                    // 노란 성 창문 불빛
                    ctx.fillStyle = "#ffd700";
                    ctx.shadowColor = "#ffd700";
                    ctx.shadowBlur = 10;
                    ctx.fillRect(85, 210, 15, 30); ctx.fillRect(115, 210, 15, 30);
                    ctx.fillRect(510, 180, 20, 35); ctx.fillRect(550, 180, 20, 35);
                    ctx.shadowBlur = 0;
                }
            }

            function update() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                let themeLevel = Math.floor(score / 1000) % 6;
                drawGorgeousBackground(themeLevel);

                // 바닥선
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
                        let charHeadY = isCrouching ? charCurrentY - 20 : charCurrentY - 45;
                        
                        if (
                            obstacleX < charX + 15 &&
                            obstacleX + obstacleWidth > charX - 15 &&
                            charCurrentY > obstacleY &&
                            charHeadY < obstacleY + obstacleHeight
                        ) {
                            isGameOver = true;
                        }
                    }

                    drawObstacle();

                    let renderY = charBaseY + jumpHeight;
                    drawPoseCharacter(charX, renderY, poseLandmarks, isCrouching);

                    const themeNames = ["🌌 우주 테마", "⛰️ 산 테마", "🌊 바다 테마", "☁️ 하늘 테마", "🪐 행성 테마", "🏰 성 테마"];
                    ctx.fillStyle = "#ffffff";
                    ctx.font = "bold 13px 'Courier New'";
                    ctx.textAlign = "left";
                    ctx.fillText("SCORE: " + score + " [" + themeNames[themeLevel] + "]", 20, 35);

                    ctx.fillStyle = "#00fff5";
                    ctx.font = "11px 'Courier New'";
                    ctx.fillText("⌨️ Space(x2):2단점프 | Ctrl:숙이기 | ESC:일시정지", 195, 35);

                    if (isGameOver) {
                        ctx.fillStyle = "rgba(15, 52, 96, 0.9)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#ff007f";
                        ctx.font = "bold 32px 'Courier New'";
                        ctx.textAlign = "center";
                        ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 20);

                        ctx.fillStyle = "#00fff5";
                        ctx.font = "16px 'Courier New'";
                        ctx.fillText("Final Score: " + score, canvas.width / 2, canvas.height / 2 + 15);

                        ctx.fillStyle = "#ffffff";
                        ctx.font = "14px 'Courier New'";
                        ctx.fillText("Click or Space to restart", canvas.width / 2, canvas.height / 2 + 55);
                    }

                    if (isPaused) {
                        ctx.fillStyle = "rgba(15, 52, 96, 0.85)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#ff007f";
                        ctx.font = "bold 26px 'Courier New'";
                        ctx.textAlign = "center";
                        ctx.fillText("GAME PAUSED", canvas.width / 2, 120);

                        ctx.fillStyle = "#00fff5";
                        ctx.fillRect(225, 210, 200, 40);
                        ctx.fillStyle = "#0f3460";
                        ctx.font = "bold 15px 'Courier New'";
                        ctx.fillText("▶ 이어서 재생", canvas.width / 2, 235);

                        ctx.fillStyle = "#ffdd59";
                        ctx.fillRect(225, 270, 200, 40);
                        ctx.fillStyle = "#0f3460";
                        ctx.fillText("🔄 처음으로", canvas.width / 2, 295);
                    }

                    if (isCountdown) {
                        ctx.fillStyle = "rgba(15, 52, 96, 0.85)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#00fff5";
                        ctx.font = "bold 60px 'Courier New'";
                        ctx.textAlign = "center";
                        ctx.shadowColor = "#00fff5";
                        ctx.shadowBlur = 20;
                        ctx.fillText(countdownValue, canvas.width / 2, canvas.height / 2 + 15);
                        ctx.shadowBlur = 0;

                        ctx.fillStyle = "#ffffff";
                        ctx.font = "16px 'Courier New'";
                        ctx.fillText("GET READY...", canvas.width / 2, canvas.height / 2 - 50);
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

    components.html(game_html, height=430)
