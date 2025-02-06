import cv2
import numpy as np
import Play_Sound as ps

def scan_frame_for_squares(frame):

    # 1. Prétraitement
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convertir en niveaux de gris
    blur = cv2.GaussianBlur(gray, (5, 5), 0)       # Réduire le bruit
    _, binary = cv2.threshold(blur, 180, 255, cv2.THRESH_BINARY)  # Seuillage

    # 2. Détection des contours
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # Approximation de contour pour simplifier
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Vérifier si c'est un quadrilatère (4 côtés)
        if len(approx) == 4:
            # Calculer l'aire pour ignorer les petits objets
            area = cv2.contourArea(contour)
            if area > 500:  # Ajuster ce seuil selon la taille du carré
                # Vérifier la forme : rapport longueur/largeur ≈ 1 (carré)
                x, y, w, h = cv2.boundingRect(approx)
                if 0.9 < w / h < 1.1:
                    # Vérifier les couleurs : noir intérieur et blanc extérieur
                    mask = np.zeros_like(gray)
                    cv2.drawContours(mask, [contour], -1, 255, -1)
                    mean_val = cv2.mean(gray, mask=mask)
                    
                    # Vérifier que l'intérieur est plus sombre que l'extérieur
                    if mean_val[0] < 150:  # Valeur arbitraire pour le noir
                        ps.play_sound(f"/home/jacemhagui/GuideMe/guideme/Audio/Sound Bank/square.mp3")
                        # Dessiner le carré détecté
                        cv2.drawContours(frame, [approx], -1, (0, 255, 0), 3)
