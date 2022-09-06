# Create the Dataset for the CiteWorth module from our Modified S2ORC dataset

## Usage
You may place the Modified S2ORC dataset into the `../data_s2orc` directory.

There is no commandline interface provided.
Please, uncomment the method call at the bottom of the `citeworth_dataset.py` file and set the respective parameters directly there.
The parameters of the `create_citeworth_dataset` method are documented in the code. 

The resulting files of the S2ORC_CiteWorth dataset are output in this `dataset` directory.
For more information on the individual files, continue reading, please.

## Further Information
We generally only consider papers that uniquely belong to the field of "Computer Science" and where the year of publication is known.  
Furthermore, we remove any entries belonging to the "Abstract" section as our structure analysis does not consider abstracts and usually there are no cite-worthy sentences in the abstract.  
Finally, it needs to be known for every sentence in a paragraph whether it is cite-worthy or not in order for the paragraph to be considered in the dataset.

The resulting output files are:
- train.jsonl
  - contains all paragraphs of papers published until including `max_train_year`
  - and only those where every sentence in the paragraph conforms to the conditions defined in [[1](#1)]
- val.jsonl
  - contains all paragraphs of papers published after `max_train_year` until including `max_val_year`
  - and only those where every sentence in the paragraph conforms to the conditions defined in [[1](#1)]
- test.jsonl
  - contains all paragraphs of papers published after `max_val_year`
- test_conform.jsonl
  - contains all paragraphs of papers published after `max_val_year`
  - and only those where every sentence in the paragraph conforms to the conditions defined in [[1](#1)]
- test_non_conform.jsonl
  - contains all paragraphs of papers published after `max_val_year`
  - and only those where every sentence in the paragraph does not conform to the conditions defined in [[1](#1)]

## References
<a id="1">[1]</a> 
Dustin Wright and Isabelle Augenstein. 2021. CiteWorth: Cite-Worthiness Detection for Improved Scientific Document Understanding. In Findings of the Association for Computational Linguistics: ACL-IJCNLP 2021. Association for Computational Linguistics, Online, 1796–1807. https://doi.org/10.18653/v1/2021.findings-acl.157