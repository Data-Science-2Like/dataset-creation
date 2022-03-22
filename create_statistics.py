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

    version = 3
    
    paper_counts = {}

    with open(f"../data/citation_needed_data_contextualized_with_removal_v{version}.jsonl") as f:

        for line in tqdm(f):
            entry = json.loads(line.strip())


            entry.pop('section_index','ignore')
            entry.pop('file_index','')
            entry.pop('file_offset','')
            entry.pop('mag_field_of_study','')
            entry.pop('original_text','')
            entry.pop('samples','')
            entry.pop('paper_abstract','')

            if entry['paper_year'] not in paper_counts.keys():
                entry['paper_year'] = 0
            entry['paper_year'] += 1


    for year in paper_counts.keys():
        print(f"Year: {year} counts {paper_counts[year]} papers ")

