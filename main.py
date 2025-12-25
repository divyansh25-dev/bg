import os
# We ONLY import lightweight things at the top
from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.responses import Response
from PIL import Image
import io

app = FastAPI()

# Get Secret from Environment
RAPIDAPI_SECRET = os.getenv("RAPIDAPI_SECRET", "DefaultSecretForTesting") 

# --- 1. INSTANT HEALTH CHECK ---
# Since we didn't import rembg at the top, this runs in 0.1 seconds.
# Render will see this port open immediately.
@app.get("/")
def home():
    return {"status": "Online", "message": "System is live."}

@app.post("/remove-bg")
async def remove_background(
    file: UploadFile = File(...), 
    x_rapidapi_proxy_secret: str = Header(None)
):
    # Security Check
    if x_rapidapi_proxy_secret != RAPIDAPI_SECRET:
         raise HTTPException(status_code=403, detail="Unauthorized Access")

    try:
        # --- 2. LAZY IMPORT (The Magic Fix) ---
        # We import rembg ONLY when needed. 
        # The first request will be slow, but the server won't crash on startup.
        print("Importing AI engine...")
        from rembg import remove, new_session 
        
        # We use the standard model to be safe on RAM
        # You can change this to "birefnet-general" later if it's stable
        model_name = "u2net" 
        session = new_session(model_name)

        # Process Image
        image_data = await file.read()
        input_image = Image.open(io.BytesIO(image_data))
        output_image = remove(input_image, session=session)

        # Return Image
        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG')
        
        return Response(content=img_byte_arr.getvalue(), media_type="image/png")

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}
