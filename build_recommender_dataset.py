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

def read_only_lines(f, start, finish):
    for ii, line in enumerate(f):
        if ii>= start and ii < finish:
            yield line
        elif ii>= finish:
            return

if __name__ == "__main__":

    version = 1

    iteration = 0

    reached_eof = False

    # only load part of file at a time
    while not reached_eof:
        data = list()
        with open(f"../data/citation_needed_data_contextualized_with_removal_v{version}.jsonl") as f:

            #for i in range(iteration * READIN_ENTRIES):
            #    next(f)
            #for l in [next(f) for i in range(READIN_ENTRIES)]:
            #    data.append(json.loads(l.strip()))
            for l in read_only_lines(f,iteration * READIN_ENTRIES, (iteration + 1) * READIN_ENTRIES):
                data.append(json.loads(l.strip()))

        print(f"Loaded {len(data)} entries")

        if len(data) < READIN_ENTRIES:
            reached_eof = True

        for entry in tqdm(data):
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

        iteration += 1
