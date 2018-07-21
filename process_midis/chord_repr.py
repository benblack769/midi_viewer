import midi
import re
import text_to_midi

all_chords = {midi.__dict__[k]:k for k in midi.__dict__.keys() if re.match(r"[A-G]((s|b)?)_[0-9](0?)",k) }

def chord_text_repr(numeric_chord_text):
    return ";".join(all_chords[num] for num in text_to_midi.string_to_pitches(numeric_chord_text))

#print(chord_text_repr("050060066069"))
#print(chord_text_repr("043062067071"))
