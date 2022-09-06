from pathlib import Path
from tqdm import tqdm
import pickle
import json

citing_papers = set()
candidate_papers = set()

valid_papers = set()
valid_paper_years = dict()

min_year = 1964
max_year = 2020

ESTIMATED_SEC_COUNT = 5567825


def check_if_valid(current_paper, paper_id):
    if paper_id in valid_papers:
        # we don't want citations into the future
        if valid_paper_years[current_paper] < valid_paper_years[paper_id]:
            return False
        return True
    return False


def filter_full_dataset(path_to_file):
    max_paragraph_length = 0
    max_sentence_length = 0
    resolution = 50
    hist_len = 2050 // 50
    sent_hist = [0 for i in range(0,hist_len)]
    para_hist = [0 for i in range(0,hist_len)]
    with open(path_to_file) as data_file:

        # first filter for legitimate candidate and citing papers and remember ids
        for line in tqdm(data_file, total=ESTIMATED_SEC_COUNT):
            entry = json.loads(line)
            if len(entry['mag_field_of_study']) != 1:
                # we only consider entries where the field of study is unique
                continue
            if 'Computer Science' not in entry['mag_field_of_study']:
                # we only consider entries where on of the field of study is CS
                continue
            #if entry['section_title'].lower() == 'abstract':
                # we are not interested in the abstract section
                #continue
            if 'paper_year' not in entry.keys() or entry['paper_year'] is None:
                # we want the paper to have a year entry
                continue

            paper_year = int(entry['paper_year'])
            if min_year > paper_year or max_year < paper_year:
                # we want the paper to be in a specific date range
                continue

            valid_papers.add(entry['paper_id'])
            valid_paper_years[entry['paper_id']] = paper_year

        print(f"Found {len(valid_papers)} papers which meet our requirements")
        data_file.seek(0)
        for line in tqdm(data_file, total=ESTIMATED_SEC_COUNT):
            entry = json.loads(line)
            paper_id = entry['paper_id']
            if paper_id not in valid_papers:
                continue
            
            # fixate current paper year
            def check(check_id):
                return check_if_valid(paper_id,check_id)

            # remove now non valid citations
            entry['outgoing_citations'] = list(filter(check,entry['outgoing_citations']))
            entry['outgoing_citations_in_paragraph'] = list(filter(check,entry['outgoing_citations_in_paragraph']))
            
            # if there is at least one citation remaining this paper is also a citing paper
            if len(entry['outgoing_citations']) > 0 and valid_paper_years[paper_id] >= 2002:
                # we only need to add outgoing_citations, because candidate_papers is a set and
                # and outgoing_citations a superset of outgoing_citations_in_paragraph
                for id in entry['outgoing_citations']:
                    candidate_papers.add(id)
                # we only want citing papers beginning with the year 2002
                citing_papers.add(paper_id)

            for idx in range(0,len(entry['samples'])):
                if entry['samples'][idx]['ref_ids']:
                    entry['samples'][idx]['ref_ids'] = list(filter(check,entry['samples'][idx]['ref_ids']))

            tmp_max_par = len(entry['original_text'].split(' '))
            if max_paragraph_length < tmp_max_par:
                max_paragraph_length = tmp_max_par
            para_hist[tmp_max_par // resolution] += 1

            tmp_max_sent = max([len(x['original_text'].split(' ')) for x in entry['samples']])
            if max_sentence_length < tmp_max_sent:
                max_sentence_length = tmp_max_sent
            for sent in entry['samples']:
                sent_len = len(sent['original_text'].split(' '))
                sent_hist[sent_len // resolution] += 1

    print(f"Max sentence length: {max_sentence_length} words")
    print(f"Max paragraph length: {max_paragraph_length} words")

    print("Sentence Histogram")
    for idx, val in enumerate(sent_hist):
        print(f"{idx * resolution}: {val}")

    print("Paragraph Histogram")
    for idx, val in enumerate(para_hist):
        print(f"{idx * resolution}: {val}")

if __name__ == "__main__":
    in_version = 5
    out_version = 5
    
    in_path = f"../data/citation_needed_data_contextualized_with_removal_v{in_version}.jsonl"

    filter_full_dataset(in_path)








