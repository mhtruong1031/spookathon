import cv2

class Visualizer:
    def __init__(self):
        self.cap = cv2.VideoCapture(2)
        
    
    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            cv2.imshow('nuts', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

v = Visualizer()
v.run()