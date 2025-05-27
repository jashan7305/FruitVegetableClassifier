from typing import cast
import sys
from PIL import Image
import matplotlib.pyplot as plt
import threading

from torchvision import transforms

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QFileDialog, 
)

image_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

app = QApplication([])

camera_window = cast(QMainWindow, uic.loadUi("ui\\camera.ui"))

upload_btn = camera_window.findChild(QPushButton, "uploadBtn")

def upload():
    file, _ = QFileDialog.getOpenFileName()
    if not file.endswith(('.jpg', '.jpeg', '.png')):
        print("Please select an image")
        return
    print(file)
    img = Image.open(file).convert("RGB")
    img.show()
    img = image_transforms(img)
    plt.imshow(img.permute(1, 2, 0).numpy())
    return img

upload_btn.clicked.connect(upload)

if __name__ == "__main__":
    camera_window.show()
    sys.exit(app.exec_())

