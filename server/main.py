# main.py
from fastapi import FastAPI
from services.getExplanation import get_explanation_math, get_explanation_graph, is_math_problem
app = FastAPI()

@app.get("/math/explain")
async def explain_math(image: bytes):
    if not is_math_problem(image):
        return "This is not a math problem"
    return get_explanation_math(image)


@app.get("/graph/explain")
async def explain_graph(image: bytes):
    if is_math_problem(image):
        return "This is a math problem"
    return get_explanation_graph(image)