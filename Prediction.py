import os
import json
import numpy as np
# from PIL import Image

model_name = "FruitClassification.h5" # change this to change model

with open(os.path.join("data", "index_to_label.json"), "r") as f:
    index_to_label = json.load(f)

if model_name == "FruitClassification.h5":

    from keras.models import load_model
    from keras.applications.mobilenet_v2 import preprocess_input
    from keras.preprocessing.image import img_to_array

    model = load_model(os.path.join("models", model_name))
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    def predict_image(img):
        print(f"using {model_name}")
        img = img.resize((224, 224))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        prediction = model.predict(img_array)
        class_index = np.argmax(prediction, axis=1)[0]
        label = index_to_label[str(class_index)]
        return label
    
else:

    from torchvision import transforms
    from torchvision.models import resnet50
    import torch.nn as nn
    from torch import load, no_grad, argmax, device, max

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    device = device("cpu")

    model = resnet50(pretrained=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(num_ftrs, 256),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(256, 128),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(128, 36)
    )
    model.to(device)
    model.load_state_dict(load(os.path.join("models", model_name), map_location=device))

    def predict_image(img):
        print(f"using {model_name}")
        img = img.convert("RGB")
        img = transform(img).unsqueeze(0).to(device)
        with no_grad():
            outputs = model(img)
            print(outputs)
            preds = argmax(outputs, dim=1)
            probs = nn.functional.softmax(outputs, dim=1)
            confidence, preds = max(probs, 1)
            print(f"Confidence: {confidence.item():.2f}")
            return index_to_label[str(preds.item())]

# trial_img = Image.open("train\\test\\apple\\Image_1.jpg")
# predict_image(trial_img)
