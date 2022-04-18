import json


def _check_consistency_of_data(json_entry):
    for sample in json_entry["samples"]:
        if sample["label_cite"] == "context-only":
            assert sample["label"] == "context-only", json_entry
        elif sample["label_cite"] == "non-check-worthy":
            assert sample["label"] == "non-check-worthy", json_entry
        elif sample["label_cite"] == "check-worthy":
            assert sample["label"] == "check-worthy" or sample["label"] == "context-only", json_entry


def _is_every_sample_valid(json_entry):
    for sample in json_entry["samples"]:
        if sample["label_cite"] == "context-only":
            # parsing issue
            return False
    return True


def _is_every_sample_conform(json_entry):
    for sample in json_entry["samples"]:
        if sample["label_cite"] == "context-only":
            # parsing issue
            return False
        if sample["label"] == "context-only":
            # not conform for citeworth
            return False
    return True


def _is_every_sample_non_conform(json_entry):
    for sample in json_entry["samples"]:
        if sample["label_cite"] == "context-only":
            # parsing issue
            return False
        if sample["label"] == "check-worthy":
            # conform for citeworth
            return False
    return True


def create_citeworth_dataset(path_to_s2orc_file, max_train_year, max_val_year, check_consistency_of_data=False):
    with open(path_to_s2orc_file) as s2orc_file, \
            open('dataset/train.jsonl', 'w') as train_file, \
            open('dataset/val.jsonl', 'w') as val_file, \
            open('dataset/test.jsonl', 'w') as test_file, \
            open('dataset/test_conform.jsonl', 'w') as test_conform_file, \
            open('dataset/test_non_conform.jsonl', 'w') as test_non_conform_file:
        for i, line in enumerate(s2orc_file):
            if i % 100000 == 0:
                print(i)
            entry = json.loads(line)
            if check_consistency_of_data:
                _check_consistency_of_data(entry)
            if len(entry["mag_field_of_study"]) != 1:
                # we only consider entries where the field of study is unique
                continue
            if "Computer Science" not in entry["mag_field_of_study"]:
                # we only consider entries where one of the field of study is CS
                continue
            if entry["section_title"].lower() == "abstract":
                # we are not interested in the Abstract section (not part of structure analysis and usually no cites)
                continue
            paper_year = entry["paper_year"]
            if paper_year is None:
                # we need the year info in the Reranker later on and splits shall be the same for all modules
                continue
            if not _is_every_sample_valid(entry):
                # we do not want to have invalid samples in our dataset
                continue
            if paper_year > max_val_year:
                # this is a test sample
                test_file.write(line.replace('"label": "context-only"', '"label": "check-worthy"'))
                if _is_every_sample_conform(entry):
                    test_conform_file.write(line)
                elif _is_every_sample_non_conform(entry):
                    test_non_conform_file.write(line.replace('"label": "context-only"', '"label": "check-worthy"'))
            elif paper_year > max_train_year:
                # this is a validation sample
                if _is_every_sample_conform(entry):
                    val_file.write(line)
            else:
                # this is a training sample
                if _is_every_sample_conform(entry):
                    train_file.write(line)


if __name__ == "__main__":
    # todo: uncomment the below call and set parameters as wished
    # create_citeworth_dataset('../data_s2orc/citation_needed_data_contextualized_with_removal_v3.jsonl', 2017, 2018)
    pass
