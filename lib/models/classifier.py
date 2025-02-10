import torch
from torchvision import models, transforms
from PIL import Image
import glob

class Classifier:
    def __init__(self, model_path, classes=["Experto", "Operario", "person"]):
        self.classes = classes  
        self.model = models.mobilenet_v3_small(pretrained=False)
        self.model.classifier[3] = torch.nn.Linear(in_features=1024, out_features=len(classes))
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cuda')))
        self.model.eval()  
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),  # Resize to match input size
            transforms.ToTensor(),  # Convert to tensor
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize
        ])

    def predict(self, image):
        image = self.transform(image).unsqueeze(0)  # Add batch dimension
        with torch.no_grad():
            output = self.model(image)
        class_id = torch.argmax(output, dim=1).item()
        return class_id, self.classes[class_id]
    