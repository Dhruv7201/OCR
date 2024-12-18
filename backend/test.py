from ultralytics import YOLO
import torch

# Assuming YOLOv8 class loads weights from 'BNo.pt'
model = YOLO("model/BNo.pt")
model.eval()

# Example inference
img = torch.zeros((1, 3, 640, 640))  # Create a batch of images
output = model(img)  # Perform inference
