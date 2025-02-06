import cv2
import numpy as np
import Play_Sound as ps

# Fonction pour vérifier si un contour est une croix
def is_cross(contour, min_size=50, max_size=500):
    # Obtenir la boîte englobante
    x, y, w, h = cv2.boundingRect(contour)
    
    # Vérifier si la forme est approximativement carrée
    if not (0.8 < w / h < 1.2):  # Vérifie une symétrie approximative
        return False
    
    # Vérifier que la taille est dans les limites spécifiées
    if not (min_size < w < max_size and min_size < h < max_size):
        return False
    
    # Approximer le contour pour simplifier
    epsilon = 0.02 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    
    # Vérifier le nombre de coins (doit être complexe mais simple, typique d'une croix)
    return len(approx) > 7  # Une croix aura plus de points d'intérêt qu'un simple rectangle

def scan_frame_for_crosses(frame):
    # 1. Prétraitement
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convertir en niveaux de gris
    blur = cv2.GaussianBlur(gray, (5, 5), 0)       # Réduire le bruit
    _, binary = cv2.threshold(blur, 190, 255, cv2.THRESH_BINARY)  # Seuillage pour isoler les blancs

    # 2. Trouver les contours
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # Vérifier si le contour est une croix
        if is_cross(contour):
            ps.play_sound(f"/home/jacemhagui/GuideMe/guideme/Audio/Sound Bank/cross.mp3")
            # Dessiner le contour détecté
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 3)

            # Calculer le centre de la croix
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            
