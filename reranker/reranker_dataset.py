import json
import pickle


def _check_causality_of_citations(path_to_papers_jsonl):
    paper_to = dict()
    with open(path_to_papers_jsonl, 'r') as papers_file:
        for line in papers_file:
            entry = json.loads(line)
            citing_id = entry["paper_id"]
            citing_year = entry["paper_year"]
            cited_ids = entry["outgoing_citations"]
            paper_to[citing_id] = {"year": citing_year, "cited_ids": cited_ids}

    for paper_id in paper_to.keys():
        citing_year = paper_to[paper_id]["year"]
        for cited_id in paper_to[paper_id]["cited_ids"]:
            cited_year = paper_to[cited_id]["year"]
            assert cited_year <= citing_year, paper_id


def _check_permissibility_of_data(entry):
    if len(entry["mag_field_of_study"]) != 1:
        # we only consider entries where the field of study is unique
        raise Exception("More than one mag_field_of_study!")
    if "Computer Science" not in entry["mag_field_of_study"]:
        # we only consider entries where one of the field of study is CS
        raise Exception("The mag_field_of_study is not Computer Science!")
    if entry["paper_year"] is None:
        # we need the year info in the Reranker later on and splits shall be the same for all modules
        raise Exception("The paper_year needs to be known.")


def _add_paper_to_file(json_entry, file, already_added_paper_ids, is_cited_paper=False):
    if json_entry["paper_id"] in already_added_paper_ids:
        # we have already added this paper
        return
    already_added_paper_ids.add(json_entry['paper_id'])
    paper_keys = ['paper_id', 'file_index', 'file_offset', 'mag_field_of_study', 'is_arxiv',
                  'paper_title', 'paper_abstract', 'paper_year', 'paper_authors', 'outgoing_citations']
    paper_entry = dict([(k, v) for k, v in json_entry.items() if k in paper_keys])
    paper_entry["is_cited_paper"] = is_cited_paper
    file.write(json.dumps(paper_entry) + '\n')


def _add_citation_contexts_to_file(json_entry, file, candidate_paper_ids=None):
    ref_ids_in_paragraph = set()
    paragraph_text = None
    sample_num = 0
    for sample in json_entry["samples"]:
        sample_num += 1
        if sample["label_cite"] != "check-worthy":
            # only cite-worthy sentences are citation contexts
            continue
        if candidate_paper_ids is None:
            ref_ids = sample["ref_ids"]
        else:
            ref_ids = [ref_id for ref_id in sample["ref_ids"] if ref_id in candidate_paper_ids]
        if not ref_ids:
            # only sentences citing at least one paper from the list of candidate papers are considered
            continue
        if paragraph_text is None:
            # create the text of the paragraph without citation markers
            paragraph_text = ""
            for s in json_entry["samples"]:
                paragraph_text += s["text"] + " "
            paragraph_text = paragraph_text[:-1]  # remove last whitespace
        context_entry = {
            "context_id": str(json_entry["paper_id"]) + '_' + str(json_entry["section_index"]) + '_' + str(sample_num),
            "paper_id": json_entry["paper_id"],
            "ref_ids": ref_ids,
            "citation_context": sample["text"],
            "text": paragraph_text.replace(sample["text"], "TARGETSENT"),
            "section_title": json_entry["section_title"]
        }
        ref_ids_in_paragraph.update(ref_ids)
        file.write(json.dumps(context_entry) + '\n')
    return ref_ids_in_paragraph


def create_contexts_files(path_to_s2orc_file, max_train_year, max_val_year, candidate_papers=None, citing_papers=None,
                          check_causality_of_citations_in_s2orc_file=False):
    if check_causality_of_citations_in_s2orc_file:
        print("check causality of citations in S2ORC file")
        _check_causality_of_citations(path_to_s2orc_file)
    citing_paper_ids = set()
    cited_paper_ids = set()

    with open(path_to_s2orc_file) as s2orc_file, \
            open('dataset/train_contexts.jsonl', 'w') as train_contexts_file, \
            open('dataset/val_contexts.jsonl', 'w') as val_contexts_file, \
            open('dataset/test_contexts.jsonl', 'w') as test_contexts_file:
        for i, line in enumerate(s2orc_file):
            if i % 100000 == 0:
                print(i)
            entry = json.loads(line)
            if citing_papers is not None and entry["paper_id"] not in citing_papers:
                # we do not consider this as a citing paper and hence the entry will not be part of the contexts
                continue
            if entry["section_title"].lower() == "abstract":
                # we are not interested in citation contexts from the Abstract section (not part of structure analysis and usually no cites)
                continue
            _check_permissibility_of_data(entry)
            paper_year = entry["paper_year"]
            if paper_year > max_val_year:
                # this is a test sample
                contexts_file = test_contexts_file
            elif paper_year > max_train_year:
                # this is a validation sample
                contexts_file = val_contexts_file
            else:
                # this is a training sample
                contexts_file = train_contexts_file
            added_ref_ids = _add_citation_contexts_to_file(entry, contexts_file, candidate_papers)
            if added_ref_ids:
                citing_paper_ids.add(entry["paper_id"])
                cited_paper_ids.update(added_ref_ids)

    with open('dataset/cited_paper_ids.pickle', 'wb') as f:
        pickle.dump(cited_paper_ids, f)
    with open('dataset/citing_paper_ids.pickle', 'wb') as f:
        pickle.dump(citing_paper_ids, f)
    return cited_paper_ids, citing_paper_ids


def create_papers_file(path_to_s2orc_file, cited_paper_ids=None, citing_paper_ids=None,
                       check_causality_of_citations_in_s2orc_file=False):
    if check_causality_of_citations_in_s2orc_file:
        print("check causality of citations in S2ORC file")
        _check_causality_of_citations(path_to_s2orc_file)

    added_paper_ids = set()
    with open(path_to_s2orc_file, 'r') as s2orc_file, \
            open('dataset/papers.jsonl', 'w') as papers_file:
        for i, line in enumerate(s2orc_file):
            if i % 100000 == 0:
                print(i)
            entry = json.loads(line)
            is_cited_paper = None
            if cited_paper_ids is None and citing_paper_ids is None:
                is_cited_paper = False
            elif cited_paper_ids is not None and entry["paper_id"] in cited_paper_ids:
                is_cited_paper = True
            elif citing_paper_ids is not None and entry["paper_id"] in citing_paper_ids:
                is_cited_paper = False
            if is_cited_paper is not None:
                _check_permissibility_of_data(entry)
                # ADD PAPER
                _add_paper_to_file(entry, papers_file, added_paper_ids, is_cited_paper=is_cited_paper)


def create_reranker_dataset(path_to_s2orc_file, max_train_year, max_val_year,
                            candidate_papers=None, citing_papers=None, check_causality_of_citations_in_s2orc_file=False):
    if check_causality_of_citations_in_s2orc_file:
        print("check causality of citations in S2ORC file")
        _check_causality_of_citations(path_to_s2orc_file)
    print("create contexts files")
    cited_paper_ids, citing_paper_ids = create_contexts_files(path_to_s2orc_file, max_train_year, max_val_year,
                                                              candidate_papers, citing_papers)
    print("creating papers file")
    create_papers_file(path_to_s2orc_file, cited_paper_ids, citing_paper_ids)


if __name__ == "__main__":
    # todo: uncomment the below call and set parameters as wished (-> creates papers and contexts files)
    # citing_papers = pickle.load(open('../data_s2orc/citing_papers_v6.pickle', 'rb'))
    # candidate_papers = pickle.load(open('../data_s2orc/candidate_papers_v6.pickle', 'rb'))
    # create_reranker_dataset('../data_s2orc/citation_needed_data_filtered_advanced_v6.jsonl', 2017, 2018,
    #                         candidate_papers, citing_papers, check_causality_of_citations_in_s2orc_file=True)

    # todo: uncomment the below call and set parameters as wished (-> creates only the contexts files)
    # citing_papers = pickle.load(open('../data_s2orc/citing_papers_v6.pickle', 'rb'))
    # candidate_papers = pickle.load(open('../data_s2orc/candidate_papers_v6.pickle', 'rb'))
    # create_contexts_files('../data_s2orc/citation_needed_data_filtered_advanced_v6.jsonl', 2017, 2018,
    #                       candidate_papers, citing_papers, check_causality_of_citations_in_s2orc_file=True)

    # todo: uncomment the below call and set parameters as wished (-> creates only the papers file)
    # citing_papers = pickle.load(open('dataset/citing_paper_ids.pickle', 'rb'))
    # cited_papers = pickle.load(open('dataset/cited_paper_ids.pickle', 'rb'))
    # create_papers_file('../data_s2orc/citation_needed_data_filtered_advanced_v6.jsonl',
    #                    cited_papers, citing_papers, check_causality_of_citations_in_s2orc_file=True)

    pass
