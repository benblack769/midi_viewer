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
import json
from collections import Counter
import math
import random
import tempfile
import multiprocessing

DOCUMENT_FILES = "docs/"
WORD_FILES = "words/"
MIDI_FOLDER = "midi_files/"
MIDI_TEXT_FOLDER = "midi_text_files/"
MIDI_TEXT_MIDI_FOLDER = "midi_text_midi_files/"
MIDI_OGG_FOLDER = "midi_ogg_files/"
#FILENAME_LIST = "files.txt"
OUT_DATAFRAME = "all_data.csv"
OUT_JSON_VIEW = "all_data.json"
OUT_DATAFRAME_PART = "view_data.csv"
OUT_JSON_PART_VIEW = "view_data.json"
VIEWER_HTML = "display_template.html"
VIEWER_JS = "template.js"
VIEWER_JSON = "template_json.js"
VEC_JSON = "vec_json.json"
MIDI_VECTOR_LIST = "midi_vecs.npy"
ERROR_LOG = "errors.txt"

DEBUG=False
NUM_OUTPUT_DIMENTIONS = 30
MAX_WORDS_TO_DISPLAY = 2000

TEXTIFY_STRATEGY = "stack_ticks_into_chords_turn_off_when_channel_activates"

def all_midi_files(root_dir):
    find_call = ["find", root_dir, "-name", '*.mid', "-type", "f" ]
    filename_list = subprocess.check_output(find_call).decode('utf-8').split("\n")[:-1]
    return filename_list

def attempt_textify(source_path):
    try:
        midi_str = midi_to_text.texify_song(midi_to_text.read_midi_file(source_path),TEXTIFY_STRATEGY)
        return midi_str
    except TypeError as e:
        # log error in log file
        open(os.path.join(output_path,ERROR_LOG),'a').write("Exception {} encountered for filename {}".format(str(e),source_path))
        return None
    except AssertionError as e:
        # assertions are caught because python-midi raises some file input problems as assertions, instead of regular eerors!
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

    return True

def process_file_sing(inp):
    return process_file(inp[0],inp[1])

def process_all_files(paths,output_path):
    if DEBUG:
        for path in paths:
            process_file(path,output_path)
    else:
        zip_inputs = [(path,output_path) for path in paths]
        pool = multiprocessing.Pool()
        pool.map(process_file_sing,zip_inputs)

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

def process_all_word_data(all_words, word_vecs):
    all_reprs = [chord_repr.chord_text_repr(w) for w in all_words]
    val_dataframe = pandas.DataFrame(data={
        "chord_repr":all_reprs,
        "chord":all_words,
    })
    return val_dataframe

def process_view_word_data(all_words, word_vecs, count_stats):
    filter_words_counts = count_stats.most_common(MAX_WORDS_TO_DISPLAY)
    filter_words = {word for word,count in filter_words_counts}
    #filter_indicies = set(random.sample(range(len(all_words)),MAX_WORDS_TO_DISPLAY)) if len(all_words) > MAX_WORDS_TO_DISPLAY else range(len(all_words))

    filter_words = [word for word in all_words if word in filter_words]
    filter_indicies = [idx for idx,word in enumerate(all_words) if word in filter_words]
    filter_vecs = [vec for word,vec in zip(all_words,word_vecs) if word in filter_words]

    filter_reprs = [chord_repr.chord_text_repr(w) for w in filter_words]

    tranformed_words = calc_tsne(filter_vecs)

    xvals,yvals = np.transpose(tranformed_words)
    val_dataframe = pandas.DataFrame(data={
        "chord_repr":filter_reprs,
        "chord":filter_words,
        "idx":filter_indicies,
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
    shutil.copyfile("viewer/metricsgraphics.js",os.path.join(output_path,DOCUMENT_FILES,"metricsgraphics.js"))
    prepare_json_var(os.path.join(output_path,DOCUMENT_FILES,OUT_JSON_VIEW),os.path.join(output_path,DOCUMENT_FILES,VIEWER_JSON))

def process_word_file(output_path,word):
    dest_text_midi_filename = os.path.join(output_path,WORD_FILES,MIDI_TEXT_MIDI_FOLDER,word+".mid")
    dest_ogg_filename = os.path.join(output_path,WORD_FILES,MIDI_OGG_FOLDER,word+".ogg")

    text_to_midi.chord_to_midi(word,dest_text_midi_filename)

    #midi_to_ogg.midi_to_ogg(dest_text_midi_filename,dest_ogg_filename)

def round_list_lists(lls):
    return [[round(x,8) for x in l] for l in lls]

def filter_indicies(item_list,idicies):
    assert list(idicies) == sorted(idicies)
    idx_set = set(idicies)
    return [itm for idx,itm in enumerate(item_list) if idx in idx_set]

def save_word_data(output_path,unique_words,word_vecs,count_stats):
    np.save(os.path.join(output_path,WORD_FILES,MIDI_VECTOR_LIST),word_vecs)

    word_view_dframe = process_view_word_data(unique_words,word_vecs,count_stats)
    word_all_dframe = process_all_word_data(unique_words,word_vecs)

    word_all_dframe.to_csv(os.path.join(output_path,WORD_FILES,OUT_DATAFRAME),index=False)
    word_view_dframe.to_csv(os.path.join(output_path,WORD_FILES,OUT_DATAFRAME_PART),index=False)
    word_view_dframe.to_json(os.path.join(output_path,WORD_FILES,OUT_JSON_PART_VIEW),orient="records")
    #word_dframe.to_json(os.path.join(output_path,WORD_FILES,OUT_JSON_VIEW),orient="records")

    shutil.copyfile("viewer/word_display_template.html",os.path.join(output_path,WORD_FILES,VIEWER_HTML))
    shutil.copyfile("viewer/word_template.js",os.path.join(output_path,WORD_FILES,VIEWER_JS))
    shutil.copyfile("viewer/math_lib.js",os.path.join(output_path,WORD_FILES,"math_lib.js"))
    shutil.copyfile("viewer/metricsgraphics.js",os.path.join(output_path,WORD_FILES,"metricsgraphics.js"))
    prepare_json_var(os.path.join(output_path,WORD_FILES,OUT_JSON_PART_VIEW),os.path.join(output_path,WORD_FILES,VIEWER_JSON))

    view_word_vec_list = filter_indicies(word_vecs.tolist(),word_view_dframe.idx)
    save_string(os.path.join(output_path,WORD_FILES,VEC_JSON),json.dumps(round_list_lists(view_word_vec_list),separators=(',', ':')))
    #save_string(os.path.join(output_path,WORD_FILES,"arg.json"),json.dumps(round_list_lists(word_vecs),separators=(',', ':')))

    for word in word_view_dframe['chord']:
        process_word_file(output_path,word)

def get_word_count_stats(all_text_paths):
    full_word_list = (" ".join(read_file(fname) for fname in all_text_paths)).split()
    return Counter(full_word_list)

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

    count_stats = get_word_count_stats(all_text_paths)

    unique_words, word_vecs, doc_vecs = run_doc2vec_on_songs.run_doc2vec(all_text_paths,NUM_OUTPUT_DIMENTIONS)

    #word_data = process_word_data(unique_words, word_vecs)

    save_doc_data(output_path,doc_vecs,all_text_files)
    save_word_data(output_path,unique_words,word_vecs,count_stats)
