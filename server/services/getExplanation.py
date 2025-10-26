import PIL.Image as Image
import io
import google.generativeai as genai
import dotenv
import os
dotenv.load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")



def get_explanation_graph(imageBytes) -> str:
    image = Image.open(io.BytesIO(imageBytes))
    
    # Configure the API key
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Get the model
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    response = model.generate_content([
        "Give me a detailed explanation of the graph in the image, especially noting the important critical points and where the function changes directions, noting to explaining the image to educate, note the math problem but it is only relevant to explaining the graph",
        image
    ])

    return response.text


def get_explanation_math(imageBytes) -> str:

    if not is_math_problem(imageBytes):
        return "This is not a math problem"

    image = Image.open(io.BytesIO(imageBytes))
    
    # Configure the API key
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Get the model
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    response = model.generate_content([
        "Give me a detailed explanation of the math problem in the image as well as a detailed explanation of the function behind the problem",
        image
    ])
    
    return response.text


def is_math_problem(imageBytes) -> bool:
    # Configure the API key
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Get the model
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Open and prepare the image
    image = Image.open(io.BytesIO(imageBytes))
    
    # Generate content
    response = model.generate_content([
        "Is this a math problem? Do not return anything other than 'True' or 'False'.",
        image
    ])
    
    return response.text.strip() == "True"






