import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.responses import Response
from rembg import remove, new_session
from PIL import Image
import io

app = FastAPI()

# --- CONFIGURATION ---
MODEL_NAME = "birefnet-general"

# GLOBAL VARIABLE (Starts Empty)
# We do NOT load the model here anymore.
# This allows the server to start instantly.
model_session = None

# Get Secret from Environment (Render)
RAPIDAPI_SECRET = os.getenv("RAPIDAPI_SECRET", "DefaultSecretForTesting") 

@app.get("/")
def home():
    return {"status": "Online", "message": "Server is running. Model will load on first request."}

@app.post("/remove-bg")
async def remove_background(
    file: UploadFile = File(...), 
    x_rapidapi_proxy_secret: str = Header(None)
):
    # 1. Security Check
    if x_rapidapi_proxy_secret != RAPIDAPI_SECRET:
         raise HTTPException(status_code=403, detail="Unauthorized Access")

    global model_session

    try:
        # 2. LAZY LOADING (The Fix)
        # We check if the model is loaded. If not, we load it NOW.
        # This means the VERY FIRST request will take 1-2 minutes.
        # All requests after that will be fast.
        if model_session is None:
            print("First request detected. Downloading AI Model now...")
            model_session = new_session(MODEL_NAME)
            print("Model loaded!")

        # 3. Read Image
        image_data = await file.read()
        input_image = Image.open(io.BytesIO(image_data))

        # 4. Process using the loaded session
        output_image = remove(input_image, session=model_session)

        # 5. Return Image
        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG')
        
        return Response(content=img_byte_arr.getvalue(), media_type="image/png")

    except Exception as e:
        return {"error": str(e)}
