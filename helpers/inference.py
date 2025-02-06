import torch
from torchvision import models, transforms
from PIL import Image
import glob
# Load the trained model
model = models.mobilenet_v3_small(pretrained=False)  # Use 'small' if needed
print("Loading model...")
model.classifier[3] = torch.nn.Linear(in_features=1024, out_features=3)
model.load_state_dict(torch.load("raizen_classifier.pth", map_location=torch.device('cuda')))
model.eval()  
print("Model loaded.")

# Define the transformation
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize to match input size
    transforms.ToTensor(),  # Convert to tensor
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize
])

imgs = glob.glob("../cropped/images/val/*")
imgs = imgs[:10]
# Load and preprocess the image
CLASSES = {
    0: "experto",
    1: "operarion",
    2: "person"
}

for i in imgs:
    print(f"Processing image: {i} ...", end=" ")
    image_path = i
    image = Image.open(image_path).convert("RGB")  # Ensure it's RGB
    image = transform(image).unsqueeze(0)  # Add batch dimension
    class_name= image_path.split("/")[-2]
    
    with torch.no_grad():
        output = model(image)

    # Get predicted class
    predicted_class = torch.argmax(output, dim=1).item()
    print(f"Predicted Class: {CLASSES[predicted_class]}")