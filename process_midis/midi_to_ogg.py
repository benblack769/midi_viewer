'''
Depends on timidity being installed

    sudo apt-get install timidity
'''

import subprocess
import os

def midi_to_ogg(midi_path,ogg_path):
    #input_path = "example_midis/01AusmeinesHerz.mid"
    #output_path = "out.ogg"
    command = ["timidity", midi_path, "-Ov", "-o", ogg_path]
    subprocess.check_call(command,stdout=open(os.devnull, 'w'))
