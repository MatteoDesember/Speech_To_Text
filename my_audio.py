from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from recognizer import *


class MyAudio:
    # This is list with divided chunk audio with added silent at the beginning and end on each one
    audio_chunk_list = []

    # This is just audio file stored by AudioSegment class
    sound_segment = None

    def __init__(self, file_path):
        """Set up some variables"""
        self.file_path = file_path
        self.file_dir = os.path.dirname(self.file_path)
        self.file_name = os.path.basename(self.file_path)
        self.file_name_without_extension = os.path.splitext(self.file_path)[0]

    def prepare(self):
        """Prepare audio so it is easiest to recognize"""
        print("Preparing...")
        try:
            # Create temporary folder
            if not os.path.exists(self.file_name_without_extension):
                os.makedirs(self.file_name_without_extension)

            # Read audio from file
            self.sound_segment = AudioSegment.from_file(self.file_path)

        except Exception as e:
            print("Error in prepare " + str(e))

    def divide(self):
        """Divide audio into chunks"""
        print("Dividing...")

        # Detect silents in audio and divide it
        chunks = detect_nonsilent(self.sound_segment,
                                  min_silence_len=250,
                                  # This value works well. Set treshold on -20 dBFS
                                  silence_thresh=self.sound_segment.dBFS - 20,
                                  seek_step=1)

        # clear audi_chunk_list
        self.audio_chunk_list.clear()

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

            # append audio data to chunk list
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
        """Recognize all audio from audio chunk list"""
        print("Recognizing...")
        all_text = ""

        if not os.path.exists(self.file_name_without_extension):
            os.makedirs(self.file_name_without_extension)

        create_threads()

        # Add all audio chunk to queue
        for item in self.audio_chunk_list:
            AUDIO_TO_RECOGNIZE_QUEUE.put(item)

        # Wait until audio queue is empty
        AUDIO_TO_RECOGNIZE_QUEUE.join()

        # Save all work to file
        for item in self.audio_chunk_list:
            all_text += item["text"] + "\n"
        save_to_txt(self.file_name_without_extension + ".txt", all_text)
