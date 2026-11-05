import streamlit as st
import streamlit.components.v1 as components
import mediapipe as mp
import numpy as np
from PIL import Image
import json
import base64
import io

# 1. 페이지 설정 (와이드 레이아웃)
st.set_page_config(page_title="내 뼈다귀가 멈추지 않아! 🦴🎮", page_icon="🐾", layout="wide")

# 🌟 스타일 및 여백 꾸미기 CSS
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #1e1e2f 0%, #25233c 50%, #2d2438 100%);
            color: #f8fafc;
            font-family: 'Quicksand', 'Nunito', sans-serif;
        }
        
        [data-testid="column"]:nth-of-type(2) {
            background-color: rgba(35, 35, 54, 0.75);
            padding: 15px;
            border-radius: 20px;
            border: 3px solid #ffb7b2;
            box-shadow: 0 10px 25px rgba(255, 183, 178, 0.15);
        }

        [data-testid="stFileUploader"] {
            background-color: rgba(45, 45, 70, 0.6);
            border: 2px dashed #ffdac1;
            border-radius: 14px;
            padding: 8px;
        }

        .stButton>button {
            border-radius: 18px;
            background-color: #ffb7b2;
            color: #ffffff;
            font-weight: bold;
            border: none;
            box-shadow: 0 4px 10px rgba(255, 183, 178, 0.3);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #ff9aa2;
            color: #ffffff;
            transform: translateY(-2px);
        }

        .streamlit-expanderHeader {
            background-color: rgba(45, 45, 70, 0.5);
            border-radius: 10px;
            color: #f8fafc !important;
            font-weight: bold;
        }

        h1, h3 {
            color: #ffdac1 !important;
            font-family: 'Quicksand', sans-serif;
        }
    </style>
""", unsafe_allow_html=True)

mp_pose = mp.solutions.pose

# 파이썬 세션 상태 초기화
if "avatar_list" not in st.session_state:
    st.session_state.avatar_list = []
if "active_index" not in st.session_state:
    st.session_state.active_index = 0

# 2. 레이아웃 비율 조정
col_game, col_panel = st.columns([2.8, 1])

with col_panel:
    st.markdown("### 🐾 아바타 보관함")
    
    uploaded_file = st.file_uploader("🖼️ 새 사진 업로드 (.jpg / .png)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file).convert("RGB")
            image.thumbnail((300, 300))
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            img_base64 = f"data:image/jpeg;base64,{img_str}"

            # MediaPipe 관절 스캔
            img_array = np.array(image)
            lm_list = []
            with mp_pose.Pose(static_image_mode=True, model_complexity=1) as pose:
                results = pose.process(img_array)
                if results.pose_landmarks:
                    for lm in results.pose_landmarks.landmark:
                        lm_list.append({"x": lm.x, "y": lm.y, "visibility": lm.visibility})
            
            new_item = {
                "name": uploaded_file.name,
                "image": img_base64,
                "landmarks": lm_list
            }
            
            if not any(item['name'] == new_item['name'] for item in st.session_state.avatar_list):
                st.session_state.avatar_list.append(new_item)
                st.session_state.active_index = len(st.session_state.avatar_list) - 1
        except Exception as e:
            st.error(f"이미지 처리 중 오류가 발생했습니다: {e}")

    # 아바타 보관함 리스트 UI (클릭하면 바로 선택되어 로드됨)
    if len(st.session_state.avatar_list) > 0:
        st.caption(f"✨ 보관된 아바타 ({len(st.session_state.avatar_list)}개)")
        for idx, avt in enumerate(st.session_state.avatar_list):
            cols = st.columns([1, 3])
            with cols[0]:
                st.image(avt['image'], width=50)
            with cols[1]:
                # 선택된 아바타 강조 표시
                btn_label = f"👉 {avt['name'][:10]}" if idx == st.session_state.active_index else f"{avt['name'][:10]}"
                if st.button(btn_label, key=f"btn_avt_{idx}"):
                    st.session_state.active_index = idx
                    st.rerun()
        
        if st.button("🗑️ 보관함 비우기"):
            st.session_state.avatar_list = []
            st.session_state.active_index = 0
            st.rerun()
    else:
        st.info("아직 저장된 아바타가 없습니다. 사진을 올려보세요!")

    st.write("---")
    st.markdown("### 🎨 플레이어 설정")
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

with col_game:
    st.markdown("### 🦴 내 뼈다귀가 멈추지 않아!")
    
    py_avatar_list_json = json.dumps(st.session_state.avatar_list)
    py_active_index = st.session_state.active_index

    raw_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body { 
            background-color: transparent; 
            color: #f8fafc; 
            text-align: center; 
            font-family: 'Quicksand', 'Nunito', sans-serif; 
            margin: 0; 
            padding: 0;
            overflow: hidden;
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
            border-radius: 20px; 
            box-shadow: 0 10px 30px rgba(255, 183, 178, 0.2);
            cursor: pointer;
            width: 100%;
            max-width: 950px;
            height: auto;
        }
    </style>
    </head>
    <body>
        <div class="game-container">
            <canvas id="gameCanvas" width="950" height="520"></canvas>
        </div>

        <script>
            const canvas = document.getElementById("gameCanvas");
            const ctx = canvas.getContext("2d");

            let audioCtx = null;

            function initAudio() {
                if (!audioCtx) {
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                }
            }

            function playPpyongSound() {
                try {
                    initAudio();
                    if (!audioCtx) return;
                    
                    let osc = audioCtx.createOscillator();
                    let gainNode = audioCtx.createGain();

                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(400, audioCtx.currentTime);
                    osc.frequency.exponentialRampToValueAtTime(1200, audioCtx.currentTime + 0.15);

                    gainNode.gain.setValueAtTime(0.2, audioCtx.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.15);

                    osc.connect(gainNode);
                    gainNode.connect(audioCtx.destination);

                    osc.start();
                    osc.stop(audioCtx.currentTime + 0.15);
                } catch(e) {
                    console.log("Audio play error:", e);
                }
            }

            let avatarList = [];
            let activeIndex = 0;

            try {
                let pyList = PY_AVATAR_LIST_PLACEHOLDER;
                let pyIndex = PY_ACTIVE_INDEX_PLACEHOLDER;

                let storedListStr = localStorage.getItem("dino_avatar_list");
                let storedList = storedListStr ? JSON.parse(storedListStr) : [];

                if (pyList && pyList.length > 0) {
                    pyList.forEach(item => {
                        if (!storedList.some(s => s.name === item.name)) {
                            storedList.push(item);
                        }
                    });
                    localStorage.setItem("dino_avatar_list", JSON.stringify(storedList));
                } else if (storedList.length > 0) {
                    avatarList = storedList;
                }

                avatarList = storedList.length > 0 ? storedList : pyList;
                activeIndex = pyIndex < avatarList.length ? pyIndex : (avatarList.length > 0 ? 0 : -1);
            } catch (err) {
                console.log("Storage load error:", err);
            }

            let hasImage = avatarList.length > 0 && activeIndex >= 0;
            let poseLandmarks = null;
            let activeImageBase64 = null;

            if (hasImage) {
                activeImageBase64 = avatarList[activeIndex].image;
                poseLandmarks = avatarList[activeIndex].landmarks;
            }

            let highScore = parseInt(localStorage.getItem("dino_high_score") || "0");

            let baseFloorY = 380;
            let floorY = 380;
            let targetFloorY = 380;
            let charX = 150;
            
            let jumpCount = 0;
            const maxJumps = 2;
            let isCrouching = false;
            let jumpVelocity = 0;
            let jumpHeight = 0;
            
            let obstacleX = 1000;
            let obstacleWidth = 40;
            let obstacleHeight = 50;
            let obstacleY = floorY - obstacleHeight;
            let obstacleSpeed = 5;
            let obstacleShape = "crystal";
            let obstacleColor = "#ff9aa2";

            let starX = -200;
            let starY = 250;
            let starActive = false;
            let starEffectTimer = 0;

            let score = 0;
            let isPaused = false;
            let isGameOver = false;
            let isCountdown = false;
            let countdownValue = 3;
            let countdownTimer = null;

            let celebrationText = "";
            let celebrationTimer = 0;
            const targetMilestones = [500, 1000, 1500, 1800, 2000, 5000, 7777, 10000];
            let achievedMilestones = {};

            const caligoShapes = ["crystal", "spike", "core", "blade"];
            const caligoColors = ["#ff9aa2", "#ffb7b2", "#ffdac1", "#e2f0cb", "#b5ead7", "#c7ceea"];

            function calculateSpeed() {
                let baseSpeed = 5.0;
                if (score >= 2000) {
                    let extraTier = Math.floor((score - 2000) / 500) + 1;
                    return baseSpeed * Math.pow(2, extraTier);
                } else if (score >= 1800) {
                    return baseSpeed * 2.2;
                } else if (score >= 1500) {
                    return baseSpeed * 1.9;
                } else if (score >= 1000) {
                    return baseSpeed * 1.6;
                } else if (score >= 500) {
                    return baseSpeed * 1.3;
                } else {
                    return baseSpeed;
                }
            }

            function resetObstacle() {
                obstacleWidth = Math.floor(30 + Math.random() * 30);
                obstacleHeight = Math.floor(35 + Math.random() * 35);
                
                obstacleSpeed = calculateSpeed();

                const isAir = Math.random() < 0.35;
                if (isAir) {
                    obstacleY = floorY - 110 + Math.random() * 30;
                } else {
                    obstacleY = floorY - obstacleHeight;
                }

                obstacleX = 950 + Math.random() * 350;
                obstacleShape = caligoShapes[Math.floor(Math.random() * caligoShapes.length)];
                obstacleColor = caligoColors[Math.floor(Math.random() * caligoColors.length)];

                if (!starActive && Math.random() < 0.25) {
                    starActive = true;
                    starX = 950 + Math.random() * 250;
                    starY = Math.random() < 0.5 ? floorY - 120 : floorY - 50; 
                }

                if (score >= 300 && Math.random() < 0.35) {
                    let offsets = [-45, -30, 20, 35];
                    targetFloorY = baseFloorY + offsets[Math.floor(Math.random() * offsets.length)];
                } else {
                    targetFloorY = baseFloorY;
                }
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
                    jumpVelocity = -18;
                }
            }

            canvas.addEventListener("click", function(e) {
                initAudio();
                if (!hasImage) return;

                const rect = canvas.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;

                if (isGameOver) {
                    isGameOver = false;
                    score = 0;
                    floorY = baseFloorY;
                    targetFloorY = baseFloorY;
                    starActive = false;
                    achievedMilestones = {};
                    resetObstacle();
                    jumpHeight = 0;
                    jumpCount = 0;
                    isCrouching = false;
                    return;
                }

                if (isPaused) {
                    if (mouseX >= 375 && mouseX <= 575 && mouseY >= 230 && mouseY <= 270) {
                        startCountdown();
                    }
                    else if (mouseX >= 375 && mouseX <= 575 && mouseY >= 290 && mouseY <= 330) {
                        score = 0;
                        floorY = baseFloorY;
                        targetFloorY = baseFloorY;
                        starActive = false;
                        achievedMilestones = {};
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
                initAudio();
                if (!hasImage) return;

                if (e.code === "Space") {
                    e.preventDefault();
                    if (isGameOver) {
                        isGameOver = false;
                        score = 0;
                        floorY = baseFloorY;
                        targetFloorY = baseFloorY;
                        starActive = false;
                        achievedMilestones = {};
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

            function drawPoseCharacter(x, currentFloorY, landmarks, crouching) {
                ctx.strokeStyle = "SKIN_COLOR_PLACEHOLDER";
                ctx.fillStyle = "SKIN_COLOR_PLACEHOLDER";
                ctx.lineWidth = 4;
                ctx.lineCap = "round";
                ctx.shadowColor = "SKIN_COLOR_PLACEHOLDER";
                ctx.shadowBlur = 8;

                let scale = crouching ? 65 : 100;

                if (landmarks && landmarks.length > 0) {
                    let maxY = -999;
                    landmarks.forEach(function(lm, idx) {
                        if ([27, 28, 29, 30, 31, 32].indexOf(idx) !== -1 && lm.visibility > 0.2) {
                            if (lm.y > maxY) maxY = lm.y;
                        }
                    });

                    if (maxY === -999) {
                        if (landmarks[23] && landmarks[24]) {
                            maxY = Math.max(landmarks[23].y, landmarks[24].y) + 0.3;
                        } else {
                            maxY = 0.85;
                        }
                    }

                    let feetYScaled = (maxY - 0.5) * scale;
                    let calculatedOffsetY = currentFloorY - feetYScaled;

                    POSE_CONNECTIONS.forEach(function(pair) {
                        const i = pair[0];
                        const j = pair[1];
                        const pt1 = landmarks[i];
                        const pt2 = landmarks[j];
                        if (pt1 && pt2 && pt1.visibility > 0.3 && pt2.visibility > 0.3) {
                            ctx.beginPath();
                            ctx.moveTo(x + (pt1.x - 0.5) * scale, calculatedOffsetY + (pt1.y - 0.5) * scale);
                            ctx.lineTo(x + (pt2.x - 0.5) * scale, calculatedOffsetY + (pt2.y - 0.5) * scale);
                            ctx.stroke();
                        }
                    });

                    const nose = landmarks[0];
                    if (nose) {
                        ctx.beginPath();
                        ctx.arc(x + (nose.x - 0.5) * scale, calculatedOffsetY + (nose.y - 0.5) * scale - 10, 14, 0, Math.PI * 2);
                        ctx.fill();
                    }

                    landmarks.forEach(function(lm, idx) {
                        if ([11,12,13,14,15,16,23,24,25,26,27,28].indexOf(idx) !== -1 && lm.visibility > 0.3) {
                            ctx.beginPath();
                            ctx.arc(x + (lm.x - 0.5) * scale, calculatedOffsetY + (lm.y - 0.5) * scale, 4, 0, Math.PI * 2);
                            ctx.fillStyle = "#ffffff";
                            ctx.fill();
                            ctx.fillStyle = "SKIN_COLOR_PLACEHOLDER";
                        }
                    });
                } else {
                    let baseOffsetY = crouching ? currentFloorY - 20 : currentFloorY - 50;
                    ctx.beginPath(); ctx.arc(x, baseOffsetY - 30, 14, 0, Math.PI * 2); ctx.fill();
                    ctx.beginPath(); ctx.moveTo(x, baseOffsetY - 16); ctx.lineTo(x, baseOffsetY + 15); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(x - 15, baseOffsetY - 8); ctx.lineTo(x + 15, baseOffsetY - 8); ctx.stroke();
                }
                ctx.shadowBlur = 0;
            }

            function drawStar(cx, cy, spikes, outerRadius, innerRadius) {
                let rot = (Math.PI / 2) * 3;
                let x = cx;
                let y = cy;
                let step = Math.PI / spikes;

                ctx.fillStyle = "#ffdf00";
                ctx.shadowColor = "#ffdf00";
                ctx.shadowBlur = 15;
                ctx.beginPath();
                ctx.moveTo(cx, cy - outerRadius);
                for (let i = 0; i < spikes; i++) {
                    x = cx + Math.cos(rot) * outerRadius;
                    y = cy + Math.sin(rot) * outerRadius;
                    ctx.lineTo(x, y);
                    rot += step;

                    x = cx + Math.cos(rot) * innerRadius;
                    y = cy + Math.sin(rot) * innerRadius;
                    ctx.lineTo(x, y);
                    rot += step;
                }
                ctx.lineTo(cx, cy - outerRadius);
                ctx.closePath();
                ctx.fill();
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
                let bgGrad = ctx.createLinearGradient(0, 0, 0, 520);
                bgGrad.addColorStop(0, "#1e1e2f");
                bgGrad.addColorStop(1, "#3b3b58");
                ctx.fillStyle = bgGrad;
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "rgba(255, 222, 215, 0.4)";
                let stars = [ [70,50], [180,100], [330,40], [450,130], [560,70], [680,150], [820,55], [100,210], [400,260], [800,180] ];
                stars.forEach(s => { ctx.fillRect(s[0], s[1], 3, 3); });
            }

            function update() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                let themeLevel = Math.floor(score / 1000) % 6;
                drawGorgeousBackground(themeLevel);

                floorY += (targetFloorY - floorY) * 0.05;

                ctx.strokeStyle = "#ffb7b2";
                ctx.lineWidth = 4;
                ctx.beginPath(); ctx.moveTo(0, floorY); ctx.lineTo(950, floorY); ctx.stroke();

                if (!hasImage) {
                    ctx.fillStyle = "#ffb7b2";
                    ctx.font = "bold 20px 'Quicksand', sans-serif";
                    ctx.textAlign = "center";
                    ctx.fillText("🐾 상단에서 내 사진을 업로드해 주세요!", canvas.width / 2, canvas.height / 2 - 15);
                    ctx.fillStyle = "#b5ead7";
                    ctx.font = "14px 'Quicksand', sans-serif";
                    ctx.fillText("Upload a photo to start playing!", canvas.width / 2, canvas.height / 2 + 20);
                } else {
                    if (!isPaused && !isCountdown && !isGameOver) {
                        if (jumpCount > 0) {
                            jumpHeight += jumpVelocity;
                            jumpVelocity += 1.05;
                            
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

                        targetMilestones.forEach(m => {
                            if (score >= m && !achievedMilestones[m]) {
                                achievedMilestones[m] = true;
                                celebrationText = "🎉 " + m + "점 돌파! 대단해요! 🎉";
                                celebrationTimer = 90;
                            }
                        });

                        if (starActive) {
                            starX -= obstacleSpeed;
                            if (starX < -50) {
                                starActive = false;
                            }

                            let currentFloor = floorY + jumpHeight;
                            if (
                                charX + 20 > starX - 15 &&
                                charX - 20 < starX + 15 &&
                                currentFloor > starY - 30 &&
                                currentFloor - 80 < starY + 15
                            ) {
                                score += 100; 
                                starActive = false;
                                starEffectTimer = 30;
                                playPpyongSound();
                            }
                        }

                        let currentFloor = floorY + jumpHeight;
                        let obsLeft = obstacleX;
                        let obsRight = obstacleX + obstacleWidth;
                        let obsTop = obstacleY;
                        let obsBottom = obstacleY + obstacleHeight;

                        let charLeft = charX - 22;
                        let charRight = charX + 22;
                        let charTop = isCrouching ? currentFloor - 45 : currentFloor - 105;
                        let charBottom = currentFloor;

                        if (
                            charRight > obsLeft &&
                            charLeft < obsRight &&
                            charBottom > obsTop &&
                            charTop < obsBottom
                        ) {
                            isGameOver = true;
                            if (score > highScore) {
                                highScore = score;
                                localStorage.setItem("dino_high_score", highScore);
                            }
                        }
                    }

                    drawObstacle();

                    if (starActive) {
                        drawStar(starX, starY, 5, 16, 8);
                    }

                    if (starEffectTimer > 0) {
                        starEffectTimer--;
                        ctx.fillStyle = "#ffdf00";
                        ctx.font = "bold 18px 'Quicksand', sans-serif";
                        ctx.textAlign = "center";
                        ctx.shadowColor = "#ffdf00";
                        ctx.shadowBlur = 10;
                        ctx.fillText("🌟 BONUS x2 SCORE! 🌟", charX + 20, floorY + jumpHeight - 110);
                        ctx.shadowBlur = 0;
                    }

                    if (celebrationTimer > 0) {
                        celebrationTimer--;
                        ctx.fillStyle = "rgba(255, 218, 193, 0.25)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#ffdf00";
                        ctx.font = "bold 28px 'Quicksand', sans-serif";
                        ctx.textAlign = "center";
                        ctx.shadowColor = "#ffb7b2";
                        ctx.shadowBlur = 20;
                        ctx.fillText(celebrationText, canvas.width / 2, 130);
                        ctx.shadowBlur = 0;
                    }

                    let currentFloor = floorY + jumpHeight;
                    drawPoseCharacter(charX, currentFloor, poseLandmarks, isCrouching);

                    const themeNames = ["✨ 포근한 밤", "🌸 몽환 숲", "☁️ 노을 바다", "🌊 오션 파스텔", "🪐 별빛 행성", "🏰 판타지 성"];
                    ctx.fillStyle = "#f8fafc";
                    ctx.font = "bold 14px 'Quicksand', sans-serif";
                    ctx.textAlign = "left";
                    ctx.fillText("⭐ SCORE: " + score + " [" + themeNames[themeLevel] + "]", 20, 35);

                    ctx.fillStyle = "rgba(35, 35, 54, 0.85)";
                    ctx.fillRect(750, 460, 180, 45);
                    ctx.strokeStyle = "#ffdac1";
                    ctx.lineWidth = 2;
                    ctx.strokeRect(750, 460, 180, 45);

                    ctx.fillStyle = "#ffdac1";
                    ctx.font = "bold 13px 'Quicksand', sans-serif";
                    ctx.textAlign = "left";
                    ctx.fillText("🏆 BEST: " + highScore, 765, 480);
                    ctx.fillStyle = "#b5ead7";
                    ctx.fillText("⭐ NOW: " + score, 765, 498);

                    if (isGameOver) {
                        ctx.fillStyle = "rgba(30, 30, 47, 0.92)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#ffb7b2";
                        ctx.font = "bold 36px 'Quicksand', sans-serif";
                        ctx.textAlign = "center";
                        ctx.fillText("GAME OVER 🐾", canvas.width / 2, canvas.height / 2 - 40);

                        ctx.fillStyle = "#ffdf00";
                        ctx.font = "bold 20px 'Quicksand', sans-serif";
                        ctx.fillText("🏆 최고 기록: " + highScore, canvas.width / 2, canvas.height / 2);

                        ctx.fillStyle = "#b5ead7";
                        ctx.font = "18px 'Quicksand', sans-serif";
                        ctx.fillText("이번 점수: " + score, canvas.width / 2, canvas.height / 2 + 35);

                        ctx.fillStyle = "#f8fafc";
                        ctx.font = "15px 'Quicksand', sans-serif";
                        ctx.fillText("클릭 또는 스페이스바로 다시 시작!", canvas.width / 2, canvas.height / 2 + 80);
                    }

                    if (isPaused) {
                        ctx.fillStyle = "rgba(30, 30, 47, 0.9)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#ffb7b2";
                        ctx.font = "bold 30px 'Quicksand', sans-serif";
                        ctx.textAlign = "center";
                        ctx.fillText("GAME PAUSED ⏸️", canvas.width / 2, 140);

                        ctx.fillStyle = "#b5ead7";
                        ctx.fillRect(375, 230, 200, 40);
                        ctx.fillStyle = "#1e1e2f";
                        ctx.font = "bold 15px 'Quicksand', sans-serif";
                        ctx.fillText("▶ 이어서 하기", canvas.width / 2, 255);

                        ctx.fillStyle = "#ffdac1";
                        ctx.fillRect(375, 290, 200, 40);
                        ctx.fillStyle = "#1e1e2f";
                        ctx.fillText("🔄 처음으로", canvas.width / 2, 315);
                    }

                    if (isCountdown) {
                        ctx.fillStyle = "rgba(30, 30, 47, 0.9)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#ffdac1";
                        ctx.font = "bold 70px 'Quicksand', sans-serif";
                        ctx.textAlign = "center";
                        ctx.shadowColor = "#ffdac1";
                        ctx.shadowBlur = 15;
                        ctx.fillText(countdownValue, canvas.width / 2, canvas.height / 2 + 20);
                        ctx.shadowBlur = 0;

                        ctx.fillStyle = "#b5ead7";
                        ctx.font = "18px 'Quicksand', sans-serif";
                        ctx.fillText("준비하세요!", canvas.width / 2, canvas.height / 2 - 60);
                    }
                }

                requestAnimationFrame(update);
            }

            update();
        </script>
    </body>
    </html>
    """

    game_html = raw_html.replace("PY_AVATAR_LIST_PLACEHOLDER", py_avatar_list_json)
    game_html = game_html.replace("PY_ACTIVE_INDEX_PLACEHOLDER", str(py_active_index))
    game_html = game_html.replace("SKIN_COLOR_PLACEHOLDER", skin_color)

    components.html(game_html, height=580)
