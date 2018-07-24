import midi
import argparse

def read_midi_file(filename):
    song = midi.read_midifile(filename)
    song.make_ticks_abs()
    return song

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="print a .midi file")
    parser.add_argument('midi_file', help='Path to .midi file to print')

    args = parser.parse_args()

    song = read_midi_file(args.midi_file)
    print(song)
