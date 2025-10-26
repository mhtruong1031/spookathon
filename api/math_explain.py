from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the current directory to Python path to import services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.getExplanation import get_explanation_math, is_math_problem

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/math/explain")
async def explain_math(file: UploadFile = File(...)):
    image = await file.read()
    if not is_math_problem(image):
        return "This is not a math problem"
    return get_explanation_math(image)
