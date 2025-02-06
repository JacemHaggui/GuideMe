from Play_Sound import *
import math

def calculate_midpoint(point1, point2): # For getting the center between both feet
    """Calculate the midpoint between two points."""
    midpoint = ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2)
    return midpoint

def give_feedback(foot_position, cross_position, square_positions, forward_angle_tolerance=15, cross_threshold=0.5):
    """Guide the user to the cross and warn about squares only if they block the path."""

    if(cross_position is not None):
        angle, distance = calculate_angle_and_distance(foot_position, cross_position)
        
        # Check if we are at the cross
        if distance <= cross_threshold:
            print("You've reached the cross!")  # Replace with audio feedback
            play_sound("/home/jacemhagui/GuideMe/guideme/Audio/Sound Bank/coin.mp3")
            return  # Stop further checks once at the cross

        # Directional guidance to the cross
        if -forward_angle_tolerance <= angle <= forward_angle_tolerance:
            print("Move forward")  # Replace with audio playback
            play_sound("/home/jacemhagui/GuideMe/guideme/Audio/Sound Bank/Forward.mp3")
        elif angle < -forward_angle_tolerance:
            play_sound("/home/jacemhagui/GuideMe/guideme/Audio/Sound Bank/Turn Left.mp3")
        else:
            play_sound("/home/jacemhagui/GuideMe/guideme/Audio/Sound Bank/Turn Right.mp3")

    # Warn only if a square is directly in the path
    if(square_positions is not None):
        for square in square_positions:
            square_angle, square_distance = calculate_angle_and_distance(foot_position, square)
            if square_distance < 250:
                play_sound("/home/jacemhagui/GuideMe/guideme/Audio/Sound Bank/Obstacle Ahead !.mp3")       
            if -forward_angle_tolerance <= square_angle <= forward_angle_tolerance:
                play_sound("/home/jacemhagui/GuideMe/guideme/Audio/Sound Bank/Obstacle Ahead !.mp3")
    
    return 