from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the current directory to Python path to import services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.getExplanation import get_explanation_math, get_explanation_graph, is_math_problem, parse_placeholder_response

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
    
    print("DEBUG API: Calling get_explanation_math...")
    raw_result = get_explanation_math(image)
    print(f"DEBUG API: Raw result: {raw_result[:200]}...")
    
    print("DEBUG API: Calling parse_placeholder_response...")
    processed_result = parse_placeholder_response(raw_result)
    print(f"DEBUG API: Processed result: {processed_result[:200]}...")
    
    return processed_result

@app.post("/graph/explain")
async def explain_graph(file: UploadFile = File(...)):
    image = await file.read()
    if is_math_problem(image):
        return "This is a math problem"
    
    print("DEBUG API: Calling get_explanation_graph...")
    raw_result = get_explanation_graph(image)
    print(f"DEBUG API: Raw result: {raw_result[:200]}...")
    
    print("DEBUG API: Calling parse_placeholder_response...")
    processed_result = parse_placeholder_response(raw_result)
    print(f"DEBUG API: Processed result: {processed_result[:200]}...")
    
    return processed_result
