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

ESTIMATED_SEC_COUNT = 5567825

def main(fields):
    version = 3
    out_version = 4

    printed = False

    outfile = open(f"../data/aae_recommender_with_section_info_v{out_version}.jsonl", 'a+')

    last_paper_id = None
    last_section_title = None

    curr_entry = None
    with open(f"../data/citation_needed_data_contextualized_with_removal_v{version}_sorted.jsonl") as f:
        for idx,line in enumerate(tqdm(f,total=ESTIMATED_SEC_COUNT)):
            entry = json.loads(line.strip())

            entry.pop('section_index','ignore')
            entry.pop('file_index','')
            entry.pop('file_offset','')
            entry.pop('original_text','')
            entry.pop('samples','')
            entry.pop('paper_abstract','')


            # append sections citations
            if last_paper_id == entry['paper_id'] and last_section_title == entry['section_title']:
                curr_entry['outgoing_citations_in_section'] = curr_entry['outgoing_citations_in_section'] + entry['outgoing_citations_in_section']

            else:


                # First Time is not initialized, but we do not want to print
                if last_paper_id is not None:
                    if not printed:
                        print("Example entry:")
                        print(f"{json.dumps(curr_entry)}")
                        printed = True

                    if fields in curr_entry['mag_field_of_study']:
                        outfile.write(f"{json.dumps(curr_entry)}\n")
                last_paper_id = entry['paper_id']
                last_section_title = entry['section_title']
                
                curr_entry = entry

    outfile.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--fields', default="Computer Science", help='fields which are going to be used')

    args = parser.parse_args()
    arguments = vars(args)
    main(arguments["fields"])
