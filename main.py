from vuer import Vuer, VuerSession
from vuer.schemas import MotionControllers
import asyncio
import os

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

@app.add_handler("SESSION_CONNECTED")
async def connected(event, session):
    print("✅ WebSocket 連線成功")

@app.add_handler("CONTROLLER_MOVE")
async def controller(event, session):
    print(f"🎮 控制器移動: {event}")

@app.spawn(start=True)
async def main(session: VuerSession):
    print("🚀 HTTPS vuer 運行（無靜態衝突）")
    session.upsert(MotionControllers(stream=True, key="motion-controller", left=True, right=True))
    while True:
        await asyncio.sleep(0.1)
