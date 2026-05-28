import pyautogui
import numpy as np

class OSController:
    def __init__(self):
        # Desactivar el failsafe de PyAutoGUI para evitar excepciones si el cursor va a la esquina
        pyautogui.FAILSAFE = False
        # Para que los movimientos sean más fluidos
        pyautogui.PAUSE = 0
        
        self.screen_w, self.screen_h = pyautogui.size()
        self.is_dragging = False
        
        # Suavizado para evitar tirones (Exponential Moving Average)
        self.smooth_x = 0
        self.smooth_y = 0
        self.smoothing_factor = 0.6  # 0.6 es rápido pero filtra el temblor natural de la mano
        
        # Sensibilidad: Reducido a 100 para que no sea tan sensible
        self.margin = 100

    def move_cursor(self, x, y, frame_w, frame_h):
        """
        Mueve el cursor basado en coordenadas relativas al tamaño del frame de la cámara.
        """
        # Mapeamos usando el margen para aumentar la sensibilidad
        # Invertimos el eje X para que funcione como espejo (más intuitivo)
        # Nota: Como ya volteamos el frame con cv2.flip en main.py, aquí solo usamos 'x' directo
        target_x = np.interp(x, (self.margin, frame_w - self.margin), (0, self.screen_w))
        target_y = np.interp(y, (self.margin, frame_h - self.margin), (0, self.screen_h))
        
        if self.smooth_x == 0 and self.smooth_y == 0:
            self.smooth_x, self.smooth_y = target_x, target_y
            
        self.smooth_x += (target_x - self.smooth_x) * self.smoothing_factor
        self.smooth_y += (target_y - self.smooth_y) * self.smoothing_factor
        
        try:
            pyautogui.moveTo(int(self.smooth_x), int(self.smooth_y))
        except Exception as e:
            pass

    def click(self):
        if not self.is_dragging:
            pyautogui.click()

    def start_drag(self):
        if not self.is_dragging:
            pyautogui.mouseDown()
            self.is_dragging = True

    def stop_drag(self):
        if self.is_dragging:
            pyautogui.mouseUp()
            self.is_dragging = False

    def scroll(self, amount):
        pyautogui.scroll(amount)
