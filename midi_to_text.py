import midi
import argparse
import copy
import random
from collections import defaultdict

'''
Idea: Turn chords into 'words' for doc2vec

midi files describe music as several independent channels of sound.

the file format describes notes within a channel as an interval:

(note start, pitch)
(note end, pitch)

This gives rise to a natural chord at every time step.

Unfortunately, the volume of the note decreases after its start,
so many files choose not to end the note until long after it is initiated,
leading to absurdly huge and unweldy chords.

So notes need to be terminated in some way other than a "note end"
event. The code describes 3 ways of doing this:

1.  `stack_ticks_into_chords`:
        only terminate when note ends
2.  `stack_ticks_into_chords_turn_off_when_channel_activates`:
        When a new note within the same channel activates,
        terminate all notes in the channel activated in a previous tick.
3.  'stack_ticks_into_chords_turn_off_on_timeout':
        Notes time out after a certain number of ticks
'''

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
    ticks.sort(key=lambda tick: tick['tick'])
    return ticks

def merge_dicts(base_dict,replace_dict):
    merge_dict = copy.copy(base_dict)
    for key in replace_dict:
        merge_dict[key] = replace_dict[key]
    return merge_dict

def stack_ticks_into_chords(ticks):
    chords = [defaultdict(set)]
    tick_idx = 0
    while tick_idx < len(ticks):
        tick_num = ticks[tick_idx]['tick']
        chord = copy.deepcopy(chords[-1])
        some_turned_on = False
        while tick_idx < len(ticks) and ticks[tick_idx]['tick'] == tick_num:
            pitch = ticks[tick_idx]['pitch']
            channel = ticks[tick_idx]['channel']
            if ticks[tick_idx]['on'] is False:
                chord[channel].discard(pitch)# remove if exists
            else:
                some_turned_on = True
                chord[channel].add(pitch)
            tick_idx += 1

        if some_turned_on:
            chords.append(chord)
    return chords

def stack_ticks_into_chords_turn_off_when_channel_activates(ticks):
    chords = [defaultdict(set)]
    tick_idx = 50
    while tick_idx < len(ticks):
        tick_num = ticks[tick_idx]['tick']
        chord = defaultdict(set)
        some_turned_on = False
        while tick_idx < len(ticks) and ticks[tick_idx]['tick'] == tick_num:
            pitch = ticks[tick_idx]['pitch']
            channel = ticks[tick_idx]['channel']
            if ticks[tick_idx]['on'] is False:
                chord[channel].discard(pitch)# remove if exists
            else:
                some_turned_on = True
                chord[channel].add(pitch)
            tick_idx += 1

        if some_turned_on:
            chords.append(merge_dicts(chords[-1],chord))
    return chords

def stack_ticks_into_chords_turn_off_on_timeout(ticks, TICK_TIMOUT=0):
    chords = [defaultdict(dict)]
    tick_idx = 0
    while tick_idx < len(ticks):
        tick_num = ticks[tick_idx]['tick']
        chord = copy.deepcopy(chords[-1])
        for channel_pitchs in chord.values():
            for pitch, tick in list(channel_pitchs.items()):
                if tick + TICK_TIMOUT < tick_num:
                    del channel_pitchs[pitch]

        some_turned_on = False
        while tick_idx < len(ticks) and ticks[tick_idx]['tick'] == tick_num:
            pitch = ticks[tick_idx]['pitch']
            channel = ticks[tick_idx]['channel']
            if ticks[tick_idx]['on'] is False:
                if pitch in chord[channel]:
                    del chord[channel][pitch]
            else:
                chord[channel][pitch] = tick_num
                some_turned_on = True
            tick_idx += 1

        if some_turned_on:
            chords.append(chord)
    return chords

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

def texify_song(song):
    ticks = tickify_song(song)
    channel_chords = stack_ticks_into_chords_turn_off_when_channel_activates(ticks)
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

    args = parser.parse_args()

    song = read_midi_file(args.midi_file)
    #print(song.sequencer_tempo)
    #exit(1)
    #print(song)
    #exit(1)

    song_text = texify_song(song)
    save_text(args.text_file,song_text)
    print_text_stats(song_text)
