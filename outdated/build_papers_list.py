from tqdm import tqdm
from pebble import ProcessPool
import json
from pathlib import Path
import gzip
import spacy
import re
import argparse

nlp = spacy.load('en_core_web_sm')

# taken from DualLCR preprocessing
def tokenize(text):
    doc = nlp(text)
    return [token.text.lower() for token in doc]


def tokenize_and_index(text, word2index, vocabulary, split_sentences=False):
    tokenids = []
    if split_sentences:
        doc = nlp(text)
        for sent in doc.sents:
            sent_tokens=[]
            for token in sent:
                t = token.text.lower()
                if t in vocabulary:
                    sent_tokens.append(word2index[t])
                else:
                    sent_tokens.append(word2index['UNK'])
            tokenids.append(sent_tokens)
    else:
        tokens = tokenize(text)
        for token in tokens:
            if token in vocabulary:
                tokenids.append(word2index[token])
            else:
                tokenids.append(word2index['UNK'])
    return tokenids

READIN_ENTRIES = 10000
ESTIMATED_SEC_COUNT 0 5567825


def main(args)

    word2index = {}
    c = 0
    # Generate vocabulary from tokens in the embeddings file

    print("Generating vocabulary")
    with open(args.embeddings_file) as f:
        next(f)  # skip the first line
        for line in f:
            word2index[line.split()[0]] = c
            c += 1
    vocabulary = set(list(word2index.keys()))

    version = 3

    papers = {}

    # collect paper information
    iteration = 0
    seek_ptr = 0

    reached_eof = False

    pbar = tqdm(total=ESTIMATED_SEC_COUNT)
    while not reached_eof:
        #only load part of file at a time

        data = list()
        with open(f"../data/citation_needed_data_contextualized_with_removal_v{version}.jsonl") as f:
            f.seek(seek_ptr)
            line = f.readline()
            i = 0
            while line:
                if i > READIN_ENTRIES:
                    seek_ptr = f.tell()
                    break
                data.append(json.loads(line.strip()))
                line = f.readline()
                i += 1

        if len(data) < READIN_ENTRIES:
            reached_eof = True

        with open(f"../data/reranker_papers_v{version}.json", 'a+') as f:
            for i, entry in enumerate(data):

                if entry['paper_id'] in papers:
                    pbar.update(1)
                    continue

                papers.add(entry['paper_id'])
                entry.pop('section_index','ignore')
                entry.pop('file_index','')
                entry.pop('file_offset','')
                entry.pop('original_text','')
                entry.pop('samples','')
                entry.pop('section_title','')
                entry.pop('outgoing_citations','')
                entry.pop('outgoing_citations_in_section','')
                entry['preprocessed_abstract'] = tokenize_and_index(entry['paper_abstract'], word2index, vocab, split_sentences=True)
                entry['preprocessed_title'] = tokenize_and_index(entry['paper_title', word2index, vocab)

                if iteration == 0 and i == 0:
                    print("Example entry:")
                    print(f"{entry['paper_id']} : {json.dumps(entry)},\n")

                f.write(f"{entry['paper_id']} : {json.dumps(entry)},\n")
                pbar.update(1)

            

        iteration += 1

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('embeddings_file', help='txt file with embeddings for tokens, used for determine vocabulary')

    args = parser.parse_args()

    main(args)
