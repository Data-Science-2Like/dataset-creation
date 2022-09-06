from tqdm import tqdm
import time
from multiprocessing import Pool
import json
import argparse

# dataset.append({
#                         'paper_id': metadata['paper_id'],
#                         'section_index': index,
#                         'file_index': f"{ab}",
#                         'file_offset': metadata['file_line_offset'],
#                         'mag_field_of_study': metadata['mag_field_of_study'],
#                         'original_text': sec['text'],
#                         'section_title': sec['section'],
#                         'samples': final_samples,
#                         'paper_title' : metadata['title'],
#                         'paper_abstract' : metadata['abstract'],
#                         'paper_year' : metadata['year'],
#                         'outgoing_citations' : metadata['outbound_citations'],
#                         'outgoing_citations_in_section' : cits_in_section
#                     })

READIN_ENTRIES = 10000
ESTIMATED_SEC_COUNT = 5567825

def create_citeworth_split(val_year: int, test_year: int) -> None:

    version = 3

    seek_ptr = 0
    iteration = 0

    reached_eof = False
    pbar = tqdm(total=ESTIMATED_SEC_COUNT)

    # only load part of file at a time
    while not reached_eof:
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

        for entry in data:
            entry.pop('paper_title','')
            entry.pop('paper_abstract','')
            entry.pop('outgoing_citations','')
            entry.pop('outgoing_citations_in_section','')
            entry.pop('paper_authors','')

        if iteration == 0:
            print("Example entry:")
            print(f"{json.dumps(data[0])}")


        train_h = open(f"../data/citeworth_train_v{version}.json",'a+')
        val_h = open(f"../data/citeworth_val_v{version}.json",'a+')
        test_h = open(f"../data/citeworth_test_v{version}.json",'a+')

        for entry in data:
            year = -1
            if 'paper_year' in entry.keys() and entry['paper_year'] is not None:
                year = int(entry['paper_year'])
            entry.pop('paper_year')

            if year > 0:
                if year >= test_year:
                    test_h.write(f"{json.dumps(entry)}\n")
                elif year >= val_year:
                    val_h.write(f"{json.dumps(entry)}\n")
                else:
                    train_h.write(f"{json.dumps(entry)}\n")
            pbar.update(1)


        train_h.close()
        val_h.close()
        test_h.close()

        iteration += 1
    pbar.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--val', default=2018, help='year where the validation split begins')
    parser.add_argument('--test', default=2019, help='year where the test split begins')

    args = parser.parse_args()
    arguments = vars(args)
    create_citeworth_split(arguments["val"],arguments["test"])
