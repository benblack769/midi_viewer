## Midi viewer

This is a research tool for using doc2vec to turn midi files into vectors, and viewing and analyzing those vectors.

### Install

get python-midi from https://github.com/nhpackard/python-midi.git

To install, follow the normal procedure for Python module installation:

    python setup.py install

install additional python packages using

    pip install -r requirments.txt

The additional system packages also need to be installed:

    sudo apt-get install timidity

### Process midi dataset

The main script, `process_midi_dataset.py` takes in 3 inputs.

1. A folder with mid files. This folder is searched recursively. Filenames are assumed to be unique. For example `examples_midis`
2. A path for an output folder. This folder is deleted if it exists, so be careful. For example, `example_midi_output`
3. A csv file listing the filenames in the folder, and any data that should be associated with it: for example, genre, author, key, etc.

For example,

    python process_midi_dataset.py example_midis/ example_midi_output/ example_midis/music_metadata.csv

Generated the folder `example_midi_output`.

### Display generated output

The html files can be viewed as just a local file in your browser, but this misses many features (because browsers block cross-origin requests). To have all features, you need to host the output on a local server.

#### Hosting generated output

A static website can be hosted locally with a simple one-liner like

    python -m SimpleHTTPServer

Alternatively, it can be uploaded to any static website provider.

Note that the service I am using to play midi files does not support https, so your site must be based off http.

I uploaded an example generation to s3. It is viewable via this link:

http://s3-us-west-2.amazonaws.com/classical-piano-display/words/display_template.html

http://s3-us-west-2.amazonaws.com/classical-piano-display/docs/display_template.html

It uses classical piano music midis from http://www.piano-midi.de/ (midis due to Bernd Krueger).

### Website features:
