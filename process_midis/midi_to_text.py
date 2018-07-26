import midi
import argparse
import random
import midi_to_text_methods

'''
Idea: Turn chords into 'words' for doc2vec

different strategies for doing so described in `midi_to_text_methods.py`
'''

def verify_values(ticks):
    for tick in ticks:
        if tick['pitch'] > 127 or tick['pitch'] < 0:
            raise TypeError("bad pitch value")

def tickify_song(song):
    ticks = []
    for i in range(len(song)):
        track = song[i]
        for note in track:
            if note.name == 'Note On':
                ticks.append({
                    'tick': note.tick,
                    'pitch': note.pitch,
                    'channel': note.channel,
                    'on': note.velocity > 0,# if velocity is 0, then it is exactly like a NoteOff event
                })
            elif note.name == 'Note Off':
                ticks.append({
                    'tick': note.tick,
                    'pitch': note.pitch,
                    'channel': note.channel,
                    'on': False,
                })
    verify_values(ticks)
    ticks.sort(key=lambda tick: tick['tick'])
    return ticks

def flatten_chords(chords):
    flat_chords = []
    for chord in chords:
        flat_chord = []
        for channel_pitches in chord.values():
            for pitch in channel_pitches:
                flat_chord.append(pitch)
        flat_chords.append(list(sorted(set(flat_chord))))
    return flat_chords


def pitch_to_str(pitch):
    return str(pitch).zfill(3)

def choords_to_word(chord):
    return "".join(sorted(pitch_to_str(pitch) for pitch in chord))

def chords_to_text(chords):
    return " ".join(choords_to_word(chord) for chord in chords if chord)

def texify_song(song,method_strategy):
    ticks = tickify_song(song)
    chord_to_text_strat = midi_to_text_methods.get_method_by_name(method_strategy)
    channel_chords = chord_to_text_strat(ticks)
    flat_chords = flatten_chords(channel_chords)
    chord_text = chords_to_text(flat_chords)
    return chord_text

def save_text(filename, text):
    with open(filename,'w') as tfile:
        tfile.write(text)

def print_text_stats(chord_text):
    words = chord_text.split()
    print("Total number of chords: {}".format(len(words)))
    print("Total number of unique chords: {}".format(len(set(words))))
    print("Max length of chord: {}".format(len(set(words))))

def read_midi_file(filename):
    song = midi.read_midifile(filename)
    song.make_ticks_abs()
    return song

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Turn a .mid file into a series of chords represented textually")
    parser.add_argument('midi_file', help='Path to .mid file to process')
    parser.add_argument('text_file', help='Path to .txt file to generate')
    parser.add_argument('chordization_strategy', nargs='?',help='name of function in `midi_to_text_methods.py to use`',default="stack_ticks_into_chords_turn_off_when_channel_activates")

    args = parser.parse_args()

    song = read_midi_file(args.midi_file)
    #print(song.sequencer_tempo)
    #exit(1)
    #print(song)
    #exit(1)

    song_text = texify_song(song,args.chordization_strategy)
    save_text(args.text_file,song_text)
    print_text_stats(song_text)
