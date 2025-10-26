import PIL.Image as Image
import io
import google.generativeai as genai
import dotenv
import os
import json
import re
dotenv.load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def parse_placeholder_response(text):
    """Parse AI response with placeholders and JSON LaTeX array"""
    if not text:
        return text
    
    import re
    import json
    
    print(f"DEBUG: Input text: {text[:200]}...")  # Debug: show first 200 chars
    
    # Extract JSON array from the end of the text - be more flexible
    json_match = re.search(r'JSON:\s*(\[.*)', text, re.DOTALL)
    if not json_match:
        print("DEBUG: No JSON found, returning original text")
        return text
    
    raw_json = json_match.group(1)
    print(f"DEBUG: Raw JSON: {raw_json[:200]}...")  # Debug: show raw JSON
    
    # Try to fix incomplete JSON
    if not raw_json.endswith(']'):
        # Count quotes to see if we have incomplete strings
        quote_count = raw_json.count('"')
        if quote_count % 2 == 1:  # Odd number means incomplete string
            # Remove the incomplete last string and close the array
            raw_json = raw_json.rstrip('"').rstrip(',').rstrip() + '"]'
        else:
            # Just close the array
            raw_json = raw_json.rstrip(',').rstrip() + '"]'
        print(f"DEBUG: Fixed JSON: {raw_json[:200]}...")
    
    try:
        # Parse the JSON array
        latex_expressions = json.loads(raw_json)
        print(f"DEBUG: Parsed LaTeX expressions: {latex_expressions}")  # Debug: show parsed array
        
        # Remove the JSON part from the text
        text_without_json = text[:json_match.start()].strip()
        print(f"DEBUG: Text without JSON: {text_without_json[:200]}...")  # Debug: show text without JSON
        
        # Process each LaTeX expression first, then replace placeholders
        processed_expressions = []
        for i, latex_expr in enumerate(latex_expressions, 1):
            # Clean and process the LaTeX expression
            cleaned_latex = latex_expr.strip()
            
            # Check if this is actually a LaTeX expression (contains LaTeX commands)
            is_latex = any(cmd in cleaned_latex for cmd in ['\\int', '\\frac', '\\sum', '\\lim', '\\sqrt', '\\left', '\\right', '\\cdot', '\\times', '\\div', '\\pm', '\\mp', '\\leq', '\\geq', '\\neq', '\\approx', '\\equiv', '\\in', '\\notin', '\\subset', '\\supset', '\\cup', '\\cap', '\\emptyset', '\\infty', '\\alpha', '\\beta', '\\gamma', '\\delta', '\\epsilon', '\\theta', '\\lambda', '\\mu', '\\pi', '\\sigma', '\\tau', '\\phi', '\\omega', '\\Gamma', '\\Delta', '\\Theta', '\\Lambda', '\\Pi', '\\Sigma', '\\Phi', '\\Omega'])
            
            # Additional check: exclude common text patterns that shouldn't be LaTeX
            is_text_pattern = any(pattern in cleaned_latex.lower() for pattern in [
                'gives:', 'now,', 'we find', 'the antiderivative', 'with respect to', 
                'lower limit', 'upper limit', 'evaluate this', 'expression from',
                'integrating', 'function', 'polynomial', 'surface', 'region',
                'parabola', 'opening', 'upwards', 'downwards', 'means', 'slices',
                'parallel to', 'passes through', 'origin', 'along the', 'where',
                'this is', 'type of', 'geometric', 'behavior', 'characteristics'
            ])
            
            # If it's a text pattern, don't treat as LaTeX
            if is_text_pattern:
                is_latex = False
            
            # AGGRESSIVE: If the expression is too complex or might cause horizontal lines, treat as text
            problematic_patterns = ['\\over', '\\atop', '\\choose', '\\hline', '\\rule', '\\hrule', '\\vrule', '\\hfill', '\\vfill', '\\hspace', '\\vspace', '\\hskip', '\\vskip']
            if any(pattern in cleaned_latex for pattern in problematic_patterns):
                is_latex = False
                print(f"DEBUG: Expression {i} contains problematic patterns, treating as text: {cleaned_latex}")
            
            if is_latex:
                # Remove all \, spacing that causes horizontal lines
                cleaned_latex = cleaned_latex.replace('\\,', '')  # Remove all thin spaces
                
                # AGGRESSIVE: Remove ALL spacing and line commands that could cause horizontal lines
                cleaned_latex = cleaned_latex.replace('\\:', '')  # Remove medium spaces
                cleaned_latex = cleaned_latex.replace('\\;', '')  # Remove thick spaces
                cleaned_latex = cleaned_latex.replace('\\!', '')  # Remove negative spaces
                cleaned_latex = cleaned_latex.replace('\\quad', ' ')  # Replace quad with space
                cleaned_latex = cleaned_latex.replace('\\qquad', ' ')  # Replace qquad with space
                cleaned_latex = cleaned_latex.replace('\\hline', '')  # Remove horizontal lines
                cleaned_latex = cleaned_latex.replace('\\rule', '')  # Remove rules
                cleaned_latex = cleaned_latex.replace('\\hrule', '')  # Remove horizontal rules
                cleaned_latex = cleaned_latex.replace('\\vrule', '')  # Remove vertical rules
                cleaned_latex = cleaned_latex.replace('\\hfill', '')  # Remove horizontal fill
                cleaned_latex = cleaned_latex.replace('\\vfill', '')  # Remove vertical fill
                cleaned_latex = cleaned_latex.replace('\\hspace', '')  # Remove horizontal space
                cleaned_latex = cleaned_latex.replace('\\vspace', '')  # Remove vertical space
                cleaned_latex = cleaned_latex.replace('\\hskip', '')  # Remove horizontal skip
                cleaned_latex = cleaned_latex.replace('\\vskip', '')  # Remove vertical skip
                
                # Remove any remaining problematic commands
                cleaned_latex = cleaned_latex.replace('\\over', '/')  # Replace \over with simple division
                cleaned_latex = cleaned_latex.replace('\\atop', '/')  # Replace \atop with simple division
                cleaned_latex = cleaned_latex.replace('\\choose', 'C')  # Replace \choose with C
                
                # Fix fractions that might create horizontal lines
                cleaned_latex = cleaned_latex.replace('\\frac', '\\frac')  # Ensure proper fraction syntax
                cleaned_latex = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\\frac{\1}{\2}', cleaned_latex)  # Normalize fraction syntax
                
                # Fix integral limits formatting
                # Pattern: \int number1 number2 -> \int_{number1}^{number2}
                cleaned_latex = re.sub(r'\\int\s+(\d+)\s+(\d+)', r'\\int_{\1}^{\2}', cleaned_latex)
                
                # Fix malformed integrals with missing underscores
                cleaned_latex = re.sub(r'\\int\{(\d+)\}\{(\d+)\}', r'\\int_{\1}^{\2}', cleaned_latex)
                cleaned_latex = cleaned_latex.replace('\\int_', '\\int')  # Fix \int_ to \int
                cleaned_latex = re.sub(r'\\int_\{(\d+)\}\^', r'\\int_{\1}', cleaned_latex)  # Fix \int_{0}^ to \int_{0}
                
                # Fix double spacing in differentials and other elements
                cleaned_latex = cleaned_latex.replace(' \\, \\, ', ' \\, ')  # Fix double spacing
                cleaned_latex = cleaned_latex.replace('  ', ' ')  # Fix double spaces
                cleaned_latex = cleaned_latex.replace('  + ', ' + ')  # Fix double spaces before +
                
                # Fix malformed equals signs that create long lines
                cleaned_latex = cleaned_latex.replace('=', ' = ')  # Add spaces around equals
                cleaned_latex = cleaned_latex.replace(' =  = ', ' = ')  # Fix double spaces around equals
                cleaned_latex = cleaned_latex.replace('  = ', ' = ')  # Fix multiple spaces before equals
                cleaned_latex = cleaned_latex.replace('=  ', '= ')  # Fix multiple spaces after equals
                
                # Fix other symbols that might create lines
                cleaned_latex = cleaned_latex.replace('---', '\\text{---}')  # Fix triple dashes
                cleaned_latex = cleaned_latex.replace('--', '\\text{--}')  # Fix double dashes
                # Don't escape underscores - they're needed for subscripts
                cleaned_latex = cleaned_latex.replace('*', '\\cdot')  # Replace asterisks with proper multiplication
                
                # Remove any standalone dashes or lines that might render as horizontal rules
                cleaned_latex = re.sub(r'^-+$', '', cleaned_latex)  # Remove lines of just dashes
                cleaned_latex = re.sub(r'^=+$', '', cleaned_latex)  # Remove lines of just equals
                cleaned_latex = re.sub(r'^_+$', '', cleaned_latex)  # Remove lines of just underscores
                
                # Fix constants of integration alignment - use proper spacing
                cleaned_latex = cleaned_latex.replace('+ C', ' + C')  # Simple space before C
                cleaned_latex = cleaned_latex.replace('+ C_1', ' + C_1')  # Simple space before C_1
                cleaned_latex = cleaned_latex.replace('+ C_2', ' + C_2')  # Simple space before C_2
                cleaned_latex = cleaned_latex.replace('+ C_3', ' + C_3')  # Simple space before C_3
                
                # Fix constants of integration that might be malformed
                cleaned_latex = cleaned_latex.replace('C', 'C')  # Ensure C is just C
                cleaned_latex = cleaned_latex.replace('C_1', 'C_1')  # Ensure C_1 is just C_1
                cleaned_latex = cleaned_latex.replace('C_2', 'C_2')  # Ensure C_2 is just C_2
                cleaned_latex = cleaned_latex.replace('C_3', 'C_3')  # Ensure C_3 is just C_3
                
                # Remove any problematic spacing around constants
                cleaned_latex = re.sub(r'\\,?\s*\+\s*C(?![_0-9])', ' + C', cleaned_latex)  # Fix + C spacing
                cleaned_latex = re.sub(r'\\,?\s*\+\s*C_1', ' + C_1', cleaned_latex)  # Fix + C_1 spacing
                cleaned_latex = re.sub(r'\\,?\s*\+\s*C_2', ' + C_2', cleaned_latex)  # Fix + C_2 spacing
                cleaned_latex = re.sub(r'\\,?\s*\+\s*C_3', ' + C_3', cleaned_latex)  # Fix + C_3 spacing
                
                # Fix differential spacing - use simple spaces instead of \, 
                cleaned_latex = cleaned_latex.replace(' dy', ' dy')
                cleaned_latex = cleaned_latex.replace(' dx', ' dx')
                cleaned_latex = cleaned_latex.replace(' dz', ' dz')
                
                # Wrap in $ delimiters
                wrapped_latex = f"${cleaned_latex}$"
                processed_expressions.append(wrapped_latex)
                print(f"DEBUG: Processed {i} (LaTeX): {latex_expr} -> {wrapped_latex}")
            else:
                # This is just text, don't wrap in $ delimiters
                processed_expressions.append(cleaned_latex)
                print(f"DEBUG: Processed {i} (text): {latex_expr} -> {cleaned_latex}")
        
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






