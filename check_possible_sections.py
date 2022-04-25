from tqdm import tqdm
import json
import gzip
import time
from multiprocessing import Pool
import scispacy
import spacy
nlp = spacy.load('en_core_sci_sm')
import re
import string
from collections import defaultdict
from pathlib import Path

data_loc = Path('../20200705v1/full/')

def get_permissible_title_list():
    with open('./permissible_section_titles.txt') as f:
        titles = [l.strip() for l in f]
    return titles


def extract_sections(pdf, permissible_titles):
    positive_sections = []
    negative_sections = []
    for j,pgr in enumerate(pdf['body_text']):
        if pgr['section'].lower() in permissible_titles and len(pgr['cite_spans']) > 0:
            positive_sections.append(pgr['section'].lower())
        elif pgr['section'].lower() not in permissible_titles and len(pgr['cite_spans']) > 0:
            negative_sections.append(pgr['section'].lower())
            
    return (positive_sections, negative_sections) 







def next_char_punctuation(text):
    """
    Determines if the next non-whitespace character is punctuation
    :param text:
    :return:
    """
    return re.search(f"^\s*[{string.punctuation}]", text) is not None

def dataset_worker(ab):
    dataset = []
    permissible_titles = get_permissible_title_list()
    with gzip.open(f"../filtered_metadata/metadata_{ab}.jsonl.gz") as f, \
         gzip.open(f"{data_loc}/pdf_parses/pdf_parses_{ab}.jsonl.gz") as g:
        for i, l in enumerate(f):
            metadata = json.loads(l.strip())
            #Seek to line in pdfs file
            g.seek(metadata['file_line_offset'])
            pdf = json.loads(g.readline())
            # Text indices are the indices into the "body_text" section of the parsed PDF json
            (poss, neg) = extract_sections(pdf, permissible_titles)
    return poss, neg


if __name__ == "__main__":
    # Get all of the statistics for venues, also time how long it takes to iterate through all the data
    start = time.time()
    pool = Pool(8)

    # with open(f"{data_loc}/citation_needed_data_v4.tsv", 'wt') as f:
    #     f.write("text\toriginal_citation\tlabel\n")
    version = 3
    completed = []
    run_list = [i for i in range(100) if i not in completed] # skip 12 since it never finishes
    print(f"{len(run_list)} files to go")

    f_run_list = list(filter(lambda n : Path(f"../filtered_metadata/metadata_{n}.jsonl.gz").exists(),run_list))
    print(f"{len(f_run_list)} files to go")
    for poss, neg in tqdm(pool.imap_unordered(dataset_worker, f_run_list), total=len(run_list)):
        # Mark it as completed first so we don't accidentally duplicate data
        with open(f'../data/positive_sections.txt', 'at+') as f:
            for record in poss:
                f.write(f"{record}\n")

        with open(f"../data/negative_sections.txt", 'at+') as f:
            for record in neg:
                f.write(f"{record}\n")

    pool.close()
    pool.join()
