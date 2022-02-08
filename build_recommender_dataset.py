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

READIN_ENTRIES = 2000

if __name__ == "__main__":

    version = 1

    iteration = 0

    data = list()

    reached_eof = False

    # only load part of file at a time
    while not reached_eof:
        with open(f"../data/citation_needed_data_contextualized_with_removal_v{version}.jsonl") as f:

            for i in range(iteration * READIN_ENTRIES):
                next(f)
            for l in [next(f) for i in range(READIN_ENTRIES)]:
                data.append(json.loads(l.strip()))

        print(f"Loaded {len(data)} entries")

        if len(data) < READIN_ENTRIES:
            reached_eof = True

        for entry in tqdm(data):
            del entry['section_index']
            del entry['file_index']
            del entry['file_offset']
            del entry['mag_field_of_study']
            del entry['original_text']
            del entry['samples']
            del entry['paper_abstract']

        if iteration == 0:
            print("Example entry:")
            print(f"{json.dumps(data[0])}")

        with open(f"../data/aae_recommender_with_section_info_v{version}.jsonl", 'a+') as f:
            for entry in data:
                f.write(f"{json.dumps(entry)}\n")

        iteration += 1
