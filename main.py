import os
import io
from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.responses import Response
from PIL import Image

app = FastAPI()

# Secrets
RAPIDAPI_SECRET = os.getenv("RAPIDAPI_SECRET", "DefaultSecretForTesting") 

@app.get("/")
def home():
    return {"status": "Online", "mode": "Render Native (Lite + Alpha Matting)"}

@app.post("/remove-bg")
async def remove_background(
    file: UploadFile = File(...), 
    x_rapidapi_proxy_secret: str = Header(None)
):
    # 1. Security Check
    if x_rapidapi_proxy_secret != RAPIDAPI_SECRET:
         raise HTTPException(status_code=403, detail="Unauthorized Access")

    try:
        # 2. Lazy Import (Prevents Startup Timeout)
        # We import here so the server starts instantly
        from rembg import remove, new_session
        
        # We use the LITE model (4MB) to guarantee it fits in Free RAM
        model_name = "u2netp"
        session = new_session(model_name)

        # 3. Read Image
        image_data = await file.read()
        input_image = Image.open(io.BytesIO(image_data))

        # 4. SAFETY RESIZE (Crucial for Free Tier)
        # Alpha Matting is memory expensive. We must shrink 4K images 
        # to ~1000px or the server will crash.
        max_dim = 1000
        if input_image.width > max_dim or input_image.height > max_dim:
            input_image.thumbnail((max_dim, max_dim))
            print("Image resized for memory safety.")

        # 5. Process with ALPHA MATTING
        # This is the "Secret Sauce". It uses math to clean up the edges 
        # of the Lite model output.
        output_image = remove(
            input_image, 
            session=session,
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10
        )

        # 6. Return Result
        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG')
        
        return Response(content=img_byte_arr.getvalue(), media_type="image/png")

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}
