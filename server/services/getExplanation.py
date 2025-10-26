import PIL.Image as Image
import io
import google.generativeai as genai
import dotenv
import os
import json
import re
import sys

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_API_KEY

def parse_placeholder_response(text):
    """Parse AI response with placeholders and JSON LaTeX array"""
    if not text:
        return text
    
    import re
    import json
    
    print(f"DEBUG: Input text: {text[:200]}...")  # Debug: show first 200 chars
    
    # Extract JSON array from the end of the text
    json_match = re.search(r'JSON:\s*(\[.*?\])', text, re.DOTALL)
    if not json_match:
        print("DEBUG: No JSON found, returning original text")
        return text  # Fallback to original text if no JSON found
    
    print(f"DEBUG: Found JSON: {json_match.group(1)}")  # Debug: show found JSON
    
    try:
        # Parse the JSON array
        latex_expressions = json.loads(json_match.group(1))
        print(f"DEBUG: Parsed LaTeX expressions: {latex_expressions}")  # Debug: show parsed array
        
        # Remove the JSON part from the text
        text_without_json = text[:json_match.start()].strip()
        print(f"DEBUG: Text without JSON: {text_without_json[:200]}...")  # Debug: show text without JSON
        
        # Process each LaTeX expression first, then replace placeholders
        processed_expressions = []
        for i, latex_expr in enumerate(latex_expressions, 1):
            # Clean and process the LaTeX expression
            cleaned_latex = latex_expr.strip()
            
            # Fix common LaTeX issues
            cleaned_latex = cleaned_latex.replace('\\\\', '\\')  # Fix double backslashes
            cleaned_latex = cleaned_latex.replace('\\newline', '')  # Remove newlines
            cleaned_latex = cleaned_latex.replace('\\n', '')  # Remove literal \n
            
            # Fix integral limits formatting
            # Pattern: \int number1 number2 -> \int_{number1}^{number2}
            cleaned_latex = re.sub(r'\\int\s+(\d+)\s+(\d+)', r'\\int_{\1}^{\2}', cleaned_latex)
            
            # Fix differential spacing
            cleaned_latex = cleaned_latex.replace(' dy', ' \\, dy')
            cleaned_latex = cleaned_latex.replace(' dx', ' \\, dx')
            cleaned_latex = cleaned_latex.replace(' dz', ' \\, dz')
            
            # Wrap in $ delimiters
            wrapped_latex = f"${cleaned_latex}$"
            processed_expressions.append(wrapped_latex)
            print(f"DEBUG: Processed {i}: {latex_expr} -> {wrapped_latex}")
        
        # Now replace placeholders with processed expressions
        for i, processed_latex in enumerate(processed_expressions, 1):
            placeholder = f"{{{i}}}"
            text_without_json = text_without_json.replace(placeholder, processed_latex)
            print(f"DEBUG: Replaced {placeholder} with {processed_latex}")
        
        print(f"DEBUG: Final result: {text_without_json[:200]}...")  # Debug: show final result
        return text_without_json
        
    except (json.JSONDecodeError, IndexError) as e:
        print(f"DEBUG: JSON parsing error: {e}")  # Debug: show error
        # If JSON parsing fails, return original text
        return text



def get_explanation_graph(imageBytes) -> str:
    image = Image.open(io.BytesIO(imageBytes))
    
    # Configure the API key
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Get the model
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    response = model.generate_content([
        "Give me a detailed explanation of the graph in the image, especially noting the important critical points and where the function changes directions. Focus on explaining the image to educate. IMPORTANT: Format your response as follows: 1) Write the explanation in plain text, but use placeholders like {1}, {2}, {3}, etc. for mathematical expressions. 2) At the end, provide a JSON array of LaTeX expressions corresponding to each placeholder. Example format: 'The critical point is at {1} and the derivative is {2}. JSON: [\"x = 0\", \"\\\\frac{d}{dx}f(x) = 3x^2 - 6x\"]'",
        image
    ])

    return parse_placeholder_response(response.text)


def get_explanation_math(imageBytes) -> str:

    if not is_math_problem(imageBytes):
        return "This is not a math problem"

    image = Image.open(io.BytesIO(imageBytes))
    
    # Configure the API key
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Get the model
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    response = model.generate_content([
        "Give me a detailed explanation of the math problem in the image as well as a detailed explanation of the function behind the problem. IMPORTANT: Format your response as follows: 1) Write the explanation in plain text, but use placeholders like {1}, {2}, {3}, etc. for mathematical expressions. 2) At the end, provide a JSON array of LaTeX expressions corresponding to each placeholder. Example format: 'The derivative is {1} and the integral is {2}. JSON: [\"\\\\frac{d}{dx}f(x)\", \"\\\\int_0^1 x^2 \\\\, dx\"]'",
        image
    ])
    
    return parse_placeholder_response(response.text)


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






