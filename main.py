import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.responses import Response
from PIL import Image
import io

app = FastAPI()

RAPIDAPI_SECRET = os.getenv("RAPIDAPI_SECRET", "DefaultSecretForTesting") 

@app.get("/")
def home():
    return {"status": "Online", "message": "Lite Mode Active"}

@app.post("/remove-bg")
async def remove_background(
    file: UploadFile = File(...), 
    x_rapidapi_proxy_secret: str = Header(None)
):
    if x_rapidapi_proxy_secret != RAPIDAPI_SECRET:
         raise HTTPException(status_code=403, detail="Unauthorized Access")

    try:
        print("Importing Lite AI engine...")
        from rembg import remove, new_session 
        
        # --- THE FIX ---
        # "u2netp" is the lightweight version (4MB).
        # It runs perfectly on free servers.
        model_name = "u2netp" 
        session = new_session(model_name)

        image_data = await file.read()
        input_image = Image.open(io.BytesIO(image_data))
        
        # Process
        output_image = remove(input_image, session=session)

        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG')
        
        return Response(content=img_byte_arr.getvalue(), media_type="image/png")

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}
