import sklearn.manifold
import numpy as np
import pandas
import argparse
import subprocess
import os
import shutil
from process_midis import midi_to_text
from process_midis import text_to_midi
import run_doc2vec_on_songs
import json

MIDI_FOLDER = "midi_files/"
MIDI_TEXT_FOLDER = "midi_text_files/"
MIDI_TEXT_MIDI_FOLDER = "midi_text_midi_files/"
#FILENAME_LIST = "files.txt"
OUT_DATAFRAME = "all_data.csv"
OUT_JSON_VIEW = "all_data.json"
VIEWER_HTML = "display_template.html"
VIEWER_JS = "template.js"
VIEWER_JSON = "template_json.js"
MIDI_VECTOR_LIST = "midi_vecs.npy"
ERROR_LOG = "errors.txt"

def all_midi_files(root_dir):
    find_call = ["find", root_dir, "-name", '*.mid', "-type", "f" ]
    filename_list = subprocess.check_output(find_call).decode('utf-8').split("\n")[:-1]
    return filename_list


def process_file(source_path,output_path):
    source_name = os.path.basename(source_path)
    dest_mid_filename = os.path.join(output_path,MIDI_FOLDER,source_name)
    dest_text_filename = os.path.join(output_path,MIDI_TEXT_FOLDER,source_name+".txt")
    dest_text_midi_filename = os.path.join(output_path,MIDI_TEXT_MIDI_FOLDER,source_name)
    try:
        midi_str = midi_to_text.texify_song(midi_to_text.read_midi_file(source_path))
    except TypeError as e:
        # log error in log file
        open(os.path.join(output_path,ERROR_LOG),'a').write("Exception {} encountered for filename {}".format(str(e),source_path))
        return False

    with open(dest_text_filename,'w') as text_file:
        text_file.write(midi_str)

    shutil.copyfile(source_path,dest_mid_filename)

    text_to_midi.song_convert(dest_text_filename,dest_text_midi_filename)

    return True

def process_all_files(paths,output_path):
    for path in paths:
        process_file(path,output_path)

def make_dir_overwrite(name):
    if os.path.exists(name):
        if os.path.isdir(name):
            shutil.rmtree(name)
        else:
            os.remove(name)
    os.mkdir(name)

def init_dirs(output_path):
    make_dir_overwrite(output_path)
    make_dir_overwrite(os.path.join(output_path,MIDI_FOLDER))
    make_dir_overwrite(os.path.join(output_path,MIDI_TEXT_FOLDER))
    make_dir_overwrite(os.path.join(output_path,MIDI_TEXT_MIDI_FOLDER))

def calc_tsne(data):
    tsne = sklearn.manifold.TSNE()
    #print(data.shape)
    #exit(1)
    transformed_data = tsne.fit_transform(data)

    return transformed_data
    #print(data)

def associate_metadata(data_2d, associate_dataframe, actual_filenames):
    xvals,yvals = np.transpose(data_2d)
    val_dataframe = pandas.DataFrame(data={
        "filename":actual_filenames,
        "x":xvals,
        "y":yvals
    })
    print(val_dataframe['filename'][0].__class__)
    print(associate_dataframe['filename'][0].__class__)
    joined_metadata = val_dataframe.merge(associate_dataframe,on="filename",how="left",sort=True)
    return joined_metadata

def are_unique(items):
    return len(items) == len(set(items))

def csv_to_json(csv_name,json_name):
    fieldnames = ("FirstName","LastName","IDNumber","Message")
    reader = csv.DictReader( csvfile, fieldnames)
    out = json.dumps( [ row for row in reader ] )

def read_file(filename):
    with open(filename) as  file:
        return file.read()

def prepare_json_var(json_name,js_name):
    with open(js_name,'w') as js_file:
        js_file.write("var input_json_data = " + read_file(json_name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Turn a folder full of .mid files into csvs with relevant data")
    parser.add_argument('midi_dataset_root', help='Path to folder full of .mid files (looks recursively into subfolders for .mid files)')
    parser.add_argument('output_data_path', help='Path to output folder where files will be stored')
    parser.add_argument('file_associated_data', help='Path to csv file where file metadata is stored. Assumes there is a header, with a key "filename", which corresponds to the filename')

    args = parser.parse_args()

    output_path = args.output_data_path
    init_dirs(output_path)
    all_midi_files = all_midi_files(args.midi_dataset_root)

    if not are_unique([os.path.basename(path) for path in all_midi_files]):
        raise RuntimeError("directory must have unique filenames for all midi files.")

    process_all_files(all_midi_files,output_path)

    all_text_files = list(sorted(os.listdir(os.path.join(output_path,MIDI_TEXT_FOLDER))))

    all_text_paths = [os.path.join(output_path,MIDI_TEXT_FOLDER,name) for name in all_text_files]
    # save filename order
    #open(os.path.join(output_path,FILENAME_LIST),'w').write("\n".join(all_text_files))

    doc_vecs = run_doc2vec_on_songs.run_doc2vec(all_text_paths)

    np.save(os.path.join(output_path,MIDI_VECTOR_LIST),doc_vecs)

    tranformed_data = calc_tsne(doc_vecs)

    out_dataframe = associate_metadata(tranformed_data,pandas.read_csv(args.file_associated_data),[s[:-4] for s in all_text_files])
    out_dataframe.to_csv(os.path.join(output_path,OUT_DATAFRAME),index=False)
    out_dataframe.to_json(os.path.join(output_path,OUT_JSON_VIEW),orient="records")
    shutil.copyfile("viewer/display_template.html",os.path.join(output_path,VIEWER_HTML))
    shutil.copyfile("viewer/template.js",os.path.join(output_path,VIEWER_JS))
    prepare_json_var(os.path.join(output_path,OUT_JSON_VIEW),os.path.join(output_path,VIEWER_JSON))
