import cv2 as cv
import time
import numpy as np
import pygame # For audio
import threading # To play audio without halting the program
import math

# Personal libraries
import HSV
from Play_Sound import *
from FPS import *

from config import *

import detection_cross as dc
import detection_square as ds

# Initialize the Mac camera (using OpenCV to access the default webcam)
dispW = 1280
dispH = 720
cap = cv.VideoCapture(0)  # Use 0 for the default camera

# Set the resolution of the camera feed
cap.set(cv.CAP_PROP_FRAME_WIDTH, dispW)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, dispH)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()


# Main loop for capturing and displaying the camera feed
while True:
    # Starting the timer for fps calculation
    tstart = time.time()
    
    # Capture frame from Mac camera
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to capture image.")
        break

    
    dc.scan_frame_for_crosses(frame)
    ds.scan_frame_for_squares(frame)
    # Masking Looked for colors
    lowerRedMask = HSV.create_hsv_mask(frame, HSV.lowerBound1, HSV.upperBound1)  # Lower red range
    upperRedMask = HSV.create_hsv_mask(frame, HSV.lowerBound2, HSV.upperBound2)  # Upper red range
    combinedRedMask = cv.bitwise_or(lowerRedMask, upperRedMask)
    combinedRedMaskSmall = cv.resize(combinedRedMask, (int(dispW/2), int(dispH/2)))
    FilteredRedMaskSmall = HSV.median_filter(combinedRedMaskSmall)

    FeetMask = HSV.create_hsv_mask(frame, HSV.lowerBoundYellow, HSV.upperBoundYellow)  # Yellow range
    FeetMaskSmall = cv.resize(FeetMask, (int(dispW/2), int(dispH/2)))


    # Fetching the contours of the two red lines------------------------------------------------------

    # Find contours in the red mask
    contours, _ = cv.findContours(combinedRedMask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # Define a minimum area threshold to filter out small contours (red noise)
    min_area_threshold = 10  # Adjust this value based on your requirements

    # Filter contours based on the minimum area
    filtered_contours = [contour for contour in contours if cv.contourArea(contour) > min_area_threshold]

    # Check if there are at least two valid contours
    if len(filtered_contours) >= 2:
        # Sort filtered contours by area and keep the largest two
        sorted_contours_area = sorted(filtered_contours, key=cv.contourArea, reverse=True)[:2]
        
        # Sort the two largest contours by the x-coordinate of their centroids
        sorted_contours = sorted(sorted_contours_area, key=lambda contour: cv.moments(contour)['m10'] / cv.moments(contour)['m00'] if cv.moments(contour)['m00'] != 0 else 0)
        
        # Fetch the two largest red contours and assign them to left_line and right_line
        left_line, right_line = sorted_contours[:2]

        # By now we are sure we have two contours for each red line
        # Visualize red contours and labeling
        for i, contour in enumerate([left_line, right_line]):
            # Draw the contour directly (for red lines, this will handle the inclination)
            cv.drawContours(frame, [contour], -1, (255, 0, 0), 2)  # Red color for the contour

            # Calculate the contour's centroid
            M = cv.moments(contour)
            if M["m00"] != 0:  # Avoid division by zero
                center_x = int(M["m10"] / M["m00"])
                center_y = int(M["m01"] / M["m00"])
            else:
                center_x, center_y = 0, 0  # Default to (0,0) if contour has zero area

            # Add the label to the contour
            label = "left line" if i == 0 else "right line"
            cv.putText(frame, label, (center_x - 50, center_y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv.LINE_AA)

        
        # Detecting feet ----------------------------------------------------------------
        contours, _ = cv.findContours(FeetMask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        centers = []

        min_area_threshold_feet = 200
        # Filter contours based on the minimum area
        filtered_feet_contours = [contour for contour in contours if cv.contourArea(contour) > min_area_threshold_feet]

        # Ensure that at least one foot is detected

        if len(filtered_feet_contours) >= 2: # we likely have both feet

            # Sort filtered feet contours by area and keep the largest two
            sorted_feet_contours_area = sorted(filtered_feet_contours, key=cv.contourArea, reverse=True)[:2]

            # Fetching the centers of the feet (transforming the feet contours to points)
            for contour in sorted_feet_contours_area:
                M = cv.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    centers.append((cx, cy))
                    cv.circle(frame, (cx, cy), 5, (255, 255, 0), -1)  # Draw center for visualization

            centers = sorted(centers, key=lambda point: point[0])  # Sort by x-coordinate
            center_left, center_right = centers[0], centers[1]

            # Calculate the shortest distance from each yellow marker to the red contour
            distance_leftfoot = abs( cv.pointPolygonTest(left_line, center_left, True) )
            distance_rightfoot = abs( cv.pointPolygonTest(right_line, center_right, True) )
            
            # Finding which foot is closer and which one it is 
            if(distance_leftfoot < distance_rightfoot):
                shortest_distance = distance_leftfoot
                foot_flag= 'left'

            else:
                shortest_distance = distance_rightfoot
                foot_flag= 'right'
                
            if(shortest_distance < distance_to_red_threshold):
                play_sound(f"/Users/jacemhagui/Desktop/Academia/EURECOM/ProjectS5/guideme/Audio/Sound Bank/Attention, {foot_flag}.mp3")


            # Display the distances for left and right feet
            #cv.putText(frame, f"Left foot distance: {distance_leftfoot:.2f}", (dispW // 4, dispH // 2 + 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            #cv.putText(frame, f"Right foot distance: {distance_rightfoot:.2f}", (dispW // 4, dispH // 2 + 60), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            #cv.putText(frame, f"shortest distance: {shortest_distance:.2f}", (dispW // 4, dispH // 2 + 100), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        elif(len(filtered_feet_contours) == 1):
            contour =  filtered_feet_contours[0] # Fetching the first and only contour
            M = cv.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                center = (cx, cy)
                cv.circle(frame, (cx, cy), 5, (255, 255, 0), -1)  # Draw center for visualization

            # Calculating Distances
            distance_to_leftline = abs(cv.pointPolygonTest(left_line, center, True))
            distance_to_rightline = abs(cv.pointPolygonTest(right_line, center, True))
            # Fetching the closest foot to danger and how far it is
            if(distance_to_leftline < distance_to_rightline):
                shortest_distance = distance_to_leftline
                foot_flag= 'left'
            else:
                shortest_distance = distance_to_rightline
                foot_flag= 'right'  
            # Warning the user accordingly
            if(shortest_distance < distance_to_red_threshold):
                play_sound(f"/Users/jacemhagui/Desktop/Academia/EURECOM/ProjectS5/guideme/Audio/Sound Bank/Attention, {foot_flag}.mp3")


        else:
            cv.putText(frame, "Feet not detected", (dispW // 4, dispH // 2), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            play_sound("/Users/jacemhagui/Desktop/Academia/EURECOM/ProjectS5/guideme/Audio/Sound Bank/Feet_not_detected.mp3")
    else:
        cv.putText(frame, "Line not detected", (dispW // 4, dispH // 2), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        play_sound("/Users/jacemhagui/Desktop/Academia/EURECOM/ProjectS5/guideme/Audio/Sound Bank/Line_not_detected.mp3")

    # Detect squares and crosses

    #-------------------------------------------------------------------------
    # Update and Overlay the FPS value on the frame
    tend = time.time()
    fps = .99 * fps + .01 * (1 / (tend - tstart))  # To avoid erratic change
    cv.putText(frame, str(int(fps)) + " FPS", pos, font, height, color, weight)

    # Display the processed frame
    cv.imshow('Processed Picture', frame)

    #Display the red tracking mask
    #cv.imshow('Red Mask', combinedRedMaskSmall)
    
    #Display the feet tracking mask
    #cv.imshow('Feet Mask', FeetMaskSmall)

    #Display the Filtered tracking mask
    #cv.imshow('Filtered Red Mask', FilteredRedMaskSmall)

    # Check for exit
    if cv.waitKey(1) == ord('q'):
        kill_Luna = True
        break

cv.destroyAllWindows()