import uvicorn
import numpy as np
import io
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image

# ---- App & Model Initialization ----
app = FastAPI(title="AI Security Demo API")
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
