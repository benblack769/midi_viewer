import subprocess
import os
import tempfile
import shutil
import argparse
import distutils.spawn

def check_if_system_commands_present():
    if not distutils.spawn.find_executable('ffmpeg'):
        raise RuntimeError('''
        You need to install the command line tool `ffmpeg` to run this.
        On Ubuntu, this can be installed with `sudo apt-get install ffmpeg`
        ''')
    if not distutils.spawn.find_executable('timidity'):
        raise RuntimeError('''
        You need to install the command line tool `timidity` to run this.
        On Ubuntu, this can be installed with `sudo apt-get install timidity++`
        ''')

def midi_to_mp3(midi_path,mp3_output_path):
    #input_path = "example_midis/01AusmeinesHerz.mid"
    #output_path = "out.ogg"
    check_if_system_commands_present()
    with tempfile.NamedTemporaryFile(suffix=".wav") as wav_file:
        print(wav_file.name)
        to_wav_command = ["timidity",
            midi_path, # input path
            "-Ow", # output format is a wav file
            "-o", wav_file.name # output path
        ]
        subprocess.check_call(to_wav_command,stdout=open(os.devnull, 'w'))
        to_mp3_command = ["ffmpeg",
            "-i", wav_file.name, # input path
            "-loglevel", "warning", # suppreses output except for warnings
            "-acodec", "libmp3lame",# encode as mp3
            mp3_output_path # output path
        ]
        subprocess.check_call(to_mp3_command,stdout=open(os.devnull, 'w'))

#midi_to_mp3("example_midis/01AusmeinesHerz.mid","arg.mp3")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Turn a .mid file into a mp3 file")
    parser.add_argument('midi_path', help='Path to .mid file to process')
    parser.add_argument('mp3_path', help='output .mp3 file path')

    args = parser.parse_args()
    midi_to_mp3(args.midi_path,args.mp3_path)
