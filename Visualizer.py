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
        
        # Frame tracking for bbox updates
        self.frame_count = 0
        self.last_bbox = None
    
    # Main runtime function
    def run(self) -> None:
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Failed to read frame")
                    break

                # Update bbox every 5 frames
                if self.frame_count % 20 == 0:
                    bbox = self.get_paper_bbox(frame)
                    if bbox is not None:
                        self.last_bbox = bbox
                else:
                    bbox = self.last_bbox
                
                self.frame_count += 1
                
                # Draw bbox if available
                print(bbox)
                if bbox is not None:
                    # Convert corners to int32 and reshape for polylines
                    pts = bbox.reshape((-1, 1, 2)).astype(np.int32)
                    cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
                
                cv2.imshow('Visualization', frame)
                
                # Exit on 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        
    def process_frame(self, image: np.ndarray) -> None:
        try:
            # First check if there's a paper/document in the frame
            corners = self.get_paper_bbox(image)
            
            # Only proceed with analysis if a document is detected
            if corners is None:
                logger.debug("No document detected in frame - skipping analysis")
                return
            
            logger.debug(f"Found paper corners: {corners.shape}")
            
            # Get relevant equation from image
            analysis = self.get_relevant_equation_from_image(image)
            
            if analysis:
                self.plot_function(analysis.code, analysis.x1, analysis.x2)
                logger.info(f"Plotted function.")
                
                # Overlay the plot onto the original image at the document center
                self.overlay_plot_on_image(image, corners)
            else:
                logger.warning("No equation found in image")
                
        except Exception as e:
            logger.error(f"Error processing frame: {e}", exc_info=True)

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

    
    def get_paper_bbox(self, image):
        pass

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
            
            logger.debug(f"Successfully plotted function over range [{x1}, {x2}]")
            
        except SyntaxError as e:
            logger.error(f"Syntax error in equation code: {e}")
        except Exception as e:
            logger.error(f"Error executing plot code: {e}", exc_info=True)
        finally:
            # Always close any open figures
            plt.close('all')
    
    def overlay_plot_on_image(self, image: np.ndarray, corners: np.ndarray) -> np.ndarray:
        """
        Overlay the plotted function onto the center of the detected document.
        
        Args:
            image: Original image
            corners: Corner points of the detected document
            
        Returns:
            Image with plot overlaid
        """
        try:
            # Load the plot image
            plot_img = cv2.imread(self.plot_output_path, cv2.IMREAD_UNCHANGED)
            if plot_img is None:
                logger.warning("Could not load plot image")
                return image
            
            # Calculate the center of the document from corners
            center_x = int(np.mean(corners[:, 0]))
            center_y = int(np.mean(corners[:, 1]))
            
            # Calculate bounding box dimensions from corners
            min_x, max_x = int(np.min(corners[:, 0])), int(np.max(corners[:, 0]))
            min_y, max_y = int(np.min(corners[:, 1])), int(np.max(corners[:, 1]))
            bbox_width = max_x - min_x
            bbox_height = max_y - min_y
            
            # Resize plot to fit within a reasonable portion of the document (e.g., 60% of bbox)
            max_plot_width = int(bbox_width * 0.6)
            max_plot_height = int(bbox_height * 0.6)
            
            plot_height, plot_width = plot_img.shape[:2]
            aspect_ratio = plot_width / plot_height
            
            if max_plot_width / aspect_ratio > max_plot_height:
                # Constrain by height
                new_height = max_plot_height
                new_width = int(new_height * aspect_ratio)
            else:
                # Constrain by width
                new_width = max_plot_width
                new_height = int(new_width / aspect_ratio)
            
            # Resize plot
            resized_plot = cv2.resize(plot_img, (new_width, new_height))
            
            # Calculate position to center the plot
            x_start = center_x - new_width // 2
            y_start = center_y - new_height // 2
            x_end = x_start + new_width
            y_end = y_start + new_height
            
            # Make sure coordinates are within image bounds
            x_start = max(0, min(x_start, image.shape[1] - new_width))
            y_start = max(0, min(y_start, image.shape[0] - new_height))
            x_end = x_start + new_width
            y_end = y_start + new_height
            
            # Handle transparency if plot has alpha channel
            if resized_plot.shape[2] == 4:
                # Extract alpha channel and convert to 3 channels
                overlay = resized_plot[:, :, :3]
                alpha = resized_plot[:, :, 3] / 255.0
                
                # Blend with original image
                for c in range(3):
                    image[y_start:y_end, x_start:x_end, c] = (
                        alpha * overlay[:, :, c] + (1 - alpha) * image[y_start:y_end, x_start:x_end, c]
                    )
            else:
                # No transparency, just overlay
                image[y_start:y_end, x_start:x_end] = resized_plot
            
            logger.debug(f"Overlaid plot at center ({center_x}, {center_y})")
            return image
            
        except Exception as e:
            logger.error(f"Error overlaying plot: {e}", exc_info=True)
            return image


# Main execution - remove this in production
v = Visualizer()
v.run()