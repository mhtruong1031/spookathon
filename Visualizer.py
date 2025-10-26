import cv2
import torch
import os
import base64
from typing import Optional, Tuple, List
import logging

from google import genai
from google.genai import types
from pydantic import BaseModel

from matplotlib import pyplot as plt
import numpy as np

from config import GOOGLE_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Analysis(BaseModel):
    code: str
    x1: float
    x2: float


class Visualizer:
    def __init__(self, camera_id: int = 2, api_key: str = GOOGLE_API_KEY):
        """
        Initialize the Visualizer.
        
        Args:
            camera_id: Camera device ID
            api_key: Google API key for Gemini
        """
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            logger.error(f"Could not open camera {camera_id}")
            raise IOError(f"Could not open camera {camera_id}")
        
        self.client = genai.Client(api_key=api_key)
        self.plot_output_path = "current_plot.png"
    
    def cleanup(self) -> None:
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()

    def get_relevant_equation_from_image(self, image: np.ndarray) -> Optional[Analysis]:
        try:
            original_height, original_width = image.shape[:2]
            
            # Resize image for API (reduce to 50% but maintain min size)
            new_width = max(int(original_width * 0.5), 200)
            new_height = max(int(original_height * 0.5), 200)
            
            resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            _, buffer = cv2.imencode('.jpg', resized_image, [cv2.IMWRITE_JPEG_QUALITY, 85])
            image_bytes = base64.b64encode(buffer.tobytes()).decode('utf-8')
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    "Analyze the image for a certain math concept and return the relevant python code to plot an example equation in matplotlib, where plt is already imported, and the range of x values is the domain where relevant part of the function is visible. Make sure to save as specified",
                    "Examples of valid equation code:",
                    """import numpy as np
import matplotlib.pyplot as plt

# Define the function
def f(x):
    return np.sin(x**2) + x/2

# Data
x = np.linspace(-10, 10, 400)
y = f(x)

# Plot
plt.figure(figsize=(8,5))
plt.plot(x, y, color='royalblue', linewidth=2)
plt.title("y = sin(x²) + x/2")
plt.xlabel("x")
plt.ylabel("y")
plt.grid(True, alpha=0.4)
plt.savefig("current_plot.png", transparent=True, bbox_inches='tight', pad_inches=0)
""",
                    """import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define the function
def f(x, y):
    return np.sin(np.sqrt(x**2 + y**2))

# Data
x = np.linspace(-6, 6, 200)
y = np.linspace(-6, 6, 200)
X, Y = np.meshgrid(x, y)
Z = f(X, Y)

# Plot
fig = plt.figure(figsize=(8,6))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none')
ax.set_title("z = sin(√(x² + y²))")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
plt.savefig("current_plot.png", transparent=True, bbox_inches='tight', pad_inches=0)
""",
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type='image/jpeg',
                    )
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": Analysis
                }
            )

            return response.parsed
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}", exc_info=True)
            return None

    def plot_function(self, equation: str, x1: float, x2: float) -> None:
        """
        Execute plotting code and save the result.
        
        Args:
            equation: Python code string to execute
            x1: Lower bound of x range
            x2: Upper bound of x range
        """
        try:
            # Validate inputs
            if x1 >= x2:
                logger.warning(f"Invalid x range: {x1} >= {x2}")
                return
            
            if not equation or not equation.strip():
                logger.warning("Empty equation code")
                return
            
            # Execute the plotting code
            # Note: Using exec is potentially dangerous in production
            # but necessary here as we're generating arbitrary plotting code
            safe_globals = {
                'np': np,
                'plt': plt,
                'numpy': np,
                'matplotlib': None,  # Don't import full module
            }
            
            exec(equation, safe_globals)
            plt.savefig("current_plot.png")
            
            logger.debug(f"Successfully plotted function over range [{x1}, {x2}]")
            
        except SyntaxError as e:
            logger.error(f"Syntax error in equation code: {e}")
        except Exception as e:
            logger.error(f"Error executing plot code: {e}", exc_info=True)
        finally:
            # Always close any open figures
            plt.close('all')