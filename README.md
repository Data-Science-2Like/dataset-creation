# dataset-creation

Code for the dataset creation of the [SCOPE Pipeline](https://github.com/Data-Science-2Like/SCOPE).
The initial code was taken from [CiteWorth](https://github.com/copenlu/cite-worth).
The repo is needed to create our Modified [S2ORC](https://github.com/allenai/s2orc) variant for each of the three individual modules.

## Folder Structure
    ├── common                                # Code shared by all modules. See README for more info.
	├── citeworth                             # Code to generate the dataset for the Citeworth module.
	├── reranker                              # Code to generate the dataset for the Reranker module.
	├── aae_recommender                       # Code to generate the dataset for the AAE-Recommender module.
	├── outdated                              # Can be ignored
	├── auxilary                              # Additional scripts to check consistency, generate plots etc.
	
	
## Usage

First of all the scripts in the `common` subfolder have to be executed. See the README for additional info.
Then depending on the wanted submodule the code in the corresponding subfolder has to be executed.

### AAE-Recommender

For creating the S2ORC_Recommender dataset from our Modified S2ORC dataset use the code in the `aae_recommender` subdirectory.
A README for additional info is included.

### S2ORC_CiteWorth and S2ORC_Reranker datasets
For creating the S2ORC_CiteWorth and S2ORC_Reranker datasets from our Modified S2ORC dataset, have a look into the `citeworth` and `reranker` directory, respectively.
There is a README with more details in each of them.

