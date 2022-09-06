# Create our Modified S2ORC Dataset

## Download the original S2ORC Dataset

First of all the s2orc dataset must be downloaded as described [here](https://github.com/allenai/s2orc).

## Execute the Preprocessing Pipeline

1. First of all `filter_papers_full.py` has to be executed. This prefilters and removes all s2orc entries that miss metadatfields that are needed for our datasets.

2. As the second script execute `get_filtered_pdf_line_offsets.py`. This aggregates the positions of the full text for the remaining papers.

3. Execute `build_dataset.py`. This extracts all citation context and their citing keys.

4. Execute `filter_for_years.py`. This will generate the final dataset file as well as the helper files `candidate_papers_vX.pickle` and `citing_papers_vX.pickle`.
   In this step we remove all papers that do not belong to only one domain, remove citations into the future and self citations, as well as citing papers before the year of 2002.
