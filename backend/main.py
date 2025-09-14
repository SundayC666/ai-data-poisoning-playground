import uvicorn
import numpy as np
import io
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware


# ---- App & Model Initialization ----
app = FastAPI(title="AI Security Demo API", docs_url = None, redoc = None, oprnapi_api = None)
model = None

# ---- FastAPI Events ----
@app.on_event("startup")
def load_model():
    """Load the model once on server startup to avoid reloading on every request."""
    global model
    model = ResNet50(weights='imagenet')

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

# 取客戶端 IP（在 Render 等代理後面優先看 X-Forwarded-For）
def get_client_ip(req: Request) -> str:
    xff = req.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return req.client.host if req.client else "unknown"
limiter = Limiter(
    key_func=get_client_ip,
    headers_enabled=True,   # 回應頭會帶上 X-RateLimit-* 資訊
)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    # 這裡的 request.state.* 由 slowapi middleware 設定
    remaining = getattr(request.state, "view_rate_remaining", None)
    reset     = getattr(request.state, "view_rate_reset", None)
    limit     = getattr(request.state, "view_rate_limit", None)
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please wait a bit and try again.",
            "limit": limit, "remaining": remaining, "reset": reset,
        },
    )

@app.get("/health")
def health():
    return {"status":"ok"}

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
