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
    st.info("사진을 올리면 **AI가 관절을 스캔**하여 관절 캐릭터를 생성합니다! **클릭하여 점프**하며, **ESC 키**를 눌러 일시 정지 메뉴를 열 수 있습니다.")
    
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
            let isJumping = false;
            let jumpVelocity = 0;
            let jumpHeight = 0;
            let obstacleX = 700;
            let score = 0;
            let isPaused = false;

            // 마우스 클릭 이벤트 (게임 중 점프 또는 일시 정지 메뉴 버튼 클릭 처리)
            canvas.addEventListener("click", function(e) {
                if (!hasImage) return;

                const rect = canvas.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;

                if (isPaused) {
                    // 1. "이어서 재생" 버튼 클릭 영역 검사 (캔버스 중앙 기준)
                    if (mouseX >= 225 && mouseX <= 425 && mouseY >= 210 && mouseY <= 250) {
                        isPaused = false;
                    }
                    // 2. "처음으로 돌아가기" 버튼 클릭 영역 검사
                    else if (mouseX >= 225 && mouseX <= 425 && mouseY >= 270 && mouseY <= 310) {
                        score = 0;
                        obstacleX = 700;
                        jumpHeight = 0;
                        isJumping = false;
                        isPaused = false;
                    }
                    return;
                }

                if (!isJumping) {
                    isJumping = true;
                    jumpVelocity = -14;
                }
            });

            // ESC 키 입력 시 일시 정지 토글
            window.addEventListener("keydown", function(e) {
                if (e.key === "Escape" && hasImage) {
                    isPaused = !isPaused;
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
                    if (!isPaused) {
                        if (isJumping) {
                            jumpHeight += jumpVelocity;
                            jumpVelocity += 0.8;
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
                    }

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
                    ctx.fillText("🖱️ Click to Jump | [ESC] Pause", 300, 40);

                    // 일시 정지 메뉴 오버레이
                    if (isPaused) {
                        ctx.fillStyle = "rgba(15, 52, 96, 0.85)";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.fillStyle = "#ff007f";
                        ctx.font = "bold 26px 'Courier New'";
                        ctx.textAlign = "center";
                        ctx.fillText("GAME PAUSED", canvas.width / 2, 120);

                        // 버튼 1: 이어서 재생
                        ctx.fillStyle = "#00fff5";
                        ctx.fillRect(225, 210, 200, 40);
                        ctx.fillStyle = "#0f3460";
                        ctx.font = "bold 15px 'Courier New'";
                        ctx.fillText("▶ 이어서 재생", canvas.width / 2, 235);

                        // 버튼 2: 처음으로 돌아가기
                        ctx.fillStyle = "#ffdd59";
                        ctx.fillRect(225, 270, 200, 40);
                        ctx.fillStyle = "#0f3460";
                        ctx.fillText("🔄 처음으로", canvas.width / 2, 295);
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
