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

    # paper_ids_already_printed = []

    curr_paper = None
    with open(f"../data/citation_needed_data_contextualized_with_removal_v{version}_sorted.jsonl") as f:
        for idx, line in enumerate(tqdm(f, total=ESTIMATED_SEC_COUNT)):

            entry = json.loads(line.strip())
            # consistency check to see if paper is really sorted
            # if entry['paper_id'] in paper_ids_already_printed:
            #    raise ValueError('Input file is not sorted')
            # consistency check makes things to slow

            if len(entry['mag_field_of_study']) != 1:
                # we only consider entries where the field of study is unique
                continue
            if entry['section_title'].lower() == 'abstract':
                # we are not interested in the Abstract section (not part of structure analysis and usually no cites)
                continue
            if fields not in entry['mag_field_of_study']:
                # we only consider entries where one of the field of study is CS
                continue

            paper_year = entry["paper_year"]
            if paper_year is None:
                # we need the year info in the Reranker later on and splits shall be the same for all modules
                continue

            entry.pop('section_index', 'ignore')
            entry.pop('file_index', '')
            entry.pop('file_offset', '')
            entry.pop('original_text', '')
            entry.pop('samples', '')
            entry.pop('paper_abstract', '')

            sec_title = entry['section_title']
            # append sections citations if section already occured
            if last_paper_id == entry['paper_id'] and sec_title in curr_paper.keys():
                curr_paper[sec_title]['outgoing_citations_in_section'] = curr_paper[sec_title][
                                                                             'outgoing_citations_in_section'] + entry[
                                                                             'outgoing_citations_in_section']
            elif last_paper_id == entry['paper_id']:
                # new section found
                curr_paper[sec_title] = entry
            else:
                # new paper print current paper
                # First Time is not initialized, but we do not want to print
                if last_paper_id is not None:
                    if not printed:
                        print("Example entry:")
                        for sec in curr_paper.keys():
                            print(f"{json.dumps(curr_paper[sec])}")
                        printed = True

                    for sec in curr_paper.keys():
                        outfile.write(f"{json.dumps(curr_paper[sec])}\n")
                    # paper_ids_already_printed.append(last_paper_id)
                last_paper_id = entry['paper_id']
                curr_paper = dict()
                curr_paper[sec_title] = entry

    outfile.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--fields', default="Computer Science", help='fields which are going to be used')

    args = parser.parse_args()
    arguments = vars(args)
    main(arguments["fields"])
