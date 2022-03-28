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
    

    estimated_sec_count = 5567825
    paper_counts = {}
    paper_ids = {}
    total_paper_count = 0
    total_section_count = 0
    paper_section_counts = {}
    paper_ids_per_year = {}

    with open(f"../data/citation_needed_data_contextualized_with_removal_v{version}.jsonl") as f:

        for line in tqdm(f, total=estimated_sec_count):
            entry = json.loads(line.strip())
            total_section_count += 1
            if entry['paper_id'] in paper_ids.keys():
                paper_section_counts[entry['paper_id']] += 1
                continue
            # Only count each paper once
            paper_ids[entry['paper_id']] = True

            total_paper_count += 1
            if entry['paper_year'] not in paper_counts.keys():
                paper_counts[entry['paper_year']] = 0
                paper_ids_per_year[entry['paper_year']] = []
            

            paper_ids_per_year[entry['paper_year']].append(entry['paper_id'])
            paper_section_counts[entry['paper_id']] = 1
            paper_counts[entry['paper_year']] += 1


    
    print("-"*67)

    years = []
    for y in paper_counts.keys():
        if y is not None:
            years.append(y)
    years.sort()

    for year in years:
        print("-"*67)
        print(f"Year: {year} counts {paper_counts[year]} papers ")
        year_section_count = 0
        for paper in paper_ids_per_year[year]:
            year_section_count += paper_section_counts[paper]
        avg_sec_count = year_section_count / len(paper_ids_per_year[year])
        print(f"Average section count: {avg_sec_count}")

    print(f"Total Paper Count: {total_paper_count}")
    print(f"Total Section Count: {total_section_count}")
