import soundfile
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import os
from datetime import datetime
import threading
from queue import Queue

TEMP_FILE_NAME = "_temp_file_PCM_16b.wav"
TEXT = ""
TXT_FILE = "recognized_text.txt"
OUTPUT_FOLDER = "out"
NUMBER_OF_THREADS = 4
AUDIO_TO_RECOGNIZE_QUEUE = Queue()


def save_to_txt(file_path, text):
    f = open(file_path, "w+")
    f.write(text)
    f.close()


def recognize(audio, language="en-US", txt_file_name=None):
    # Recognize audio
    try:
        text = sr.Recognizer().recognize_google(audio, language=language)
        # text = "Google recognize function disabled"
    except:
        text = "[Not Recognized :(]"
    print(text)

    if txt_file_name is None:
        if not os.path.exists("out"):
            os.makedirs("out")
        txt_file_name = datetime.today().strftime("out\\%Y.%m.%d %H.%M.%S.%f.txt")

    # Safe temp txt file so if program will crash there is no work wasted
    save_to_txt(os.path.abspath(txt_file_name), text)

    return text


def recognize_audio():
    while True:
        audio_listened = AUDIO_TO_RECOGNIZE_QUEUE.get()
        recognize(audio_listened, language="pl-PL")
        AUDIO_TO_RECOGNIZE_QUEUE.task_done()


def recognize_dict():
    while True:
        item = AUDIO_TO_RECOGNIZE_QUEUE.get()
        item["text"] = recognize(audio=item["audio_to_recognize"],
                                 language="pl-PL",
                                 txt_file_name=item['path']+".txt")
        AUDIO_TO_RECOGNIZE_QUEUE.task_done()


def create_threads(target):
    for _ in range(NUMBER_OF_THREADS):
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()


def recognize_from_microphone():
    print("Press Ctrl-C to stop recognizing...")

    create_threads(recognize_audio)

    all_recognized_text = ""
    try:
        while True:
            with sr.Microphone() as source:
                print("Say something...")
                audio_listened = sr.Recognizer().listen(source)
                AUDIO_TO_RECOGNIZE_QUEUE.put(audio_listened)
    except KeyboardInterrupt:
        pass
    save_to_txt(TXT_FILE + ".txt", all_recognized_text)


class MyAudio:
    # This is list with divided chunk audio with added silent at the beginning and end on each one
    audio_chunk_list = []

    # This is just audio file stored by AudioSegment class
    sound_segment = None

    def __init__(self, file_path):

        self.file_path = file_path
        self.file_dir = os.path.dirname(self.file_path)
        self.file_name = os.path.basename(self.file_path)
        self.file_name_without_extension = os.path.splitext(self.file_path)[0]

    def prepare(self):
        try:
            # Create temporary folder
            if not os.path.exists(self.file_name_without_extension):
                os.makedirs(self.file_name_without_extension)

            data, sample_rate = soundfile.read(self.file_path)

            # Save as PCM16. Other bitrate doesn't work well
            soundfile.write(self.file_name_without_extension + "\\" + TEMP_FILE_NAME,
                            data,
                            sample_rate,
                            subtype='PCM_16')

            self.sound_segment = AudioSegment.from_file(self.file_name_without_extension + "\\" + TEMP_FILE_NAME)
        except Exception:
            print("Error in prepare")

    def divide(self):
        # Detect silents in audio and divide it
        chunks = detect_nonsilent(self.sound_segment,
                                  min_silence_len=250,
                                  # This value works well. Set treshold on -20 dBFS
                                  silence_thresh=self.sound_segment.dBFS - 20,
                                  seek_step=1)

        for start_i, end_i in chunks:
            keep_silence = 300

            # Add some silence at the beginning and at the end
            start_i_a = max(0, start_i - keep_silence)
            end_i_a = end_i + keep_silence
            path = self.file_name_without_extension + "\\_splitted_{}_{}_{}_{}.wav".format(start_i_a,
                                                                                           start_i,
                                                                                           end_i, end_i_a)

            # short_silence = AudioSegment.silent(duration=50)
            # audio = short_silence + sound_segment[self.start_i:self.end_i] + short_silence
            audio = self.sound_segment[start_i_a:end_i_a]
            audio.export(path, format="wav")

            # self.audio_chunk_list.append({start_i, end_i, self.sound_segment, path})

            self.audio_chunk_list.append({
                "start_i": start_i,
                "end_i": end_i,
                "path": path,
                "audio": audio,
                "audio_to_recognize": sr.AudioData(audio.raw_data,
                                                   audio.frame_rate,
                                                   audio.frame_width)
            })

    def recognize_all(self):

        global TEXT

        if not os.path.exists(self.file_name_without_extension):
            os.makedirs(self.file_name_without_extension)

        create_threads(recognize_dict)

        for item in self.audio_chunk_list:
            AUDIO_TO_RECOGNIZE_QUEUE.put(item)

        AUDIO_TO_RECOGNIZE_QUEUE.join()

        # Save all work to file
        for item in self.audio_chunk_list:
            TEXT += item["text"] + "\n"
        save_to_txt(self.file_name_without_extension + ".txt", TEXT)
