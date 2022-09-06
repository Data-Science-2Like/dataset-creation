# Create the Dataset for the Reranker module from our Modified S2ORC dataset

## Usage
You may place the Modified S2ORC dataset into the `../data_s2orc` directory.

There is no commandline interface provided.
Please, uncomment the respective method call at the bottom of the `reranker_dataset.py` file and set the parameters directly there.
The parameters of the methods are documented in the code. 

The resulting files of the S2ORC_Reranker dataset are output in this `dataset` directory.
For more information on the individual files, continue reading, please.

## Further Information
We generally only consider papers that uniquely belong to the field of "Computer Science" and where the year of publication is known.  
Furthermore, we remove any citation contexts belonging to the "Abstract" section as our structure analysis does not consider abstracts and usually there are no cite-worthy contexts in the abstract.  
Finally, the sentence needs to be cite-worthy and cite at least one of the considered papers in order to be added as a citation context in the dataset.

The resulting output files are:
- papers.jsonl
  - contains information about all papers (citing as well as cited papers in the dataset) 
- train_contexts.jsonl
  - contains all citation contexts (fulfilling the above criteria) of papers published until including `max_train_year`
- val_contexts.jsonl
  - contains all citation contexts (fulfilling the above criteria) of papers published after `max_train_year` until including `max_val_year`
- test_contexts.jsonl
  - contains all citation contexts (fulfilling the above criteria) of papers published after `max_val_year`
