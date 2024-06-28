import glob
import itertools
import os
import pandas as pd
from dataclasses import dataclass, field
from typing import List

@dataclass
class Melody:
    name: str
    midi: List[float]
    duration: List[float]
    onset: List[float] = field(init=False)
    total_n_beats: float = field(init=False)

    def __post_init__(self):
        self.onset = [0] + list(itertools.accumulate(self.duration))[:-1]
        self.total_n_beats = sum(self.duration)

    def realize(self, tempo, target_mean_pitch=60.0):
        beat_duration_sec = 60 / tempo
        note_durations_sec = [duration * beat_duration_sec for duration in self.duration]
        total_note_durations_sec = sum(note_durations_sec)

        unnormalised_pitches = self.midi

        # Note: we weight each pitch by its duration when normalising pitch height
        unnormalised_mean_pitch = sum(
            [
                pitch * duration_sec / total_note_durations_sec
                for pitch, duration_sec in zip(unnormalised_pitches, note_durations_sec)
            ]
        )
        transposition = target_mean_pitch - unnormalised_mean_pitch
        pitches = [pitch + transposition for pitch in unnormalised_pitches]

        return {
            "pitches": pitches,
            "note_durations_sec": note_durations_sec,
            "total_note_durations_sec": total_note_durations_sec,
            "transposition": transposition,
        }


def load_melodies(path):
    melodies = [
        load_melody(x) for x in glob.glob(os.path.join(path, "*.csv"))
    ]
    return {
        melody.name: melody
        for melody in melodies
    }


def load_melody(path):
    name = os.path.splitext(os.path.basename(path))[0]
    df = pd.read_csv(path)
    return Melody(name, list(df.midi), list(df.duration))
