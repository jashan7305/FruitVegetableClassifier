from typing import cast
import sys
from PIL import Image
import cv2

from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, QRectF
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QFileDialog, QGraphicsView, QGraphicsScene,
    QDialog, QMessageBox, QLineEdit    
)

from Prediction import predict_image
import resources

app = QApplication([])

camera_window = cast(QMainWindow, uic.loadUi("ui\\Page\\Display_Screen.ui"))

discard_btn = camera_window.findChild(QPushButton, "discardBtn")
cap_btn = camera_window.findChild(QPushButton, "capBtn")
upload_btn = camera_window.findChild(QPushButton, "uploadBtn")
pred_btn = camera_window.findChild(QPushButton, "predBtn")
file_path_line = camera_window.findChild(QLineEdit, "filePathLineEdit")
camera_view = camera_window.findChild(QGraphicsView, "cameraView")

scene = QGraphicsScene()
camera_view.setScene(scene)

cap = cv2.VideoCapture(0)
timer = QTimer()

def show_frame():
    ret, frame = cap.read()
    if ret:
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

def capture_image():
    stop_camera()
    ret, frame = cap.read()
    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)

        h, w = frame_rgb.shape[:2]
        qt_img = QImage(frame_rgb.data, w, h, 3 * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        scene.clear()
        scene.addPixmap(pixmap)
        scene.setSceneRect(QRectF(pixmap.rect()))
        camera_view.fitInView(scene.sceneRect(), mode=1)

        prediction = predict_image(img)
        print(prediction)

def upload():
    stop_camera()
    file, _ = QFileDialog.getOpenFileName()
    if not file.endswith(('.jpg', '.jpeg', '.png')):
        print("please select an image")
        return
    file_path_line.setText(file)
    img = Image.open(file).convert("RGB")
    pixmap = QPixmap(file)
    scene.clear()
    scene.addPixmap(pixmap)
    scene.setSceneRect(QRectF(pixmap.rect()))
    camera_view.fitInView(scene.sceneRect(), mode=2)

    prediction = predict_image(img)
    print(prediction)

def discard():
    file_path_line.clear()
    scene.clear()
    start_camera()

upload_btn.clicked.connect(upload)
cap_btn.clicked.connect(capture_image)
discard_btn.clicked.connect(discard)

if __name__ == "__main__":
    start_camera()
    camera_window.show()
    exit_code = app.exec_()
    cap.release()
    sys.exit(exit_code)
