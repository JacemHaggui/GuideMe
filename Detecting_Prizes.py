import cv2 as cv
import numpy as np
import math

def calculate_midpoint(point1, point2): # For getting the center between both feet
    """Calculate the midpoint between two points."""
    midpoint = ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2)
    return midpoint

def calculate_distance(from_point, to_point):
    """Calculate angle in degrees and distance between two points."""
    dx = to_point[0] - from_point[0]
    dy = to_point[1] - from_point[1]
    distance = math.sqrt(dx**2 + dy**2)
    return distance

# Function to detect squares
def detect_hollow_squares(frame):
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    _, binary = cv.threshold(gray, 230
                             , 255, cv.THRESH_BINARY)
    contours, _ = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    centers = []
    for contour in contours:
        if cv.contourArea(contour) < 500:
            continue
        
        epsilon = 0.02 * cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, epsilon, True)
        
        if len(approx) == 4:
            # Check for a square by verifying the angles between edges (optional check)
            for i in range(4):
                pt1, pt2, pt3 = approx[i], approx[(i + 1) % 4], approx[(i + 2) % 4]
                vec1 = np.array(pt2[0]) - np.array(pt1[0])
                vec2 = np.array(pt3[0]) - np.array(pt2[0])
                angle = np.arccos(np.clip(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)), -1.0, 1.0))
                if (np.pi / 2 - 0.35 <= angle <= np.pi / 2 + 0.35):
                    angle_check = True
                else:
                    angle_check = False
            if angle_check:
                # Calculate the centroid of the contour
                M = cv.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    # Check if the centroid is in the hollow region (centroid should be inside a black area)
                    if binary[cy, cx] < 150:  # Centroid is inside the hollow area (black)
                        # Draw the contour if it's hollow
                        centers.append((cx, cy))
                        centers.append((cx, cy))

    return centers
    return centers

def detect_crosses(frame):
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    _, binary = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)

    contours, _ = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    centers = []
    centers = []
    for contour in contours:
        if cv.contourArea(contour) < 500:
            continue
        epsilon = 0.01 * cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, epsilon, True)
        if len(approx) >= 12 and len(approx) <= 17:
            M = cv.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                if binary[cy, cx] > 240:
                    centers.append((cx, cy))
    return centers 

def closest_point(array_of_point, point):
    min = -1
    size = len(array_of_point)
    for i in range(size):
        dist = np.linalg.norm(np.array(array_of_point[i]) - np.array(point))
        if min == -1 or dist < min:
            min = dist
            closest = array_of_point[i]
    return closest
