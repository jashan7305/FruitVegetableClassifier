from typing import cast
import sys
import os
from PIL import Image
import cv2

from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, QRectF
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QGraphicsView, QGraphicsScene,
    QDialog, QLineEdit, QComboBox, QLabel    
)

from Prediction import predict_image
import resources

app = QApplication([])

camera_window = cast(QMainWindow, uic.loadUi(os.path.join("ui", "Page", "Display_Screen.ui")))
validation_dialog = cast(QDialog, uic.loadUi(os.path.join("ui", "Page", "Validate.ui")))

discard_btn = camera_window.findChild(QPushButton, "discardBtn")
cap_btn = camera_window.findChild(QPushButton, "capBtn")
upload_btn = camera_window.findChild(QPushButton, "uploadBtn")
file_path_line = camera_window.findChild(QLineEdit, "filePathLineEdit")
camera_view = camera_window.findChild(QGraphicsView, "cameraView")
combo_box = validation_dialog.findChild(QComboBox, "comboBox")
prediction_label = validation_dialog.findChild(QLabel, "predLabel")
other_option = validation_dialog.findChild(QLineEdit, "otherOption")
yes_btn = validation_dialog.findChild(QPushButton, "yesBtn")
no_btn = validation_dialog.findChild(QPushButton, "noBtn")
save_btn = validation_dialog.findChild(QPushButton, "saveBtn")

scene = QGraphicsScene()
camera_view.setScene(scene)

train_dir = os.path.join("data", "train")
labels = [label for label in os.listdir(train_dir)]
labels.append("other")
cap = cv2.VideoCapture(0)
timer = QTimer()
correct_label = None
current_image = None

combo_box.addItems(labels)

def show_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qt_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        scene.clear()
        scene.addPixmap(pixmap)
        scene.setSceneRect(QRectF(pixmap.rect()))
        camera_view.fitInView(scene.sceneRect(), mode=1)

def start_camera():
    if not timer.isActive():
        timer.timeout.connect(show_frame)
        timer.start(30)

def stop_camera():
    if timer.isActive():
        timer.stop()
        timer.timeout.disconnect(show_frame)

def show_prediction(prediction):
    validation_dialog.show()
    combo_box.hide()
    other_option.hide()
    save_btn.hide()
    prediction_label.setText(f"Prediction: {prediction}\n\nIs this correct?")

def correct_prediction():
    validation_dialog.hide()
    discard()

def incorrect_prediction():
    prediction_label.setText("\nPlease select the correct label")
    combo_box.show()
    no_btn.setText("Confirm")
    no_btn.setStyleSheet("background-color: blue; color: white")
    yes_btn.setText("Discard")
    yes_btn.setStyleSheet("background-color: red; color: white")
    try:
        no_btn.clicked.disconnect()
    except TypeError:
        pass
    no_btn.clicked.connect(confirm_selection)

def confirm_selection():
    global correct_label, current_image
    correct_label = combo_box.currentText()
    print(correct_label)
    if correct_label:
        if correct_label == "other":
            other_option.show()
            save_btn.show()
            save_btn.clicked.connect(save_other_label)
        else:
            label_dir = os.path.join(train_dir, correct_label)
            if not os.path.exists(label_dir):
                os.makedirs(label_dir)
            current_image.save(os.path.join(label_dir, f"{len(os.listdir(label_dir))+1}.jpg"))
            print(f"image saved as {os.path.join(label_dir, f'{len(os.listdir(label_dir))}.jpg')}")
            discard()

def save_other_label():
    global correct_label, current_image
    correct_label = other_option.text()
    if correct_label:
        label_dir = os.path.join(train_dir, correct_label)
        if not os.path.exists(label_dir):
            os.makedirs(label_dir)
        current_image.save(os.path.join(label_dir, f"{len(os.listdir(label_dir))+1}.jpg"))
        print(f"image saved as {os.path.join(label_dir, f'{len(os.listdir(label_dir))}.jpg')}")
    discard()
        
def capture_image():
    stop_camera()
    ret, frame = cap.read()
    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        global current_image
        current_image = img

        h, w = frame_rgb.shape[:2]
        qt_img = QImage(frame_rgb.data, w, h, 3 * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        scene.clear()
        scene.addPixmap(pixmap)
        scene.setSceneRect(QRectF(pixmap.rect()))
        camera_view.fitInView(scene.sceneRect(), mode=1)

        prediction = predict_image(img)
        show_prediction(prediction)
        
def upload():
    stop_camera()
    file, _ = QFileDialog.getOpenFileName(camera_window, "Select Image", "", "Images (*.jpg *.jpeg *.png *.jfif)")
    if not file:
        return
    file_path_line.setText(file)
    img = Image.open(file).convert("RGB")
    global current_image
    current_image = img
    pixmap = QPixmap(file)
    scene.clear()
    scene.addPixmap(pixmap)
    scene.setSceneRect(QRectF(pixmap.rect()))
    camera_view.fitInView(scene.sceneRect(), mode=2)

    prediction = predict_image(img)
    print(prediction)
    show_prediction(prediction)

def discard():
    yes_btn.setText("Yes")
    yes_btn.setStyleSheet("background-color: green; color: white")
    no_btn.setText("No")
    no_btn.setStyleSheet("background-color: red; color: white")
    other_option.clear()
    other_option.hide()
    save_btn.hide()
    try:
        yes_btn.clicked.disconnect()
    except TypeError:
        pass
    yes_btn.clicked.connect(correct_prediction)

    try:
        no_btn.clicked.disconnect()
    except TypeError:
        pass
    no_btn.clicked.connect(incorrect_prediction)
    validation_dialog.hide()
    file_path_line.clear()
    scene.clear()
    global correct_label, current_image
    correct_label = None
    current_image = None
    start_camera()

upload_btn.clicked.connect(upload)
cap_btn.clicked.connect(capture_image)
discard_btn.clicked.connect(discard)
yes_btn.clicked.connect(correct_prediction)
no_btn.clicked.connect(incorrect_prediction)

if __name__ == "__main__":
    start_camera()
    camera_window.show()
    exit_code = app.exec_()
    cap.release()
    sys.exit(exit_code)
