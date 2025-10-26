from Visualizer import Visualizer
import cv2, requests

# visualizer = Visualizer()

# image = cv2.imread("test_image.jpg")
# res = visualizer.get_relevant_equation_from_image(image)

# visualizer.plot_function(res.code, res.x1, res.x2)

response = requests.post("http://localhost:8000/graph/generate", files={"file": open("test_image.jpg", "rb")})

print(response)