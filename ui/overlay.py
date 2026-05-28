import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QMainWindow, QLabel, QApplication, QWidget, QPushButton
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor

class Overlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Configurar la ventana para que flote, no tenga bordes y se mantenga encima
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.label = QLabel(self)
        self.label.setStyleSheet("background-color: transparent;")
        
        self.setCentralWidget(self.label)
        
        self.resize(640, 480)
        self.label.resize(640, 480)
        
        # Posicionar en la esquina inferior derecha
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 660, screen.height() - 520)
        
        # Variable para poder arrastrar la ventana
        self.drag_position = None

    def update_frame(self, frame):
        # Convertir frame de OpenCV (BGR) a RGB
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Añadir un canal alfa para hacer semitransparente el feed de la cámara
        # Esto le da el efecto holograma en el escritorio usando numpy para mejor rendimiento
        rgba_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2RGBA)
        rgba_image[:, :, 3] = 220  # Opacidad (0-255), 220 es ~85%
        
        h, w, ch = rgba_image.shape
        bytes_per_line = ch * w
        q_img = QImage(rgba_image.data, w, h, bytes_per_line, QImage.Format.Format_RGBA8888)
        
        pixmap = QPixmap.fromImage(q_img)
        self.label.setPixmap(pixmap)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def keyPressEvent(self, event):
        # Cerrar si se presiona la tecla 'Q' o 'Esc'
        if event.key() == Qt.Key.Key_Q or event.key() == Qt.Key.Key_Escape:
            self.close_app()
        super().keyPressEvent(event)

    def close_app(self):
        # We can close the application completely when the button is clicked
        QApplication.quit()
