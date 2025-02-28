## About The Project

This repository has the code for two Tabu search algorithms solving Maximum Diversity Problem.

* TS-MA for solving the MaxSum Diversity Problem by Atallah et al (2024)
* DropAddTS for solving the bi-level MaxSum Diversity Problem

Directory layout is as follow:

    .
    ├── create_matrix
    │   ├── foldseek.py          # Run foldseek to create structure similarity file
    │   └── needleall.py         # Run needleall to create sequence similarity files
    ├── MDP                      # Run TS-MA
    ├── MMDP                     # Run bi-level MMDP
    ├── test
    ├── Dockerfile               # Dockerfile for building image (Ignore for now!!!)
    ├── id_ed25519
    ├── init_head_mat.py         # Create matrix and heading files from similarity files
    ├── main.nf
    ├── main.py
    └── README.md

## What's new

MDP:
* Cleaned up non-essential scripts
* Fixed bug that returned error when selecting small subset (k<30)

MMDP:
* An alternative way of selecting diverse subset
* Combined MaxSum and MaxMin Diversity Problem models to overcome the bias towards closely related elements frequently encountered when using only MaxSum model
* Added subset expansion function for cases where more sequeneces need to be selected in the same dataset

## Prerequisites
Docker image is not built yet but will be updated.
Nextflow script is ready for use after installation.

## Getting Started

You can run the algorithm either with Nextflow or Python. The final outputs are a subset id file `.txt` and a histogram of the similarity distribution in the subset `.pdf`.

There are several ways to run the algorithm depending on what you have.

<b>Foldseek script workflow not yet tested so just a placeholder for now!!!</b>

If you prefer running each step individually, use Python:
* <b>Python</b>
    1. If you have sequence FASTA files, run
        ```ruby
        python create_matrix/needleall.py {YOUR_FASTA}
        ```
        to produce `identities.txt` and `similarities.txt`.
    2. If you have similarity files, create matrix and heading files by running
        ```ruby
        python init_head_mat.py {YOUR_SIMILARITY_FILE} {MEASURE_CODE}
        ```
        The measure code is 1 for sequence identity, 2 for sequence similarity, and 3 for structure similarity (TM scores). This step creates `.npy` and `.json` files.
    3. If you have the matrix and heading files ready, run
        ```ruby
        python main.py -hd {YOUR_HEADING_JSON} -d {YOUR_MATRIX_NPY} -k {SUBSET_SIZE} -m {MEASURE_CODE}
        ```
        This automatically run three solvers on the your files: TS-MA solving MaxSum problem, DropAddTS solving MaxMin problem, DropAddTS solving bi-level MaxSum problem.
    4. If you have got a subset selected, and you want to select more (e.g. 50) from the same dataset, run
        ```ruby
        python main.py -hd {YOUR_HEADING_JSON} -d {YOUR_MATRIX_NPY} -e {YOUR_SUBSET_FILE} -k 50 -m {MEASURE_CODE}
        ```
    * Options of main.py are
        ```ruby
        -hd HEADING, --heading HEADING
                                Path to the heading json file
        -d SIMILARITY, --similarity SIMILARITY
                                Path to the similarity npy file
        -e EXPAND, --expand EXPAND
                                Path to the subset id txt file
        -k SUBSET_SIZE, --subset_size SUBSET_SIZE
                                Subset size
        -s {0,1,2,3}, --solver {0,1,2,3}
                                Solver(s) to use (default: 0): 
                                0 - Solve all three problems
                                1 - MaxSum diversity problem 
                                2 - MaxMin diversity problem 
                                3 - Bi-level MaxSum diversity problem
        -m {0,1,2,3}, --measure {0,1,2,3}
                                Measure(s) to use (default: 0): 
                                0 - Use all three measures
                                1 - Sequence Pairwise Identity
                                2 - Sequence Pairwise Similarity
                                3 - Structural Similarity
        ```
Alternatively, you can use Nextflow to get to the final outputs straight away. All outputs will be stored in folders named after the time of execution `results_{yyyy_mm_dd_hh-mm-ss}`.
* <b>Nextflow</b>
    1. If you have sequence FASTA files, run
        ```ruby
        nextflow run main.nf --seqfile {YOUR_FASTA} --k {SUBSET_SIZE} --measure {MEASURE_CODE}
        ```
    2. If you have the matrix and heading files ready, run
        ```ruby
        nextflow run main.nf --head {YOUR_HEADING_JSON} --mat {YOUR_MATRIX_NPY} --k {SUBSET_SIZE} --measure {MEASURE_CODE}
        ```
    3. If you have got a subset selected, and you want to select more (e.g. 50) from the same dataset, run
        ```ruby
        nextflow run main.nf --head {YOUR_HEADING_JSON} --mat {YOUR_MATRIX_NPY} --idfile {YOUR_SUBSET_FILE} --k 50 --measure {MEASURE_CODE}
        ```

