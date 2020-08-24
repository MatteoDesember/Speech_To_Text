import threading
from datetime import datetime
from queue import Queue
import speech_recognition as sr
import os

TEMP_FILE_NAME = "_temp_file_PCM_16b.wav"
TXT_FILE = "recognized_text.txt"
OUTPUT_FOLDER = "out"
NUMBER_OF_THREADS = 4
AUDIO_TO_RECOGNIZE_QUEUE = Queue()


def save_to_txt(file_path, text):
    """save text to txt file"""
    f = open(file_path, "w+")
    f.write(text)
    f.close()


def recognize(audio, language="en-US"):
    """Recognize audio using Google Recognizer"""
    try:
        text = sr.Recognizer().recognize_google(audio, language=language)
        # text = "Google recognize function disabled"
    except:
        text = "[Not recognized :(]"
    print(text)
    return text


def recognize_audio():
    """recognize audio is method which is used by threads"""
    while True:
        # Get item from queue
        item = AUDIO_TO_RECOGNIZE_QUEUE.get()

        file_name = None
        text = ""

        # Check if type is sr AudioData or dictionary
        if isinstance(item, sr.AudioData):
            # If it is AudioData recognize item
            text = recognize(item, language="pl-PL")

            # Create output folder if not exists
            if not os.path.exists(OUTPUT_FOLDER):
                os.makedirs(OUTPUT_FOLDER)
            file_name = datetime.today().strftime(OUTPUT_FOLDER + "\\%Y.%m.%d %H.%M.%S.%f.txt")

            # Write audio to file
            f = open(file_name + ".wav", "wb+")
            f.write(item.get_wav_data())
            f.close()

        elif isinstance(item, dict):
            # If it is dictionary get audio to recognize from item
            text = recognize(audio=item["audio_to_recognize"],
                             language="pl-PL")
            item["text"] = text

            file_name = item["path"] + ".txt"
        else:
            print("Error! There is no audio in item")

        # Save to file
        save_to_txt(os.path.abspath(file_name), text)

        # Task was completed
        AUDIO_TO_RECOGNIZE_QUEUE.task_done()


def create_threads():
    """Create threads"""
    for _ in range(NUMBER_OF_THREADS):
        thread = threading.Thread(target=recognize_audio)
        thread.daemon = True
        thread.start()


def recognize_from_microphone():
    """Recognize audio from microphone as source"""
    print("Press Ctrl-C to stop recognizing...")

    # Create threads
    create_threads()

    try:
        while True:
            with sr.Microphone() as source:
                # Turn on microphone and start listening to
                print("Say something...")
                # If there is an audio listened by microphone add it to a queue
                audio_listened = sr.Recognizer().listen(source)
                AUDIO_TO_RECOGNIZE_QUEUE.put(audio_listened)

    except KeyboardInterrupt:
        # If there is Ctrl-C pressed break while loop
        pass
