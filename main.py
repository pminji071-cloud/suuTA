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
    st.info("사진을 올리면 **AI가 관절을 스캔**하여 뼈다귀 캐릭터를 생성합니다! **보내주신 사진들의 감성을 담은 고화질 테마 배경**이 점수대별로 펼쳐집니다. Space 2단점프와 Ctrl 숙이기로 생존하세요!")
    
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
    st.markdown("### 🦴 내 뼈다귀가 멈추지 않아! (RUNNING BONES)")
    
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
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
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
            let obstacleHeight = 45;
            let obstacleY = 315;
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
                let base = 4.5 + Math.random() * 1.5;
                
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
                obstacleWidth = Math.floor(25 + Math.random() * 30);
                obstacleHeight = Math.floor(30 + Math.random() * 40);
                
                obstacleSpeed = calculateSpeed();

                const isAir = Math.random() < 0.35;
                if (isAir) {
                    obstacleY = 225 + Math.random() * 40;
                } else {
                    obstacleY = 360 - obstacleHeight;
                }

                obstacleX = 650 + Math.random() * 350;
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
                ctx.shadowBlur = 6;

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

            // 보내주신 사진들의 감성을 그대로 재현한 고화질 실사풍 배경 렌더링 함수
            function drawGorgeousBackground(themeLevel) {
                if (themeLevel === 0) {
                    // [테마 0: 우주 성운] 보내주신 파란색/보라색 찬란한 성운과 별무리 사진 감성
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 360);
                    bgGrad.addColorStop(0, "#0b0c2a");
                    bgGrad.addColorStop(0.5, "#2b0d4f");
                    bgGrad.addColorStop(1, "#111827");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    // 성운 코어 빛 번짐
                    let nebulaGrad = ctx.createRadialGradient(450, 180, 20, 450, 180, 220);
                    nebulaGrad.addColorStop(0, "rgba(236, 72, 153, 0.35)");
                    nebulaGrad.addColorStop(0.5, "rgba(59, 130, 246, 0.25)");
                    nebulaGrad.addColorStop(1, "transparent");
                    ctx.fillStyle = nebulaGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    // 반짝이는 별무리
                    ctx.fillStyle = "#ffffff";
                    let stars = [ [50,40], [120,90], [230,30], [340,110], [420,60], [510,130], [600,45], [80,180], [290,220], [480,190], [150,280], [380,310] ];
                    stars.forEach(s => { ctx.fillRect(s[0], s[1], 2, 2); });
                } else if (themeLevel === 1) {
                    // [테마 1: 노을빛 호수와 부두] 보내주신 푸른 보랏빛 하늘과 잔잔한 물결, 나무 선착장 감성
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 360);
                    bgGrad.addColorStop(0, "#25316d");
                    bgGrad.addColorStop(0.5, "#57417e");
                    bgGrad.addColorStop(1, "#b57186");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    // 잔잔한 수평선 및 물결 반사
                    ctx.fillStyle = "rgba(15, 23, 42, 0.3)";
                    ctx.fillRect(0, 240, 650, 120);

                    // 선착장 실루엣 펜스
                    ctx.strokeStyle = "rgba(30, 41, 59, 0.8)";
                    ctx.lineWidth = 4;
                    ctx.beginPath();
                    ctx.moveTo(0, 280); ctx.lineTo(180, 280);
                    ctx.moveTo(30, 260); ctx.lineTo(30, 300);
                    ctx.moveTo(90, 260); ctx.lineTo(90, 300);
                    ctx.moveTo(150, 260); ctx.lineTo(150, 300);
                    ctx.stroke();
                } else if (themeLevel === 2) {
                    // [테마 2: 몽환적인 구름 바다 (하늘 위 풍경)] 보내주신 황금빛 구름과 녹색 대지가 어우러진 하늘 위 뷰 감성
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 360);
                    bgGrad.addColorStop(0, "#1d4ed8");
                    bgGrad.addColorStop(0.5, "#f59e0b");
                    bgGrad.addColorStop(1, "#b45309");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    // 대형 뭉게구름 군락
                    ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
                    ctx.beginPath();
                    ctx.arc(100, 180, 50, 0, Math.PI * 2);
                    ctx.arc(150, 160, 65, 0, Math.PI * 2);
                    ctx.arc(200, 185, 45, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.beginPath();
                    ctx.arc(480, 210, 60, 0, Math.PI * 2);
                    ctx.arc(540, 190, 75, 0, Math.PI * 2);
                    ctx.arc(600, 215, 50, 0, Math.PI * 2);
                    ctx.fill();
                } else if (themeLevel === 3) {
                    // [테마 3: 심해 오션] 딥 블루 바다 테마
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 360);
                    bgGrad.addColorStop(0, "#0369a1");
                    bgGrad.addColorStop(1, "#0c4a6e");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.fillStyle = "rgba(255, 255, 255, 0.1)";
                    ctx.beginPath(); ctx.arc(180, 220, 140, Math.PI, 0, false); ctx.fill();
                    ctx.beginPath(); ctx.arc(500, 260, 180, Math.PI, 0, false); ctx.fill();
                } else if (themeLevel === 4) {
                    // [테마 4: 외계 행성과 오로라]
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 360);
                    bgGrad.addColorStop(0, "#18181b");
                    bgGrad.addColorStop(1, "#3f3f46");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.fillStyle = "#52525b";
                    ctx.beginPath(); ctx.arc(520, 100, 60, 0, Math.PI * 2); ctx.fill();
                    ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
                    ctx.lineWidth = 5;
                    ctx.beginPath(); ctx.ellipse(520, 100, 95, 25, 0.3, 0, Math.PI * 2); ctx.stroke();
                } else {
                    // [테마 5: 판타지 요새 야경]
                    let bgGrad = ctx.createLinearGradient(0, 0, 0, 360);
                    bgGrad.addColorStop(0, "#020617");
                    bgGrad.addColorStop(1, "#0f172a");
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);

                    ctx.fillStyle = "#1e293b";
                    ctx.fillRect(60, 180, 90, 180);
                    ctx.fillRect(480, 150, 110, 210);
                    ctx.beginPath(); ctx.moveTo(60, 180); ctx.lineTo(105, 110); ctx.lineTo(150, 180); ctx.fill();
                    ctx.beginPath(); ctx.moveTo(480, 150); ctx.lineTo(535, 80); ctx.lineTo(590, 150); ctx.fill();

                    ctx.fillStyle = "#ca8a04";
                    ctx.fillRect(85, 210, 15, 30); ctx.fillRect(115, 210, 15, 30);
                    ctx.fillRect(510, 180, 20, 35); ctx.fillRect(550, 180, 20, 35);
                }
            }

            function update() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                let themeLevel = Math.floor(score / 1000) % 6;
                drawGorgeousBackground(themeLevel);

                ctx.strokeStyle = "#475569";
                ctx.lineWidth = 4;
                ctx.beginPath(); ctx.moveTo(0, 360); ctx.lineTo(650, 360); ctx.stroke();

                if (!hasImage) {
                    ctx.fillStyle = "#f43f5e";
                    ctx.font = "bold 20px 'Courier New'";
                    ctx.textAlign = "center";
                    ctx.fillText("⚠️ WAITING FOR CHARACTER IMAGE", canvas.width / 2, canvas.height / 2 - 15);
                    ctx.fillStyle = "#38bdf8";
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
                        let charHeadY = isCrouching ? charCurrentY - 18 : charCurrentY - 44;
                        let charLeft = charX - 12;
                        let charRight = charX + 12;

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
                    ctx.font = "bold 13px 'Courier New'";
                    ctx.textAlign = "left";
                    ctx.fillText("SCORE: " + score + " [" + themeNames[themeLevel] + "]", 20, 35);

                    ctx.fillStyle = "#94a3b8";
                    ctx.font = "11px 'Courier New'";
                    ctx.fillText("⌨️ Space(x2):2단점프 | Ctrl:숙이기 | ESC:일시정지", 195, 35);

                    if (isGameOver) {
                        ctx.fillStyle = "rgba(15, 23, 42, 0.92)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#f43f5e";
                        ctx.font = "bold 32px 'Courier New'";
                        ctx.textAlign = "center";
                        ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 20);

                        ctx.fillStyle = "#38bdf8";
                        ctx.font = "16px 'Courier New'";
                        ctx.fillText("Final Score: " + score, canvas.width / 2, canvas.height / 2 + 15);

                        ctx.fillStyle = "#94a3b8";
                        ctx.font = "14px 'Courier New'";
                        ctx.fillText("Click or Space to restart", canvas.width / 2, canvas.height / 2 + 55);
                    }

                    if (isPaused) {
                        ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#f43f5e";
                        ctx.font = "bold 26px 'Courier New'";
                        ctx.textAlign = "center";
                        ctx.fillText("GAME PAUSED", canvas.width / 2, 120);

                        ctx.fillStyle = "#0284c7";
                        ctx.fillRect(225, 210, 200, 40);
                        ctx.fillStyle = "#ffffff";
                        ctx.font = "bold 15px 'Courier New'";
                        ctx.fillText("▶ 이어서 재생", canvas.width / 2, 235);

                        ctx.fillStyle = "#475569";
                        ctx.fillRect(225, 270, 200, 40);
                        ctx.fillStyle = "#ffffff";
                        ctx.fillText("🔄 처음으로", canvas.width / 2, 295);
                    }

                    if (isCountdown) {
                        ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#38bdf8";
                        ctx.font = "bold 60px 'Courier New'";
                        ctx.textAlign = "center";
                        ctx.shadowColor = "#38bdf8";
                        ctx.shadowBlur = 10;
                        ctx.fillText(countdownValue, canvas.width / 2, canvas.height / 2 + 15);
                        ctx.shadowBlur = 0;

                        ctx.fillStyle = "#94a3b8";
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
