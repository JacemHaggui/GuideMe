import pygame
import threading

# Function to play audio files----------------------------------------------------------------------

# Global flag to track if the sound is playing
sound_playing = False

def play_sound(sound_path):
    global sound_playing
    if not sound_playing:
        def play():
            global sound_playing
            sound_playing = True
            pygame.mixer.init()
            sound_play = pygame.mixer.Sound(sound_path)
            sound_play.play()
            # After the sound finishes playing, set the flag back to False
            while pygame.mixer.get_busy():
                pygame.time.wait(100)  # Wait until the sound finishes
            sound_playing = False

        # Run the sound playback in a separate thread
        threading.Thread(target=play, daemon=True).start()
