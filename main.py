import os
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.responses import Response

app = FastAPI()

# --- CONFIGURATION ---
# We use the free Hugging Face API URL for the BriaAI model (State of the Art)
# This runs on THEIR powerful GPUs, not your weak server.
API_URL = "https://api-inference.huggingface.co/models/briaai/RMBG-1.4"

# Get Secrets from Render
RAPIDAPI_SECRET = os.getenv("RAPIDAPI_SECRET", "DefaultSecretForTesting") 
HF_TOKEN = os.getenv("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") # <--- We will add this in Render next

@app.get("/")
def home():
    return {"status": "Online", "mode": "Broker Mode (Hugging Face)"}

@app.post("/remove-bg")
async def remove_background(
    file: UploadFile = File(...), 
    x_rapidapi_proxy_secret: str = Header(None)
):
    # 1. Security Check
    if x_rapidapi_proxy_secret != RAPIDAPI_SECRET:
         raise HTTPException(status_code=403, detail="Unauthorized Access")

    if not HF_TOKEN:
        return {"error": "Server configuration error: HF_TOKEN is missing."}

    try:
        # 2. Read the Image from the User
        image_data = await file.read()

        # 3. Forward it to the Super Computer (Hugging Face)
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        
        # We send the raw image bytes directly
        response = requests.post(API_URL, headers=headers, data=image_data)

        # 4. Check if they did the job
        if response.status_code != 200:
            return {"error": f"AI Provider Error: {response.text}"}

        # 5. Return the clean image to the user
        return Response(content=response.content, media_type="image/png")

    except Exception as e:
        return {"error": str(e)}

