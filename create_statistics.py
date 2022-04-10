from tqdm import tqdm
import time
from multiprocessing import Pool
import json
from statistics import mean
from pathlib import Path
from pebble import concurrent, ProcessPool, ProcessExpired
import gzip

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

FINE_GRAINED_LABELS = {
     "introduction": 1, # Intro
     "abstract": 2, # Abstract
     "method": 3, # Methods
     "methods": 3, # Methods
     "results": 4, # Results
     "discussion": 5, # Discussion
     "discussions": 5, # Discussion
     "conclusion": 6, # Conclusion
     "conclusions": 6, # Conclusion
     "results and discussion": 5, # Discussion
     "related work": 7, # Background
     "experimental results": 4, # Results
     "literature review": 7, # Background
     "experiments": 4, # Results
     "background": 7, # Background
     "methodology": 3, # Methods
     "conclusions and future work": 6, # Conclusion
     "related works": 7, # Background
     "limitations": 5, # Discussion
     "procedure": 3, # Methods
     "material and methods": 3, # Methods
     "discussion and conclusion": 5, # Discussion
     "implementation": 3, # Methods
     "evaluation": 4, # Results
     "performance evaluation": 4, # Results
     "experiments and results": 4, # Results
     "overview": 1, # Introduction
     "experimental design": 3, # Methods
     "discussion and conclusions": 5, # Discussion
     "results and discussions": 5, # Discussion
     "motivation": 1, # Introduction
     "proposed method": 3, # Methods
     "analysis": 4, # Results
     "future work": 6, # Conclusion
     "results and analysis": 4, # Results
     "implementation details": 3 # Methods 
}

SYNONYMS_PARSER = {
    "abstract" : "abstract",
    "introduction": "introduction",
    "intro": "introduction",
    "overview": "introduction",
    "motivation": "introduction",
    "problem motivation": "introduction",
    "related work": "related work",
    "related works": "related work",
    "previous work": "related work",
    "literature": "related work",
    "background": "related work",
    "literature review": "related work",
    "state of the art": "related work",
    "current state of research": "related work",
    "requirement": "related work",
    "theory basics": "theory basics",
    "techniques": "techniques",
    "experiment": "experiment",
    "experiments" : "experiment",
    "experiments and results": "experiment",
    "experimental result": "experiment",
    "experimental results": "experiment",
    "experimental setup": "experiment",
    "result": "experiment",
    "results" : "experiment",
    "evaluation": "experiment",
    "performance evaluation": "experiment",
    "experiment and result": "experiment",
    "analysis": "experiment",
    "methodology": "method",
    "method": "method",
    "methods": "method",
    "material and method": "method",
    "material and methods": "method",
    "proposed method": "method",
    "evaluation methodology": "method",
    "procedure": "method",
    "implementation": "method",
    "experimental design": "method",
    "implementation detail": "method",
    "implementation details": "method",
    "system model": "method",
    "definition": "definition",
    "data set": "data set",
    "solution": "solution",
    "discussion": "discussion",
    "discussions" : "discussion",
    "limitation": "discussion",
    "limitations" : "discussion",
    "discussion and conclusion": "discussion",
    "discussion and conclusions" : "discussion",
    "result and discussion": "discussion",
    "results and discussion": "discussion",
    "results and discussions": "discussion",
    "results and analysis": "discussion",
    "future work": "conclusion",
    "conclusion": "conclusion",
    "conclusions" : "conclusion",
    "summary": "conclusion",
    "conclusion and outlook": "conclusion",
    "conclusion and future work": "conclusion",
    "conclusions and future work": "conclusion",
    "concluding remark": "conclusion"
}

NUM_TO_SEC = ["None","Introduction","Abstract","Methods","Results","Discussion","Conclusion", "Background"]


def get_mapping(query: str) -> str:

    # find out missing labels
    #for key in FINE_GRAINED_LABELS.keys():
    #    if key not in SYNONYMS_PARSER.keys():
    #        print(key)
    #raise ValueError()
    #return NUM_TO_SEC[FINE_GRAINED_LABELS[query]]
    return SYNONYMS_PARSER[query]


def get_permissible_title_list():
    with open('./permissible_section_titles.txt') as f:
        titles = [l.strip() for l in f]
    return titles

def calc_avg(old_v, old_w, new_v, new_w = 1):
    return (old_v * old_w + new_v * new_w) / (old_w + new_w)



def get_years(ab):
    p_years = {}
    
    with gzip.open(ab) as f:
        for l in f:
            entry = json.loads(l.strip())
            p_years[entry['paper_id']] = entry['year']

    return p_years

if __name__ == "__main__":

    version = 3
    

    estimated_sec_count = 5567825
    paper_years = {}
    paper_counts = {}
    paper_ids = {}
    total_paper_count = 0
    total_section_count = 0
    paper_section_counts = {}
    paper_ids_per_year = {}

    sec_stats = {}

    data_loc = Path('../20200705v1/full/')

    files = [f for f in data_loc.glob(f"metadata/*.gz")]
    with ProcessPool() as pool:
        future = pool.map(get_years, files, timeout =300)
        print("Collecting paper years")

        iterator = future.result()
        with tqdm(total=100) as pbar:
            while True:
                try:
                    result = next(iterator)
                    paper_years.update(result)

                    pbar.update(1)
                except StopIteration:
                    break
                except Exception as error:
                    print(error.traceback)

    print(f"Found {len(paper_years)} paper")
    print("Collecting statistics")
    with open(f"../data/citation_needed_data_contextualized_with_removal_v{version}.jsonl") as f:
        for line in tqdm(f, total=estimated_sec_count):
            entry = json.loads(line.strip())
            total_section_count += 1
            if entry['paper_id'] in paper_ids.keys():
                paper_section_counts[entry['paper_id']] += 1

                # collecting information abount average cits in sections and their age

                st = get_mapping(entry['section_title'].lower())
                if st not in sec_stats.keys():
                    sec_stats[st] = {}
                    sec_stats[st]['avg_count'] = 0
                    sec_stats[st]['avg_age'] = 0
                    sec_stats[st]['weight'] = 0

                cit_count = len(list(filter(lambda s : s['label'] == 'check-worthy',entry['samples']))) / len(entry['samples'])

                years = []
                for s in entry['samples']:
                    if 'ref_ids' in s.keys() and s['ref_ids'] is not None and len(s['ref_ids']) > 0:
                        for id in s['ref_ids']:
                            if id is not None and paper_years[id] is not None and entry['paper_year'] is not None:
                                years.append(entry['paper_year'] - paper_years[id])

                # avg_age = mean([entry['paper_year'] - paper_years[id] for s in entry['samples'] for id in s['ref_ids']])
                avg_age = mean(years) if len(years) > 0 else 0
                ow = sec_stats[st]['weight']
                sec_stats[st]['avg_count'] = calc_avg(sec_stats[st]['avg_count'],ow, cit_count)
                sec_stats[st]['avg_age'] = calc_avg(sec_stats[st]['avg_age'], ow, avg_age)
                sec_stats[st]['weight'] += 1

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

    print("-"*67)

    for section in sec_stats.keys():
        print(f"Section {section}: Avg Count: {sec_stats[section]['avg_count']} Avg Age: {sec_stats[section]['avg_age']}, Weight: {sec_stats[section]['weight']}")
