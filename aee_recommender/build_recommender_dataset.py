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


def main(fields,paper_wise= False):
    version = 7
    out_version = 7

    printed = False

    outfile = open(f"../data/aae_recommender_with_section_info_v{out_version}{'_papers' if paper_wise else ''}.jsonl", 'w')

    citing_papers = pickle.load(open(f"../data/citing_papers_v{version}.pickle",'rb'))

    candidate_papers = pickle.load(open(f"../data/candidate_papers_v{version}.pickle",'rb'))

    cit_count = 0
    cand_count = 0
    total_count = 0

    last_paper_id = None
    testing_paper_set = set()
    paper_ids_already_printed = []
    curr_paper = None
    with open(f"../data/citation_needed_data_contextualized_with_removal_v{version}_sorted.jsonl") as f:
        for idx, line in enumerate(tqdm(f, total=ESTIMATED_SEC_COUNT)):

            entry = json.loads(line.strip())
            
            if entry['paper_id'] not in citing_papers and entry['paper_id'] not in candidate_papers:
                # only use citing papers
                continue


            # skip empty sections of citing papers, there has to be at least one none empty section
            if entry['paper_id'] in citing_papers and len(entry['outgoing_citations_in_paragraph']) == 0:
                continue

            if entry['paper_id'] not in citing_papers:
                # only a candidate paper
                entry['outgoing_citations'] = []
                entry['outgoing_citations_in_paragraph'] = []

            # Additional flags for better debugging
            entry['is_citing_paper'] = True if entry['paper_id'] in citing_papers else False
            entry['is_candidate_paper'] = True if entry['paper_id'] in candidate_papers else False

            if entry['paper_id'] in citing_papers and int(entry['paper_year']) >= 2019:
                testing_paper_set.add(entry['paper_id'])

            #if entry['paper_id'] not in candidate_papers:
            #    # only a citing paper
            

            entry.pop('section_index', 'ignore')
            entry.pop('file_index', '')
            entry.pop('file_offset', '')
            entry.pop('original_text', '')
            entry.pop('samples', '')
            entry.pop('paper_abstract', '')

            debug_id = '83458577'
            if entry['paper_id'] == debug_id:
                print(entry)


            sec_title = entry['section_title']
            # append sections citations if section already occured
            if last_paper_id == entry['paper_id'] and sec_title in curr_paper.keys():
                curr_paper[sec_title]['outgoing_citations_in_paragraph'] = curr_paper[sec_title][
                                                                             'outgoing_citations_in_paragraph'] + entry[
                                                                             'outgoing_citations_in_paragraph']
            elif last_paper_id == entry['paper_id'] and len(entry['outgoing_citations_in_paragraph']) > 0:
                # we ony want to add sections which also have citation links
                # new section found
                curr_paper[sec_title] = entry
            else:
                # new paper print current paper
                # First Time is not initialized, but we do not want to print
                if last_paper_id is not None:

                    paper_fields = curr_paper[list(curr_paper.keys())[0]]['mag_field_of_study']
                    if fields in paper_fields and len(paper_fields) == 1:
                        if not printed:
                            print("Example entry:")
                            for sec in curr_paper.keys():
                                print(f"{json.dumps(curr_paper[sec])}")
                            printed = True

                        if last_paper_id in citing_papers:
                            cit_count += 1

                        if last_paper_id in candidate_papers:
                            cand_count += 1
                        total_count += 1

                        if paper_wise:
                            # only write once and use the outgoing_citations field for ref
                            first = list(curr_paper.keys())[0]
                            outfile.write(f"{json.dumps(curr_paper[first])}\n")
                        else:
                            for sec in curr_paper.keys():
                                outfile.write(f"{json.dumps(curr_paper[sec])}\n")
                    # paper_ids_already_printed.append(last_paper_id)
                last_paper_id = entry['paper_id']
                curr_paper = dict()
                curr_paper[sec_title] = entry
                

    outfile.close()
    print(f"Citing: {cit_count} and Candidate: {cand_count} papers")
    print(f"Total paper count: {total_count}")
    print(f"Testing paper count: {len(testing_paper_set)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--fields', default="Computer Science", help='fields which are going to be used')
    parser.add_argument('--paper_wise', default=False,action="store_true", help='fields which are going to be used')

    args = parser.parse_args()
    arguments = vars(args)
    main(arguments["fields"],arguments['paper_wise'])
