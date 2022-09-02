# dataset-creation



## Usage

First of all the s2orc dataset must be downloaded as described [here](https://github.com/allenai/s2orc).
Second the script `filter_papers_full.py` and `get_filtered_pdf_line_offsets.py` must be run.
They are taken from [CiteWorth](https://github.com/copenlu/cite-worth).

`build_dataset.py` generates the full dataset and extracts citation contexts.

`create_statistics.py` calculates statistics containing the average age of citations in a given section and the average amount of citation in a given section.

### S2ORC_CiteWorth and S2ORC_Reranker datasets
For creating the S2ORC_CiteWorth and S2ORC_Reranker datasets from our Modified S2ORC dataset, have a look into the `citeworth` and `reranker` directory, respectively.
There is a README with more details in each of them.
