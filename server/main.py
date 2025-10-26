# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from services.getExplanation import get_explanation_math, get_explanation_graph, is_math_problem, parse_placeholder_response
import cv2
import numpy as np
import os
import tempfile
import google.generativeai as genai

from Visualizer import Visualizer
from config import GOOGLE_API_KEY

# Configure the API key
genai.configure(api_key=GOOGLE_API_KEY)

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
    
    print("DEBUG Server: Calling get_explanation_math...")
    raw_result = get_explanation_math(image)
    print(f"DEBUG Server: Raw result: {raw_result[:200]}...")
    
    print("DEBUG Server: Calling parse_placeholder_response...")
    processed_result = parse_placeholder_response(raw_result)
    print(f"DEBUG Server: Processed result: {processed_result[:200]}...")
    
    return processed_result


@app.post("/graph/explain")
async def explain_graph(file: UploadFile = File(...)):
    image = await file.read()
    if is_math_problem(image):
        return "This is a math problem"
    
    print("DEBUG Server: Calling get_explanation_graph...")
    raw_result = get_explanation_graph(image)
    print(f"DEBUG Server: Raw result: {raw_result[:200]}...")
    
    print("DEBUG Server: Calling parse_placeholder_response...")
    processed_result = parse_placeholder_response(raw_result)
    print(f"DEBUG Server: Processed result: {processed_result[:200]}...")
    
    return processed_result


@app.post("/graph/generate")
async def generate_graph(file: UploadFile = File(...)):
    """
    Generate a graph visualization from an uploaded image using Visualizer.py
    """
    try:
        print("DEBUG: Received request to /graph/generate")
        # Read the uploaded image
        image_bytes = await file.read()
        print(f"DEBUG: Image bytes length: {len(image_bytes)}")
        
        # Convert bytes to numpy array for OpenCV
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        print(f"DEBUG: Image decoded successfully: {image is not None}")
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Initialize Visualizer
        print("DEBUG: Initializing Visualizer...")
        visualizer = Visualizer()
        print("DEBUG: Visualizer initialized successfully")
        
        # Analyze the image to get equation and parameters
        print("DEBUG: Analyzing image...")
        analysis = visualizer.get_relevant_equation_from_image(image)
        print(f"DEBUG: Analysis result: {analysis}")
        
        if analysis is None:
            raise HTTPException(status_code=400, detail="Could not analyze the image to extract mathematical content")
        
        # Generate the plot using the extracted equation
        try:
            print("DEBUG: Generating plot...")
            visualizer.plot_function(analysis.code, analysis.x1, analysis.x2)
            print("DEBUG: Plot generated successfully")
        except Exception as e:
            print(f"DEBUG: Error in plot_function: {e}")
            raise HTTPException(status_code=500, detail=f"Error executing plot code: {str(e)}")
        
        # Check if the plot was generated successfully
        if not os.path.exists("current_plot.png"):
            raise HTTPException(status_code=500, detail="Failed to generate plot - no output file created")
        
        # Return the generated plot as a file response
        print("DEBUG: Returning file response")
        return FileResponse(
            path="current_plot.png",
            media_type="image/png",
            filename="generated_graph.png"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Unexpected error in generate_graph: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating graph: {str(e)}")