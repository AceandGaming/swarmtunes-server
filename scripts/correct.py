from pydub import AudioSegment, silence
import pyloudnorm as loudnorm
import numpy as np
import warnings
from scripts.load_metadata import DeleteID3Tags
import acoustid
from os import PathLike

TARGET_LUFS = -16
MIN_DBFS = -55 #trim audio lower then this

def CorrectMP3(inputFile: PathLike, output: PathLike):
    DeleteID3Tags(inputFile)
    
    song = AudioSegment.from_file(inputFile, format="mp3")

    silences = silence.detect_silence(song, min_silence_len=300, silence_thresh=MIN_DBFS)
    start = 0
    end = len(song)

    if silences:
        if silences[0][0] == 0:
            start = silences[0][1]
        if silences[-1][1] == len(song):
            end = silences[-1][0]
    song = song[start:end].fade_in(100).fade_out(100)

    samples = np.array(song.get_array_of_samples()) / (1 << 15)
    meter = loudnorm.Meter(song.frame_rate)
    loudness = meter.integrated_loudness(samples)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        samples = loudnorm.normalize.loudness(samples, loudness, TARGET_LUFS)

    samples = np.clip(samples, -1.0, 0.9995) #prevents clipping

    song = song._spawn((samples * (1 << 15)).astype(np.int16).tobytes())

    #song.export(output, format="ogg", codec="vorbis", bitrate="128k")
    song.export(output, format="mp3", bitrate="128k")

    return acoustid.fingerprint_file(str(output))