from tqdm import tqdm
import time
from multiprocessing import Pool
import json
import argparse
import pickle

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

ESTIMATED_SEC_COUNT = 5567825


def main(fields):
    version = 5
    out_version = 5

    printed = False

    outfile = open(f"../data/pipeline_title_id_v{out_version}.json", 'w')

    citing_papers = pickle.load(open("../data/citing_paper.pickle",'rb'))

    candidate_papers = pickle.load(open("../data/candidate_papers.pickle",'rb'))

    title_to_id = dict()

    paper_ids_already_printed = []
    curr_paper = None
    with open(f"../data/citation_needed_data_contextualized_with_removal_v{version}_sorted.jsonl") as f:
        for idx, line in enumerate(tqdm(f, total=ESTIMATED_SEC_COUNT)):

            entry = json.loads(line.strip())
            if entry['paper_id'] not in citing_papers and entry['paper_id'] not in candidate_papers:
                continue
            title_to_id[entry['paper_title']] = entry['paper_id']


    json.dump(title_to_id,outfile)
    outfile.close()
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--fields', default="Computer Science", help='fields which are going to be used')

    args = parser.parse_args()
    arguments = vars(args)
    main(arguments["fields"])
