from vuer import Vuer, VuerSession
from vuer.schemas import MotionControllers
from vuer.schemas import (
    Text3D,
    Text,
    Billboard,
    DefaultScene,
    AmbientLight,
    DirectionalLight,
    MeshNormalMaterial,
    Scene, 
    ImageBackground
)
from asyncio import sleep
from pprint import pprint
import imageio as iio
from tqdm import tqdm
import os
from vuer import Vuer, VuerSession
from vuer.events import ClientEvent
import cv2

KEY_FILE = os.path.abspath("key.pem")
CERT_FILE = os.path.abspath("cert.pem")

print(f"使用憑證: {KEY_FILE}, {CERT_FILE}")

# ❌ 完全自訂，不依賴 vuer 內建 HTML
app = Vuer(
    host="0.0.0.0",
    port=4000,
    cert=CERT_FILE,  # SSL 證書
    key=KEY_FILE,    # SSL 私鑰
    # static_dir=None  # 你要自己提供前端就保持 None
)

@app.add_handler("CAMERA_MOVE")
async def on_camera(event: ClientEvent, sess: VuerSession):
    assert event == "CAMERA_MOVE", "the event type should be correct"
    # print("camera event", event.etype, event.value)
@app.add_handler("SESSION_CONNECTED")
async def connected(event, session):
    print("✅ WebSocket 連線成功")

@app.add_handler("CONTROLLER_MOVE")
async def controller(event, session):
    pprint(event.value)


@app.spawn(start=True)
async def main(session: VuerSession):
    print("🚀 HTTPS vuer 運行（無靜態衝突）")
    session.upsert(MotionControllers(stream=True, key="motion-controller", left=True, right=True))
    while True:
        while True:
            try:
                cap = cv2.VideoCapture(3)
                if not cap.isOpened():
                    print("Failed to open camera")
                    return
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        await sleep(0.016)
                        continue
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # use the upsert(..., to="bgChildren") syntax, so it is in global frame.
                    session.upsert(
                        ImageBackground(
                            # Can scale the images down.
                            frame[::1, ::1, :],
                            # One of ['b64png', 'png', 'b64jpeg', 'jpeg']
                            # 'b64png' does not work for some reason, but works for the nerf demo.
                            # 'jpeg' encoding is significantly faster than 'png'.
                            format="jpeg",
                            quality=20,
                            key="background",
                            interpolate=True,
                            fixed=True,
                            distanceToCamera=1,
                            position=[0, 1.5, -3],
                            ### Can also rotate the plane in-place.
                            # rotation=[-0.25, 0, 0],
                        ),
                        # we place this into the background children list, so that it is
                        # not affected by the global rotation
                        # to="bgChildren",
                    )
                    # 'jpeg' encoding should give you about 30fps with a 16ms wait in-between.
                    # this is mostly limited by the python server side.
                    await sleep(0.016)
            except Exception as e:
                print("Error in show_heatmap:", e)
