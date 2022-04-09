from tqdm import tqdm
import time
from multiprocessing import Pool
import json

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

if __name__ == "__main__":

    version = 3

    iteration = 0
    seek_ptr = 0

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
            entry.pop('section_index','ignore')
            entry.pop('file_index','')
            entry.pop('file_offset','')
            entry.pop('mag_field_of_study','')
            entry.pop('original_text','')
            entry.pop('samples','')
            entry.pop('paper_abstract','')

        if iteration == 0:
            print("Example entry:")
            print(f"{json.dumps(data[0])}")

        with open(f"../data/aae_recommender_with_section_info_v{version}.jsonl", 'a+') as f:
            for entry in data:
                f.write(f"{json.dumps(entry)}\n")
                pbar.update(1)

        iteration += 1
    pbar.close()
