from gensim.test.utils import common_texts
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import subprocess
import numpy as np

def read_text_file(filename):
    with open(filename) as textfile:
        return textfile.read()

def get_filenames(base_path):
    command = 'find ../midi_dataset/ -name "*.mid"'
    filenames = subprocess.check_output(command,shell=True).split("\n")[:-1]
    return filenames

def get_tagged_docs(doc_filenames):
    docs = []
    for idx,name in enumerate(doc_filenames):
        word_list = read_text_file(name).split()
        docs.append(TaggedDocument(word_list,[(idx)]))
    return docs

def doc_count(docs):
    return sum(len(doc.words) for doc in docs)

def all_words(docs):
    words = {w for d in docs for w in d.words }
    return list(words)

def run_doc2vec(doc_filenames):
    docs = get_tagged_docs(doc_filenames)
    total_word_count = doc_count(docs)
    unique_word_list = all_words(docs)
    model = Doc2Vec(
            vector_size=6,
            window=5,# consider fiddling with this parameter
            min_count=1,
            workers=4,
            total_words=total_word_count,
            epochs=50)
    #model.build_vocab(docs)
    #model.train()

    model.build_vocab(docs)
    model.train(docs, total_examples=len(docs), epochs=50)

    #print("trained")
    #print(model.docvecs[0])
    #print(model.docvecs[1])
    #vecs = np.stack(model.infer_vector(doc.words) for doc in docs)
    #print(vecs)
    docvecs = np.stack([model.docvecs[i] for i in range(len(docs))])
    wordvecs = np.stack([model.wv[w] for w in unique_word_list])
    return unique_word_list,wordvecs,docvecs

def save_text(filename, text):
    with open(filename,'w') as tfile:
        tfile.write(text)

if __name__ == "__main__":
    filenames = get_filenames("../midi_dataset/")
    vecs = run_doc2vec(filenames)
    print(vecs)
    np.save("../midi_dataset/weights.npy",vecs)
    save_text("../midi_dataset/filenames.txt","\n".join(filenames))
