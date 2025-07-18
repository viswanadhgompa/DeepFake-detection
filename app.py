import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import cv2
import timm
from fastapi import FastAPI, File, UploadFile, HTTPException
import shutil
import os
import tempfile
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for Flask frontend (Running on port 5000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5501"],  # Your frontend domain
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods including OPTIONS
    allow_headers=["*"],
)







# Check server status
@app.get("/")
def home():
    return {"message": "Deepfake detection API is running!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}


# Device configuration (use GPU if available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Image transformation (same as model training)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load the trained ViT model
print("Loading model...")
try:
    model = timm.create_model('vit_large_patch16_224', pretrained=False, num_classes=2)
    model.load_state_dict(torch.load('/Users/vishwa/Documents/Backend deepfake/best_vit_model.pth', map_location=device))
    model.to(device)
    model.eval()
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    raise RuntimeError("Model loading failed. Check model path and compatibility.")

# Function to process video and classify frames
def predict_video(video_path):
    print(f"Processing video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Error opening video file.")

    frame_count = 0
    real_count = 0
    manipulated_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        image = transform(image).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(image)
            _, predicted = torch.max(outputs, 1)
        
        if predicted.item() == 0:
            real_count += 1
        else:
            manipulated_count += 1

        # Debug print every 10 frames
        if frame_count % 10 == 0:
            print(f"Processed {frame_count} frames...")
    
    cap.release()
    result = "Real" if real_count > manipulated_count else "Manipulated"
    print(f"Video processed. Result: {result}")
    return {
        "total_frames": frame_count,
        "real_frames": real_count,
        "manipulated_frames": manipulated_count,
        "result": result
    }


# API endpoint for video deepfake detection
import time  # 🔼 Add this near the top if not already

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    print(f"Received file: {file.filename}")
    
    try:
        start_time = time.time()

        # Save the file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            shutil.copyfileobj(file.file, temp_video)
            temp_video_path = temp_video.name

        result = predict_video(temp_video_path)

        scan_time = round(time.time() - start_time, 2)
        total = result["real_frames"] + result["manipulated_frames"]
        confidence = round(max(result["real_frames"], result["manipulated_frames"]) / total * 100, 2)

        return {
            "fileName": file.filename,
            "type": file.content_type,
            "scanTime": scan_time,
            "confidence": confidence,
            "result": result["result"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

    finally:
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
            print("Temporary file deleted.")


    return result
from pydantic import BaseModel

# Simulated in-memory database
fake_users_db = {
    "user@example.com": {
        "username": "testuser",
        "email": "user@example.com",
        "password": "123456",  # Insecure! Just for testing/demo
        "token": "fake-jwt-token"
    }
}

# Request models
class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

# LOGIN endpoint
@app.post("/login")
async def login_user(data: LoginRequest):
    user = fake_users_db.get(data.email)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": user["token"], "email": data.email}

# SIGNUP endpoint
@app.post("/signup")
async def signup_user(data: SignupRequest):
    if data.email in fake_users_db:
        raise HTTPException(status_code=409, detail="User already exists")
    
    # Save user (fake DB)
    fake_users_db[data.email] = {
        "username": data.username,
        "email": data.email,
        "password": data.password,
        "token": "fake-jwt-token"  # You can replace with a real token later
    }
    return {"access_token": "fake-jwt-token", "email": data.email}
