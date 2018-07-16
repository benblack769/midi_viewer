import sklearn.manifold
import numpy as np
import pandas
import argparse
import subprocess
import os
from process_midis import midi_to_text
from process_midis import text_to_midi

MIDI_FOLDER = "midi_files/"
MIDI_TEXT_FOLDER = "midi_text_files/"
MIDI_TEXT_MIDI_FOLDER = "midi_text_midi_files/"


def all_midi_files(root_dir):
    find_call = ["find", root_dir, "-name", '*.mid', "-type", "f" ]
    filename_list = subprocess.check_output(find_call).decode('utf-8').split("\n")[:-1]
    return filename_list

def copy_file(src,dest):
    contents = open(src,'rb').read()
    open(dest,'wb').write(contents)


def process_file(source_file,output_path):
    dest_mid_filename = os.path.join(output_path,MIDI_FOLDER,os.path.basepath(source_file))
    dest_text_filename = os.path.join(output_path,MIDI_TEXT_FOLDER,os.path.basepath(source_file)+".txt")
    try:
        midi_str = midi_to_text.texify_song(midi_to_text.read_midi_file(filename))
    except TypeError as e:
        return False

    with open(text_filename,'w') as text_file:
        text_file.write(midi_str)
        
    copy_file(source_file,dest_mid_filename)

    return True

def copy_all_files_to_output(paths,output_path):
    for path in paths:
        out_path =
        copy_file(path,out_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Turn a folder full of .mid files into csvs with relevant data")
    parser.add_argument('midi_dataset_root', help='Path to folder full of .mid files (looks recursively into subfolders for .mid files)')
    parser.add_argument('output_data_path', help='Path to output folder where files will be stored')

    args = parser.parse_args()

    all_midi_files = all_midi_files(args.midi_dataset_root)
    song = all_midi_files(args.midi_dataset_root)
