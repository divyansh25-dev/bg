import os # <--- ADD THIS
from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.responses import Response
from rembg import remove, new_session
from PIL import Image
import io

app = FastAPI()

# --- CONFIGURATION ---
MODEL_NAME = "birefnet-general"

# Only load model if we are NOT in a build step (optional safety, but good to have)
# For now, we keep it simple.
print(f"Loading AI Model: {MODEL_NAME}...")
try:
    session = new_session(MODEL_NAME)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Model loading warning (ignore if building docker): {e}")
    session = None

# --- SECURITY CHANGE ---
# Instead of "MY_SUPER_SECRET...", we ask the Operating System (os) for it.
# If it can't find one, it defaults to a placeholder.
RAPIDAPI_SECRET = os.getenv("RAPIDAPI_SECRET", "DefaultSecretForTesting") 

@app.get("/")
def home():
    return {"status": "Online", "model": MODEL_NAME}

@app.post("/remove-bg")
async def remove_background(
    file: UploadFile = File(...), 
    x_rapidapi_proxy_secret: str = Header(None)
):
    # Security Check
    if x_rapidapi_proxy_secret != RAPIDAPI_SECRET:
         raise HTTPException(status_code=403, detail="Unauthorized Access")

    try:
        image_data = await file.read()
        input_image = Image.open(io.BytesIO(image_data))

        # Use the session
        if session:
            output_image = remove(input_image, session=session)
        else:
            # Fallback if session failed to load
            output_image = remove(input_image)

        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG')
        
        return Response(content=img_byte_arr.getvalue(), media_type="image/png")

    except Exception as e:
        return {"error": str(e)}
