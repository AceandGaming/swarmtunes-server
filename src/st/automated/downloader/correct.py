import warnings
from pathlib import Path

import numpy as np
import pyloudnorm as loudnorm
from mutagen.mp3 import MP3
from pydub import AudioSegment, silence

TARGET_LUFS = -16
MIN_DBFS = -55  # trim audio lower then this


def delete_id3_tags(file: Path):
    audio = MP3(file)
    audio.delete()
    audio.save()


def correct_and_convert_mp3(inputFile: Path, output: Path):
    """Normalizes and converts an MP3 file to OGG Vorbis format."""
    if not inputFile.exists():
        raise FileNotFoundError(f"File {inputFile} does not exist.")
    if output.exists():
        raise FileExistsError(f"File {output} already exists.")

    delete_id3_tags(inputFile)

    song = AudioSegment.from_file(inputFile, format="mp3")

    silences = silence.detect_silence(
        song, min_silence_len=300, silence_thresh=MIN_DBFS
    )
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

    samples = np.clip(samples, -1.0, 0.9995)  # prevents clipping

    song = AudioSegment(
        (samples * 32767).astype(np.int16).tobytes(),
        frame_rate=song.frame_rate,
        sample_width=2,
        channels=song.channels,
    )

    song.export(
        output,
        format="mp4",
        codec="aac",
        bitrate="128k",
        parameters=["-movflags", "+faststart"],
    )
    return len(song) / 1000
