import sklearn.manifold
from sklearn.metrics import pairwise_distances
import numpy as np
import pandas
import argparse
import subprocess
import os
import shutil
from process_midis import midi_to_text
from process_midis import midi_to_ogg
from process_midis import text_to_midi
from process_midis import chord_repr
import run_doc2vec_on_songs
import multiprocessing
import json
import math
import random
import tempfile

DOCUMENT_FILES = "docs/"
WORD_FILES = "words/"
MIDI_FOLDER = "midi_files/"
MIDI_TEXT_FOLDER = "midi_text_files/"
MIDI_TEXT_MIDI_FOLDER = "midi_text_midi_files/"
MIDI_OGG_FOLDER = "midi_ogg_files/"
#FILENAME_LIST = "files.txt"
OUT_DATAFRAME = "all_data.csv"
OUT_JSON_VIEW = "all_data.json"
VIEWER_HTML = "display_template.html"
VIEWER_JS = "template.js"
VIEWER_JSON = "template_json.js"
VEC_JSON = "vec_json.js"
MIDI_VECTOR_LIST = "midi_vecs.npy"
ERROR_LOG = "errors.txt"

NUM_DIMENTIONS = 30

TSNE_MAX = 2000

DEBUG=True
CONVERT_TO_OGG = False
USE_CHORD_LIST_AS_MID = True

def all_midi_files(root_dir):
    find_call = ["find", root_dir, "-name", '*.mid', "-type", "f" ]
    filename_list = subprocess.check_output(find_call).decode('utf-8').split("\n")[:-1]
    return filename_list

def attempt_textify(source_path):
    try:
        midi_str = midi_to_text.texify_song(midi_to_text.read_midi_file(source_path))
        return midi_str
    except TypeError as e:
        # log error in log file
        open(os.path.join(output_path,ERROR_LOG),'a').write("Exception {} encountered for filename {}".format(str(e),source_path))
        return None

def save_string(filename, string):
    with open(filename, 'w') as file:
        file.write(string)

def process_file(source_path,output_path):
    source_name = os.path.basename(source_path)
    dest_mid_filename = os.path.join(output_path,DOCUMENT_FILES,MIDI_FOLDER,source_name)
    dest_text_filename = os.path.join(output_path,DOCUMENT_FILES,MIDI_TEXT_FOLDER,source_name+".txt")
    dest_text_midi_filename = os.path.join(output_path,DOCUMENT_FILES,MIDI_TEXT_MIDI_FOLDER,source_name)
    dest_ogg_filename = os.path.join(output_path,DOCUMENT_FILES,MIDI_OGG_FOLDER,source_name+".ogg")

    midi_str = attempt_textify(source_path)
    if midi_str is None:
        return False

    save_string(dest_text_filename,midi_str)

    shutil.copyfile(source_path,dest_mid_filename)

    text_to_midi.song_convert(dest_text_filename,dest_text_midi_filename)

    if CONVERT_TO_OGG:
        src_mid_path = dest_text_midi_filename if USE_CHORD_LIST_AS_MID else source_path
        midi_to_ogg.midi_to_ogg(src_mid_path,dest_ogg_filename)

    return True

def process_file_sing(inp):
    return process_file(inp[0],inp[1])

def process_all_files(paths,output_path):
    if not DEBUG:
        pool = multiprocessing.Pool()
        input_tuples = [(p,output_path) for p in paths]

        pool.map(process_file_sing,input_tuples)
    else:
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
    make_dir_overwrite(os.path.join(output_path,DOCUMENT_FILES))
    make_dir_overwrite(os.path.join(output_path,WORD_FILES))
    make_dir_overwrite(os.path.join(output_path,DOCUMENT_FILES,MIDI_FOLDER))
    make_dir_overwrite(os.path.join(output_path,DOCUMENT_FILES,MIDI_TEXT_FOLDER))
    make_dir_overwrite(os.path.join(output_path,DOCUMENT_FILES,MIDI_TEXT_MIDI_FOLDER))
    make_dir_overwrite(os.path.join(output_path,DOCUMENT_FILES,MIDI_OGG_FOLDER))
    make_dir_overwrite(os.path.join(output_path,WORD_FILES,MIDI_FOLDER))
    make_dir_overwrite(os.path.join(output_path,WORD_FILES,MIDI_TEXT_FOLDER))
    make_dir_overwrite(os.path.join(output_path,WORD_FILES,MIDI_TEXT_MIDI_FOLDER))
    make_dir_overwrite(os.path.join(output_path,WORD_FILES,MIDI_OGG_FOLDER))

def build_cosine_dist_matrix(data):
    fdata = np.float32(data)
    fone = np.float32(1.0001)

    sqr_data = np.sqrt(np.sum(fdata*fdata,axis=1))

    top_data = np.stack(
        np.sum(fdata[i] * fdata,axis=1) for i in range(len(data))
    )
    bottom_data = np.reshape(sqr_data,(len(data),1)) * sqr_data.transpose()

    full_comp = fone-(top_data / bottom_data)

    return full_comp

def calc_tsne(data):
    import sys
    print("tsne started")
    cos_dist_matrix = build_cosine_dist_matrix(data)
    print(cos_dist_matrix.shape)
    sys.stdout.flush()
    #def cosine_d(d1,d2):
    #    return 1.0 - np.sum(d1*d2) / (math.sqrt(np.sum(d1*d1)) * math.sqrt(np.sum(d2*d2)))
    tsne = sklearn.manifold.TSNE(metric="precomputed")
    #print(data.shape)
    #exit(1)
    #distance_matrix = pairwise_distances(data, data, metric='cosine', n_jobs=1)
    transformed_data = tsne.fit_transform(cos_dist_matrix)
    print(transformed_data.shape)
    print("tsne ended")
    sys.stdout.flush()
    return transformed_data
    #print(data)

def associate_metadata(data_2d, associate_dataframe, actual_filenames):
    xvals,yvals = np.transpose(data_2d)
    val_dataframe = pandas.DataFrame(data={
        "filename":actual_filenames,
        "x":xvals,
        "y":yvals
    })
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

def process_word_data(all_words, word_vecs):
    filter_indicies = set(random.sample(range(len(all_words)),TSNE_MAX)) if len(all_words) > TSNE_MAX else range(len(all_words))

    filter_words = [word for i, word in enumerate(all_words) if i in filter_indicies]
    filter_vecs = [word for i, word in enumerate(word_vecs) if i in filter_indicies]

    filter_reprs = [chord_repr.chord_text_repr(w) for w in filter_words]

    tranformed_words = calc_tsne(filter_vecs)

    xvals,yvals = np.transpose(tranformed_words)
    val_dataframe = pandas.DataFrame(data={
        "chord_repr":filter_reprs,
        "chord":filter_words,
        "x":xvals,
        "y":yvals
    })
    return val_dataframe

def save_doc_data(output_path,doc_vecs,all_text_files):
    np.save(os.path.join(output_path,DOCUMENT_FILES,MIDI_VECTOR_LIST),doc_vecs)

    tranformed_data = calc_tsne(doc_vecs)

    out_dataframe = associate_metadata(tranformed_data,pandas.read_csv(args.file_associated_data),[s[:-4] for s in all_text_files])

    out_dataframe.to_csv(os.path.join(output_path,DOCUMENT_FILES,OUT_DATAFRAME),index=False)
    out_dataframe.to_json(os.path.join(output_path,DOCUMENT_FILES,OUT_JSON_VIEW),orient="records")

    shutil.copyfile("viewer/display_template.html",os.path.join(output_path,DOCUMENT_FILES,VIEWER_HTML))
    shutil.copyfile("viewer/template.js",os.path.join(output_path,DOCUMENT_FILES,VIEWER_JS))
    prepare_json_var(os.path.join(output_path,DOCUMENT_FILES,OUT_JSON_VIEW),os.path.join(output_path,DOCUMENT_FILES,VIEWER_JSON))

def process_word_file(output_path,word):
    dest_text_midi_filename = os.path.join(output_path,WORD_FILES,MIDI_TEXT_MIDI_FOLDER,word+".mid")
    dest_ogg_filename = os.path.join(output_path,WORD_FILES,MIDI_OGG_FOLDER,word+".ogg")

    text_to_midi.chord_to_midi(word,dest_text_midi_filename)

    #midi_to_ogg.midi_to_ogg(dest_text_midi_filename,dest_ogg_filename)


def save_word_data(output_path,unique_words,word_vecs):
    word_dframe = process_word_data(unique_words,word_vecs)

    word_dframe.to_csv(os.path.join(output_path,WORD_FILES,OUT_DATAFRAME),index=False)
    word_dframe.to_json(os.path.join(output_path,WORD_FILES,OUT_JSON_VIEW),orient="records")

    shutil.copyfile("viewer/word_display_template.html",os.path.join(output_path,WORD_FILES,VIEWER_HTML))
    shutil.copyfile("viewer/word_template.js",os.path.join(output_path,WORD_FILES,VIEWER_JS))
    prepare_json_var(os.path.join(output_path,WORD_FILES,OUT_JSON_VIEW),os.path.join(output_path,WORD_FILES,VIEWER_JSON))

    save_string(os.path.join(output_path,WORD_FILES,VEC_JSON),"var music_vectors = " + json.dumps(word_vecs.tolist()))

    for word in word_dframe['chord']:
        process_word_file(output_path,word)

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

    all_text_files = list(sorted(os.listdir(os.path.join(output_path,DOCUMENT_FILES,MIDI_TEXT_FOLDER))))

    all_text_paths = [os.path.join(output_path,DOCUMENT_FILES,MIDI_TEXT_FOLDER,name) for name in all_text_files]

    unique_words, word_vecs, doc_vecs = run_doc2vec_on_songs.run_doc2vec(all_text_paths,NUM_DIMENTIONS)

    #word_data = process_word_data(unique_words, word_vecs)

    save_doc_data(output_path,doc_vecs,all_text_files)
    save_word_data(output_path,unique_words,word_vecs)
