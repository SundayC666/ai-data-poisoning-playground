import uvicorn
import numpy as np
import io
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.default import _rate_limit_exceeded_handler

# ---- App & Model Initialization ----
app = FastAPI(title="AI Security Demo API", docs_url = None, redoc = None, oprnapi_api = None)
model = None

# ---- FastAPI Events ----
@app.on_event("startup")
def load_model():
    """Load the model once on server startup to avoid reloading on every request."""
    global model
    model = ResNet50(weights='imagenet')

# ===== slowapi 設定（關鍵）=====
def get_client_ip(req: Request) -> str:
    """
    在 Render（反向代理）後面，優先取 X-Forwarded-For 第一個 IP，
    取不到再退回 request.client.host
    """
    xff = req.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return req.client.host if req.client else "unknown"
# 你可以改為 get_remote_address（會用 request.client.host），
# 但在代理後面更推薦用上面的 get_client_ip
limiter = Limiter(
    key_func=get_client_ip,       # 每個 IP 單獨計數
    headers_enabled=True,         # 在回應頭顯示限速資訊
)
# 掛上 middleware 與 429 handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.get("/health")
def health():
    return {"status":"ok"}

# ===== 你的 /predict 路由 =====
# 每個 IP：每分鐘最多 6 次、每小時最多 60 次（你可調）
@limiter.limit("6/minute;60/hour")
@app.post("/predict")
async def predict(request: Request, file: UploadFile = File(...)):
    # ⬇️ 你的既有推論邏輯放這（保留原來程式即可）
    # data = await file.read()
    # img = Image.open(io.BytesIO(data)).convert("RGB")
    # ... TensorFlow 推論 ...
    # return {"object": "...", "confidence": 0.95}
    return {"ok": True}

# ---- CORS Middleware ----
# Allows your Vue frontend to access this backend API
ALLOWED_ORIGINS = [
    "https://sundayc666.github.io",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS, # The address of your Vue App
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# ---- API Endpoint ----
@app.post("/predict", tags=["Prediction"])
@app.post("/predict/", tags=["Prediction"])
async def predict_image(file: UploadFile = File(...)):
    """Accept an image file, process it, and return the AI model's prediction."""
    
    # Read the contents of the uploaded file
    contents = await file.read()
    
    # Convert the bytes to an image object
    # This is the line that was likely causing the error before
    img = Image.open(io.BytesIO(contents)).convert('RGB').resize((224, 224))
    
    # Preprocess the image and make a prediction
    img_array = image.img_to_array(img)
    img_array_expanded = np.expand_dims(img_array, axis=0)
    processed_img = preprocess_input(img_array_expanded)
    predictions = model.predict(processed_img)
    decoded_predictions = decode_predictions(predictions, top=1)[0]
    
    # Format and return the result
    result = {"object": decoded_predictions[0][1], "confidence": float(decoded_predictions[0][2])}
    return result

# ---- Run Instruction ----
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
