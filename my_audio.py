import soundfile
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import os

TEMP_FILE_NAME = "_temp_file_PCM_16b.wav"
TXT_FILE = "recognized_text.txt"


class MyAudio:
    # This is list with divided chunk audio with added silent at the beginning and end on each one
    audio_chunk_list = []

    # This is just audio file stored by AudioSegment class
    sound_segment = None

    def __init__(self, file_path, language="en-US"):

        self.file_path = file_path
        self.file_dir = os.path.dirname(self.file_path)
        self.file_name = os.path.basename(self.file_path)
        self.file_name_without_extension = os.path.splitext(self.file_path)[0]
        self.language = language

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
                "audio": audio,
                "path": path
            })
        print("Break point")#TODO

    def recognize_all(self):

        if not os.path.exists(self.file_name_without_extension):
            os.makedirs(self.file_name_without_extension)
        all_recognized_text = ""
        for item in self.audio_chunk_list:
            # Recognize audio

            audio_to_recognize = sr.AudioData(item["audio"].raw_data,
                                              sample_rate=item["audio"].frame_rate,
                                              sample_width=item["audio"].frame_width)

            item["text"] = self.recognize(audio_to_recognize, language=self.language)

            all_recognized_text += item["text"] + "\r\n"

            # Safe temp txt file so if program will crash there is no work wasted
            self.save_to_txt(item["path"] + ".txt", item["text"])

        # Save all work to file
        self.save_to_txt(self.file_name_without_extension + ".txt", all_recognized_text)

    def recognize(self, audio, language="en-US"):
        # print("Google is recognizing...")
        try:
            text = sr.Recognizer().recognize_google(audio, language=language)
            print(text)
        except:
            text = "[Not Recognized :(]\r\n"
        return text

        # with sr.AudioFile(item["sound_segment"]) as source: # Doesnt work
        # with sr.WavFile(item["path"]) as source:
        #     audio_listened = self.recognizer.listen(source)  # audio = recognizer.record(source)

    # Save global txt
    def save_to_txt(self, file, text):
        f = open(file, "w+")
        f.write(text + "\n")
        f.close()
