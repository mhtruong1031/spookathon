# main.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from services.getExplanation import get_explanation_math, get_explanation_graph, is_math_problem


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


@app.post("/graph/explain")
async def explain_graph(file: UploadFile = File(...)):
    image = await file.read()
    if is_math_problem(image):
        return "This is a math problem"
    return get_explanation_graph(image)