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
ESTIMATED_SEC_COUNT = 5567825

if __name__ == "__main__":

    progress = True

    unconsistent_sections = 0

    unconsistent_sentences = 0
    total_sentences = 0

    version = 3

    iteration = 0
    seek_ptr = 0

    reached_eof = False

    pbar = tqdm(total=ESTIMATED_SEC_COUNT) if progress else None
    # only load part of file at a time
    while not reached_eof:
        data = list()
        with open(f"../data/citation_needed_data_contextualized_with_removal_v{version}.jsonl") as f:
            f.seek(seek_ptr)
            line = f.readline()
            i = 0
            while line:
                if i > READIN_ENTRIES:
                    seek_ptr = f.tell()
                    break
                data.append(json.loads(line.strip()))
                line = f.readline()
                i += 1

        if len(data) < READIN_ENTRIES:
            reached_eof = True

        for entry in data:
            is_consistent = True
            for sample in entry['samples']:
                if sample['label'] == 'check-worthy' and sample['label_cite'] == 'check-worthy':
                    total_sentences += 1
                    continue
                elif sample['label_cite'] == 'context-only' and sample['label'] == 'context-only':
                    total_sentences += 1
                    continue
                elif sample['label'] == 'context-only' and sample['label_cite'] != 'non-check-worthy':
                    total_sentences += 1
                    continue
                elif sample['label'] == 'non-check-worthy' and sample['label_cite'] == 'non-check-worthy':
                    total_sentences += 1
                    continue
                else:
                    print(f"label was {sample['label']} and label_cite was {sample['label_cite']}")
                    print(f"{json.dumps(sample)}\n")
                    unconsistent_sentences += 1
                    total_sentences += 1
                    is_consistent = False
                    continue
            if not is_consistent:
                unconsistent_sections += 1
            if progress:
                pbar.update(1)
        iteration += 1
    if progress:
        pbar.close()

    print(f"Unconsistent: {unconsistent_sections} / {ESTIMATED_SEC_COUNT} Percent: {unconsistent_sections/ ESTIMATED_SEC_COUNT}")
    print(f"Un. Sentences: {unconsistent_sentences} / {total_sentences} Percent: {unconsistent_sentences/total_sentences}")

