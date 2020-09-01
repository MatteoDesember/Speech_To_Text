from my_audio import *
import tkinter as tk
from tkinter import filedialog, Tk
import os

INFO = """  * l [lg-LG] - change language (default is: en-EN)
  * m - recognize_by_google from microphone as source
  * f - recognize_by_google from audio file eg. .wav
  * e - exit program
"""

"""
    audio_441_16.wav'  # works
    audio_441_24.wav'  # works
    audio_441_32.wav'  # doesn't work
    audio_480_16.wav'  # works
    audio_480_24.wav'  # works
    audio_480_32.wav'  # doesn't work
"""


def open_file_dialog():
    """open_file_dialog opens file dialog and return selected file chosen by user as string"""
    file_path = tk.filedialog.askopenfilename()
    # file_dir = os.path.dirname(os.path.abspath(file))
    # file_name = os.path.basename(os.path.abspath(file))
    return file_path


# Little console for user
while True:
    print("Tell me what you wanna do:")
    user_input = input(INFO)

    if user_input == 'm':
        recognize_from_microphone()

    elif user_input == 'f':
        root = Tk()
        root.withdraw()
        print("Select an audio file to recognize_by_google...")
        audio_path = open_file_dialog()
        if audio_path:
            print("Let's start...")
            my_audio = MyAudio(os.path.abspath(audio_path))
            my_audio.prepare()
            my_audio.divide()
            my_audio.recognize_all()
        else:
            print("Doesn't select any file")

    elif "l" in user_input:
        if user_input.find("l") == 0:
            lg_input = user_input.split(" ")
            if len(lg_input) == 2:
                lg = lg_input[1]
                if lg == "en":
                    LANGUAGE = "en-EN"
                elif lg == "pl":
                    LANGUAGE = "pl-PL"
                elif lg == "no":
                    LANGUAGE = "no-NO"
                elif lg == "ru":
                    LANGUAGE = "ru-RU"
                elif lg == "de":
                    LANGUAGE = "de-DE"
                else:
                    LANGUAGE = lg
                print("Changed language to: " + LANGUAGE)
            else:
                print("Does't select an language")

    elif user_input == 'e' or user_input == 'exit':
        break
    else:
        print("Incorrect command.")

print("Exiting program...")
