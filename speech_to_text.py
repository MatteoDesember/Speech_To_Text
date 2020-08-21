from my_audio import MyAudio
import speech_recognition as sr
import threading
import tkinter as tk
from tkinter import filedialog, Tk
import os

INFO = """  * m - recognize from microphone as source
  * f - recognize from audio file eg. .wav
  * h - print help
  * e - exit program
"""

'''
    audio_441_16.wav'  # works
    audio_441_24.wav'  # doesn't play
    audio_441_32.wav'  # doesn't open
    audio_480_16.wav'  # works
    audio_480_24.wav'  # doesn't play
    audio_480_32.wav'  # doesn't open
'''

'''
    open_file_dialog opens file dialog and return selected file chosen by user as string
'''


def open_file_dialog():
    file_path = tk.filedialog.askopenfilename()
    # file_dir = os.path.dirname(os.path.abspath(file))
    # file_name = os.path.basename(os.path.abspath(file))
    return file_path


# Little console for user
while True:
    print("Tell me what you wanna do:")
    user_input = input(INFO)
    # user_input = 'm'

    if user_input == 'm':
        print("Press Ctrl-C to stop recognizing...")
        try:
            iterator = 0
            while True:
                with sr.Microphone() as source:
                    print("Say sth... " + str(iterator))
                    audio_listened = sr.Recognizer().listen(source)
                    thread1 = threading.Thread(target=MyAudio.recognize, args=(iterator, audio_listened))
                    thread1.start()
                    iterator += 1

        except KeyboardInterrupt:
            # print("Press Ctrl-C to stop recognizing...")
            pass

    elif user_input == 'f':
        root = Tk()
        root.withdraw()
        print("Select an audio to recognize...")
        audio_path = open_file_dialog()
        if audio_path:
            my_audio = MyAudio(os.path.abspath(audio_path), language="pl-PL")
            my_audio.prepare()
            my_audio.divide()
            my_audio.recognize_all()
        else:
            print("Doesn't select any file")

    elif user_input == 't':
        print("test")
        # file_path = os.path.dirname(os.path.abspath(recognizer'C:\Users\Mateusz\Desktop\StT\Speech Recognition\SpeechRecognitionTest\Main_3.wav')) #Static selection
        # dir = os.path.dirname(os.path.abspath(file_path))
        # file = os.path.basename(os.path.abspath(file_path))
        file_dir = "test\\test_audio.wav"
        my_audio = MyAudio(os.path.abspath(file_dir), language="pl-PL")
        my_audio.prepare()
        my_audio.divide()
        my_audio.recognize_all()

        with sr.WavFile('test\\test_audio.wav') as source:
            audio_listened = sr.Recognizer().listen(source)
            out = sr.Recognizer().recognize_google(audio_listened, language="pl-PL")
            print(out)

    elif user_input == 'h':
        print(INFO)

    elif user_input == 'e' or user_input == 'exit':
        break

    else:
        print("Incorrect command.")

print("Exiting program...")
