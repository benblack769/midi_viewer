import argparse
import subprocess
import midi_to_text
import multiprocessing
import text_to_midi
import sys

root_dir = ".."

def run_midi_on_one(filename):
    text_filename = filename+".txt"
    midi_genfilename = text_filename+".mid"
    try:
        midi_str = midi_to_text.texify_song(midi_to_text.read_midi_file(filename))

        with open(text_filename,'w') as text_file:
            text_file.write(midi_str)

        #text_to_midi.song_convert(text_filename,midi_genfilename)
    except TypeError as e:
        print(filename)
        print(e)
        print(e.__class__)
        sys.stdout.flush()

def all_midi_files():
    find_call = "find {} -name '*.mid' -type f".format(root_dir)
    print(find_call)

    filename_list = subprocess.check_output(find_call,shell=True).decode('utf-8').split("\n")[:-1]

    print(filename_list)
    pool = multiprocessing.Pool(processes=8)

    pool.map(run_midi_on_one,filename_list)

all_midi_files()
