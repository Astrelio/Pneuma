import cv2
import numpy as np


class HUD:
    def __init__(self):
        # Paleta minimalista — blanco roto sobre oscuro
        self.white       = (255, 255, 255)
        self.white_dim   = (180, 180, 180)
        self.accent      = (200, 220, 255)   # blanco azulado suave
        self.active      = (120, 200, 255)   # azul claro para estado activo
        self.danger      = (80,  80,  220)   # rojo suave (pinch activo)
        self.glass_bg    = (30,  30,  30)    # fondo del panel glass

    # ─────────────────────────────────────────────
    # UTILIDADES
    # ─────────────────────────────────────────────

    def _glass_panel(self, frame, x1, y1, x2, y2, alpha=0.35):
        """Simula liquid glass: blur + overlay semitransparente."""
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            return
        # Blur del fondo (efecto frosted glass)
        blurred = cv2.GaussianBlur(roi, (21, 21), 0)
        # Overlay oscuro semitransparente
        overlay = blurred.copy()
        overlay[:] = self.glass_bg
        blended = cv2.addWeighted(blurred, 1 - alpha, overlay, alpha, 0)
        frame[y1:y2, x1:x2] = blended
        # Borde sutil
        cv2.rectangle(frame, (x1, y1), (x2, y2), (*self.white_dim, 60), 1)

    def _text(self, frame, text, x, y, scale=0.45, color=None, thickness=1):
        color = color or self.white_dim
        cv2.putText(frame, text, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness,
                    cv2.LINE_AA)

    def _dot(self, frame, cx, cy, r=3, color=None, filled=True):
        color = color or self.accent
        cv2.circle(frame, (cx, cy), r, color,
                   cv2.FILLED if filled else 1, cv2.LINE_AA)

    # ─────────────────────────────────────────────
    # SKELETON — solo conexiones esenciales
    # ─────────────────────────────────────────────

    def draw_skeleton(self, frame, hand_landmarks):
        """Líneas finas entre nudillos y puntas, puntos en las puntas."""
        # Conexiones: par (origen, destino) por dedo
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),      # pulgar
            (0, 5), (5, 6), (6, 7), (7, 8),       # índice
            (0, 9), (9, 10), (10, 11), (11, 12),  # medio
            (0, 13),(13, 14),(14, 15),(15, 16),    # anular
            (0, 17),(17, 18),(18, 19),(19, 20),    # meñique
            (5, 9), (9, 13),(13, 17),              # palma
        ]
        tips = {4, 8, 12, 16, 20}

        lm = {l[0]: (l[1], l[2]) for l in hand_landmarks}

        # Líneas muy finas y semitransparentes
        for a, b in connections:
            if a in lm and b in lm:
                cv2.line(frame, lm[a], lm[b],
                         self.white_dim, 1, cv2.LINE_AA)

        # Puntos en las puntas
        for idx, (cx, cy) in lm.items():
            if idx in tips:
                self._dot(frame, cx, cy, 5, self.accent)
                self._dot(frame, cx, cy, 8, self.accent, filled=False)
            elif idx == 0:
                self._dot(frame, cx, cy, 4, self.white_dim)

    # ─────────────────────────────────────────────
    # CROSSHAIR — minimalista
    # ─────────────────────────────────────────────

    def draw_crosshair(self, frame, x, y, active=False):
        """Cruz minimalista con punto central."""
        color  = self.danger if active else self.accent
        gap    = 6
        length = 14

        # Punto central
        self._dot(frame, x, y, 2, color)

        # Cruz con gap central
        cv2.line(frame, (x - gap - length, y), (x - gap, y), color, 1, cv2.LINE_AA)
        cv2.line(frame, (x + gap, y),           (x + gap + length, y), color, 1, cv2.LINE_AA)
        cv2.line(frame, (x, y - gap - length),  (x, y - gap), color, 1, cv2.LINE_AA)
        cv2.line(frame, (x, y + gap),           (x, y + gap + length), color, 1, cv2.LINE_AA)

        # Círculo exterior si activo
        if active:
            cv2.circle(frame, (x, y), gap + length, color, 1, cv2.LINE_AA)

    # ─────────────────────────────────────────────
    # PANEL DE INFO — glass card en esquina
    # ─────────────────────────────────────────────

    def draw_info(self, frame, gesture, dist):
        h, w = frame.shape[:2]

        # ── Panel glass (esquina superior izquierda) ──
        px, py, pw, ph = 10, 10, 170, 60
        self._glass_panel(frame, px, py, px + pw, py + ph, alpha=0.45)

       

        # Textos
        self._text(frame, "PNEUMA  REACH Astrelio",
                   px + 10, py + 18, 0.35, self.white, 1)
        self._text(frame, f"{gesture}",
                   px + 10, py + 36, 0.45, self.accent, 1)

        if dist is not None:
            self._text(frame, f"d = {dist:.0f} px",
                       px + 10, py + 52, 0.32, self.white_dim)

        # ── Indicador de estado (esquina superior derecha) ──
        sx = w - 90
        self._glass_panel(frame, sx, 10, sx + 80, 36, alpha=0.4)
        dot_color = self.active if gesture != "NONE" else self.white_dim
        self._dot(frame, sx + 12, 23, 4, dot_color)
        label = "ACTIVE" if gesture != "NONE" else "IDLE"
        self._text(frame, label, sx + 22, 27, 0.38, dot_color)

        # ── Esquinas del frame (minimalistas) ──
        self._draw_corners(frame, w, h)

    # ─────────────────────────────────────────────
    # ESQUINAS — trazo corto y fino
    # ─────────────────────────────────────────────

    def _draw_corners(self, frame, w, h):
        L = 18
        m = 8
        c = self.white_dim

        def corner(x, y, dx, dy):
            cv2.line(frame, (x, y), (x + dx * L, y), c, 1, cv2.LINE_AA)
            cv2.line(frame, (x, y), (x, y + dy * L), c, 1, cv2.LINE_AA)

        corner(m,     m,     1,  1)   # TL
        corner(w - m, m,    -1,  1)   # TR
        corner(m,     h - m, 1, -1)   # BL
        corner(w - m, h - m,-1, -1)   # BR

    # ─────────────────────────────────────────────
    # ÁREA ACTIVA — borde punteado suave
    # ─────────────────────────────────────────────

    def draw_active_area(self, frame, margin=90):
        h, w = frame.shape[:2]
        x1, y1 = margin, margin
        x2, y2 = w - margin, h - margin

        # Borde punteado manual
        step = 10
        for x in range(x1, x2, step * 2):
            cv2.line(frame, (x, y1), (min(x + step, x2), y1),
                     self.white_dim, 1, cv2.LINE_AA)
            cv2.line(frame, (x, y2), (min(x + step, x2), y2),
                     self.white_dim, 1, cv2.LINE_AA)
        for y in range(y1, y2, step * 2):
            cv2.line(frame, (x1, y), (x1, min(y + step, y2)),
                     self.white_dim, 1, cv2.LINE_AA)
            cv2.line(frame, (x2, y), (x2, min(y + step, y2)),
                     self.white_dim, 1, cv2.LINE_AA)

        self._text(frame, "DETECTION ZONE",
                   x1 + 6, y1 - 6, 0.32, self.white_dim)