from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

import cv2
import numpy as np
from pathlib import Path
import tempfile
import shutil
import os
from typing import List
from google.cloud import storage
from PIL import Image
import io
import uvicorn


app = FastAPI(
    title="BluStory App Image to Video Converter",
    description="Convert uploaded images to video and store in Google Cloud Storage"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------
# Google Cloud Storage setup
# ---------------------------
GCS_BUCKET_NAME = "blustoryapp"   # Replace with your bucket name
GCS_PROJECT_ID = "caesaraiapis"   # Replace with your project ID

storage_client = storage.Client(project=GCS_PROJECT_ID)
bucket = storage_client.bucket(GCS_BUCKET_NAME)

# Temporary directory
TEMP_DIR = Path(tempfile.mkdtemp())
os.makedirs(TEMP_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Welcome to the BluStory App Image to Video Converter API"}

@app.post("/convert-to-video/")
async def convert_images_to_video(
    files: List[UploadFile] = File(...),
    fps: int = Form(1),
    video_name: str = Form("output_video.webm"),
    seconds_per_image: int = Form(5)
):
    """
    Convert uploaded images to a WebM video and upload it to Google Cloud Storage.
    Each image will stay in the video for 5 seconds.
    """
    image_paths = []

    try:
        # Save uploaded images temporarily
        for i, file in enumerate(files):
            if not file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not an image")

            contents = await file.read()
            image = Image.open(io.BytesIO(contents)).convert("RGB")  # Force RGB
            print(f"Processing image {file.filename} | size: {image.size}, mode: {image.mode}")

            temp_image_path = TEMP_DIR / f"frame_{i:03d}.jpg"
            image.save(temp_image_path, "JPEG", quality=95)
            image_paths.append(str(temp_image_path))

        # Sort to maintain order
        image_paths.sort()

        # Read first frame to get dimensions
        first_frame = cv2.imread(image_paths[0])
        if first_frame is None:
            raise HTTPException(status_code=500, detail="Failed to read first image")

        height, width, layers = first_frame.shape
        temp_video_path = TEMP_DIR / "temp_video.webm"

        # Set up video writer (VP8 codec for WebM)
        fourcc = cv2.VideoWriter_fourcc(*"VP80")
        video_writer = cv2.VideoWriter(str(temp_video_path), fourcc, fps, (width, height), isColor=True)

        if not video_writer.isOpened():
            raise HTTPException(status_code=500, detail="Failed to open VideoWriter. Ensure OpenCV is built with libvpx support.")

        # Each image stays on screen for 5 seconds
      
        frames_per_image = int(fps * seconds_per_image)

        # Write frames
        for image_path in image_paths:
            frame = cv2.imread(image_path)
            if frame is None:
                raise HTTPException(status_code=500, detail=f"Failed to read {image_path}")

            # Ensure consistent frame size
            frame = cv2.resize(frame, (width, height))

            # Write the same frame multiple times to make it stay for 5 seconds
            for _ in range(frames_per_image):
                video_writer.write(frame)

        video_writer.release()
        cv2.destroyAllWindows()

        # Sanity check
        if not temp_video_path.exists() or os.path.getsize(temp_video_path) < 1024:
            raise HTTPException(status_code=500, detail="Generated video file is empty or invalid")

        # Upload to GCS
        gcs_blob = bucket.blob(f"videos/{video_name}")
        gcs_blob.upload_from_filename(str(temp_video_path), content_type="video/webm")
        gcs_blob.make_public()
        gcs_blob.cache_control = 'no-cache, max-age=0'
        gcs_blob.patch()

        # Cleanup
        temp_video_path.unlink(missing_ok=True)
        for path in image_paths:
            Path(path).unlink(missing_ok=True)

        return {
            "message": "Video created and uploaded successfully",
            "video_url": gcs_blob.public_url,
            "fps": fps,
            "seconds_per_image": seconds_per_image,
            "total_frames": len(image_paths) * frames_per_image,
            "resolution": f"{width}x{height}"
        }

    except Exception as e:
        print(f"Error during video creation: {e}")
        # Cleanup in case of errors
        for path in image_paths:
            Path(path).unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.on_event("shutdown")
async def cleanup():
    """Clean up temporary directory on shutdown"""
    shutil.rmtree(TEMP_DIR, ignore_errors=True)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
