import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse,RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

import os

from dataclasses import dataclass

from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from settings import Settings
from repository import SupabaseUserRepository
from models.dtos import CreatedUser
from supabase import create_client, Client
from services import UserService
from models.requests import CreateUserRequest
from models.responses import CreateUserResponse
from dependencies import get_supabase_client, get_user_repository, get_user_service

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



@app.post("/users/{license_holder_id}", response_model=CreateUserResponse, status_code=201)
def create_user(
    license_holder_id: UUID,
    body: CreateUserRequest,
    service: UserService = Depends(get_user_service),
):
    try:
        user = service.register_user(body.username, body.password, license_holder_id=str(license_holder_id))
        return CreateUserResponse(id=user.id, email=user.email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@app.get("/users/{license_holder_id}/students", response_model=list[CreateUserResponse])
def get_students(
    license_holder_id: UUID,
    service: UserService = Depends(get_user_service),
):
    try:
        students = service.get_students_by_license_holder(str(license_holder_id))
        return [CreateUserResponse(id=str(s.id), email=s.email) for s in students]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
