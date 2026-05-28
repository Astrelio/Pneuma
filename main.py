import sys
import cv2
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from detector.hand_tracker import HandTracker
from detector.gesture_classifier import GestureClassifier
from controller.os_controller import OSController
from ui.hud import HUD
from ui.overlay import Overlay

def main():
    app = QApplication(sys.argv)
    
    # Inicializar componentes
    tracker = HandTracker()
    classifier = GestureClassifier()
    os_ctrl = OSController()
    hud = HUD()
    overlay = Overlay()
    
    # Iniciar cámara (0 suele ser la cámara web predeterminada)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        sys.exit(1)
        
    # Ajustar resolución
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Mostrar la ventana de la interfaz "Iron Man"
    overlay.show()
    
    def update():
        success, frame = cap.read()
        if not success:
            return
            
        # Voltear el frame para crear un efecto espejo más natural
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        # Procesar con MediaPipe
        results = tracker.process_frame(frame)
        lm_list = tracker.get_landmarks(frame, results)
        
        gesture = "NONE"
        dist = None
        target_x, target_y = 0, 0
        
        if lm_list:
            hand_landmarks = lm_list[0]
            
            # Clasificar gesto y obtener centro de acción
            gesture, dist, target_x, target_y = classifier.classify(lm_list)
            
            # Lógica de acciones del Sistema Operativo
            if gesture == "PINCH":
                os_ctrl.start_drag()
                os_ctrl.move_cursor(target_x, target_y, w, h)
            elif gesture == "OPEN_PALM":
                os_ctrl.stop_drag()
                # Palma abierta mueve el cursor sin hacer click
                os_ctrl.move_cursor(target_x, target_y, w, h)
            elif gesture == "FIST":
                # Puño cerrado detiene el drag pero no mueve el cursor
                os_ctrl.stop_drag()
            else:
                # Gesto neutro (mano visible pero ni palma, ni puño, ni pinch)
                os_ctrl.stop_drag()
                os_ctrl.move_cursor(target_x, target_y, w, h)
                
        # Dibujar UI
        # Dibujamos el área de detección con el mismo margen de 100 que definimos en os_controller.py
        hud.draw_active_area(frame, margin=100)
        hud.draw_info(frame, gesture, dist)
        
        # Actualizar overlay de PyQt6
        overlay.update_frame(frame)
        
    # QTimer permite ejecutar el bucle de cámara sin bloquear la UI de PyQt
    timer = QTimer()
    timer.timeout.connect(update)
    timer.start(30) # ~33fps
    
    # Arrancar la app
    exit_code = app.exec()
    
    # Limpieza
    cap.release()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
