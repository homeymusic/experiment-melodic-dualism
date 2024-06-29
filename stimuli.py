import glob
import itertools
import os
import pandas as pd
from dataclasses import dataclass, field
from typing import List
import numpy as np 

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

@dataclass
class DiatonicMode:
  name: str
  midi: [int]
  home_midi: int
  def __init__(self, name: str, midi: [int], home_midi: int):
    self.name = name
    self.midi = np.sort(midi % 12)
    self.home_midi = home_midi

def diatonic_modes():
    lydian     = np.array([0,2,4,6,7,9,11])
    locrian    = -lydian
    ionian     = lydian + np.array([0,0,0,-1,0,0,0])
    phrygian   = -ionian
    mixolydian = ionian + np.array([0,0,0,0,0,0,-1])
    aeolian    = -mixolydian
    dorian     = mixolydian + np.array([0,0,-1,0,0,0,0])
    
    return {
      'lydian':     DiatonicMode('lydian',     lydian,     65),
      'locrian':    DiatonicMode('locrian',    locrian,    59),
      'ionian':     DiatonicMode('ionian',     ionian,     60),
      'phrygian':   DiatonicMode('phrygian',   phrygian,   64),
      'mixolydian': DiatonicMode('mixolydian', mixolydian, 55),
      'aeolian':    DiatonicMode('aeolian',    aeolian,    57),
      'dorian':     DiatonicMode('dorian',     dorian,     62)
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
