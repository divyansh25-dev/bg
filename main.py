from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.responses import Response
from rembg import remove, new_session
from PIL import Image
import io

app = FastAPI()

# --- CONFIGURATION ---
# This is where we upgrade the model. 
# "birefnet-general" is the high-quality model for general use.
# It is heavier (approx 170MB) but much smarter than standard U2Net.
MODEL_NAME = "birefnet-general"

# We load the "Associate" (the model) once when the app starts.
# This prevents the app from reloading the brain for every single client.
print(f"Loading AI Model: {MODEL_NAME}...")
session = new_session(MODEL_NAME)
print("Model loaded successfully.")

# Your Secret Password for RapidAPI
RAPIDAPI_SECRET = "MY_SUPER_SECRET_KEY_123"

@app.get("/")
def home():
    return {"status": "Online", "model": MODEL_NAME}

@app.post("/remove-bg")
async def remove_background(
    file: UploadFile = File(...), 
    x_rapidapi_proxy_secret: str = Header(None)
):
    # 1. Security Check
    # If testing locally, you can comment these two lines out temporarily
    if x_rapidapi_proxy_secret != RAPIDAPI_SECRET:
         raise HTTPException(status_code=403, detail="Unauthorized Access")

    try:
        # 2. Read Image
        image_data = await file.read()
        input_image = Image.open(io.BytesIO(image_data))

        # 3. Process using the specific BiRefNet Session
        # We pass 'session=session' to use our high-quality loaded model
        output_image = remove(input_image, session=session)

        # 4. Return Image
        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG')
        
        return Response(content=img_byte_arr.getvalue(), media_type="image/png")

    except Exception as e:
        return {"error": str(e)}