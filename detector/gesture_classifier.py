import math
import numpy as np

class GestureClassifier:
    def __init__(self):
        # Umbral para iniciar el pinch (clic)
        self.pinch_start_threshold = 25
        # Umbral para soltar el pinch (drag). Al ser mayor, evita que sueltes archivos por accidente si la cámara falla un poco
        self.pinch_stop_threshold = 50
        # Umbral a partir del cual el cursor empieza a hacer transición suave hacia el punto medio
        self.pre_pinch_threshold = 80
        self.is_pinching = False
        self.frozen_offset = None

    def classify(self, lm_list):
        if not lm_list:
            return "NONE", None, 0, 0

        # Para este prototipo, analizamos la primera mano detectada
        hand = lm_list[0]
        
        # Puntas de los dedos
        thumb_tip = hand[4][1:]
        index_tip = hand[8][1:]
        middle_tip = hand[12][1:]
        ring_tip = hand[16][1:]
        pinky_tip = hand[20][1:]

        # Articulaciones (PIP) para determinar si el dedo está doblado o extendido
        index_pip = hand[6][1:]
        middle_pip = hand[10][1:]
        ring_pip = hand[14][1:]
        pinky_pip = hand[18][1:]
        # Estrategia híbrida:
        # 1. Si NO estamos haciendo pinch, usamos la distancia 3D real estricta.
        #    Como los dedos están separados, la cámara no tiene oclusión y el eje Z evita cruces falsos.
        if not self.is_pinching:
            pinch_dist = math.dist(thumb_tip, index_tip)
            threshold = self.pinch_start_threshold
        # 2. Si YA estamos haciendo pinch (arrastrando), usamos solo la distancia 2D (X, Y) y un umbral mayor.
        #    Al tocarse los dedos, la cámara se confunde con la Z (oclusión), así que la ignoramos para no soltar.
        else:
            pinch_dist = math.hypot(thumb_tip[0] - index_tip[0], thumb_tip[1] - index_tip[1])
            threshold = self.pinch_stop_threshold

        # Solución de "Anclaje" (Anchor Lock) para el deslizamiento anatómico.
        # En lugar de promediar, congelamos la distancia entre el nudillo (que no se mueve al hacer clic)
        # y la punta del dedo en el momento en que empiezas a juntar los dedos.
        dist_2d = math.hypot(thumb_tip[0] - index_tip[0], thumb_tip[1] - index_tip[1])
        index_mcp = hand[5][1:]  # Nudillo base del índice
        
        if dist_2d >= self.pre_pinch_threshold:
            # Manos separadas: rastreo directo
            self.frozen_offset = None
            cursor_x = int(index_tip[0])
            cursor_y = int(index_tip[1])
        else:
            # Preparando el clic: Congelamos el vector (distancia) entre el nudillo y la punta del dedo.
            if self.frozen_offset is None:
                self.frozen_offset = (index_tip[0] - index_mcp[0], index_tip[1] - index_mcp[1])
            
            # El cursor ahora sigue al nudillo + la distancia congelada.
            # ¡Esto anula por completo el movimiento hacia abajo del dedo al encorvarse!
            cursor_x = int(index_mcp[0] + self.frozen_offset[0])
            cursor_y = int(index_mcp[1] + self.frozen_offset[1])

        # Evaluar estado de pinch
        if pinch_dist < threshold:
            self.is_pinching = True
            return "PINCH", pinch_dist, cursor_x, cursor_y
        
        self.is_pinching = False
        
        # Palma abierta y Puño cerrado necesitan ser calculados si no hay pinch
        open_palm = (
            index_tip[1] < index_pip[1] and
            middle_tip[1] < middle_pip[1] and
            ring_tip[1] < ring_pip[1] and
            pinky_tip[1] < pinky_pip[1]
        )
        
        closed_fist = (
            index_tip[1] > index_pip[1] and
            middle_tip[1] > middle_pip[1] and
            ring_tip[1] > ring_pip[1] and
            pinky_tip[1] > pinky_pip[1]
        )

        if closed_fist:
            return "FIST", None, cursor_x, cursor_y
        elif open_palm:
            return "OPEN_PALM", None, cursor_x, cursor_y
        
        return "NONE", None, cursor_x, cursor_y
