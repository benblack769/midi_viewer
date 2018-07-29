import subprocess
import os
import tempfile
import shutil
import soundfile as sf
import argparse
import random
import distutils.spawn


def midi_to_wav(midi_path,wav_file):
    if not distutils.spawn.find_executable('timidity'):
        raise RuntimeError('''
        You need to install the command line tool `timidity` to run this.
        On Ubuntu, this can be installed with `sudo apt-get install timidity++`
        ''')
    to_wav_command = ["timidity",
        midi_path, # input path
        "-Ow", # output format is a wav file
        "-o", wav_file # output path
    ]
    subprocess.check_call(to_wav_command,stdout=open(os.devnull, 'w'))

def wav_to_mp3(wav_file,mp3_output_path,max_duration=None):
    if not distutils.spawn.find_executable('ffmpeg'):
        raise RuntimeError('''
        You need to install the command line tool `ffmpeg` to run this.
        On Ubuntu, this can be installed with `sudo apt-get install ffmpeg`
        ''')

    to_mp3_command = ["ffmpeg",
        "-i", wav_file, # input path
        "-loglevel", "warning", # suppreses output except for warnings
        "-acodec", "libmp3lame",# encode as mp3
        "-y", # overwrite if exists
        mp3_output_path # output path
    ]
    subprocess.check_call(to_mp3_command,stdout=open(os.devnull, 'w'))

def make_window(wav_file,window_size=30):
    data,samplerate = sf.read(wav_file)
    number_of_seconds = len(data)//samplerate

    number_of_choices = number_of_seconds - window_size
    if number_of_choices > 0:
        start_sec = random.randrange(number_of_choices)
        end_sec = start_sec + window_size
        data = data[start_sec*samplerate:end_sec*samplerate]
        sf.write(wav_file,data,samplerate)
    else:
        print("file not long enough")
        exit(0)

def midi_to_30s_mp3(midi_path,mp3_output_path):
    #input_path = "example_midis/01AusmeinesHerz.mid"
    #output_path = "out.ogg"
    with tempfile.NamedTemporaryFile(suffix=".wav") as wav_file:
        midi_to_wav(midi_path,wav_file.name)
        window_size = 30
        make_window(wav_file.name,window_size)
        wav_to_mp3(wav_file.name,mp3_output_path)

#midi_to_mp3("example_midis/01AusmeinesHerz.mid","arg.mp3")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Turn a .mid file into a mp3 file")
    parser.add_argument('midi_path', help='Path to .mid file to process')
    parser.add_argument('mp3_path', help='output .mp3 file path')

    args = parser.parse_args()
    midi_to_30s_mp3(args.midi_path,args.mp3_path)
