# Create the Dataset for the AAE_Recommender / Prefetcher module from our Modified S2ORC dataset

## Usage

```
python build_recommender_dataset.py [--fields FIELD --paper_wise]
```

The preprocessed data from the Modified S2ORC dataset has to be placed in the `../data` directory.
The output files are also going to be generated there. If you paths differ, adjust accordingly.
Make sure the correct version is selected in the code.

When supplying `--fields` another part of the S2ORC dataset can be selected.
When supplying `--paper_wise` a dataset entry is created for each paper. The standard behavior is to create a entry for each section in a paper.
