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


if __name__ == "__main__":

    version = 3
    
    paper_counts = {}
    paper_ids = {}
    total_paper_count = 0
    total_section_count = 0

    with open(f"../data/citation_needed_data_contextualized_with_removal_v{version}.jsonl") as f:

        for line in tqdm(f):
            entry = json.loads(line.strip())
            total_section_count += 1
            if entry['paper_id'] in paper_ids.keys():
                continue
            # Only count each paper once
            paper_ids[entry['paper_id']] = True

            total_paper_count += 1
            if entry['paper_year'] not in paper_counts.keys():
                paper_counts[entry['paper_year']] = 0
            paper_counts[entry['paper_year']] += 1


    years = []
    for y in paper_counts.keys():
        if y is not None:
            years.append(y)
    years.sort()

    for year in years:
        print(f"Year: {year} counts {paper_counts[year]} papers ")

    print(f"Total Paper Count: {total_paper_count}")
    print(f"Total Section Count: {total_section_count}")
