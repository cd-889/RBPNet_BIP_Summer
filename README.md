# RBPNet_BIP_Summer

## Modified Code

- This includes two files
  - validate.py - This modification was made to remove code relating to the enrichment ratio filter. Credit: Claude
  - prep_data.py - This was modified to filter by read coverage and enrichment ratio. These are passed in as extra parameters that can be modified as needed.

## Results
- RBPNet Lean
  - Read coverage - All 100% windows to 70% windows
  - Enrichment Ratio Filter - Top 80% Windows

- RBPNet Transformer
  - Read coverage - All 100% windows to 70% windows
  - Transformer 12 Block Results - 44 RBPs

Both the lean and transformer (original) models for all windows are trained on all 57 RBPs in the `ENCORE_candidates.txt` file (provided by Chris).

Note - the 100% windows don't have training times and the RBPs that do have them are not accurate. Therefore, direct comparison to other window sizes is not possible.

The lean and transformer (original) models for all other window sizes is trained on 40 RBPs. 

- Window splits across training, testing and validation (for all 100% windows)
  - dataset_seqsizes.csv - contains how many windows training, testing and validation contain. 


## Results Analysis Code
- Includes two files
  - extract_results.py - Extracts training times for each RBP through training log files and metrics through the validation metrics files. Includes index of each RBP and verification for any RBP mismatch between selected file and the RBP it corresponds to. Reports how many metrics and log files were not found, across the 57 RBPs. 
  - extract_windows.sh - Extracts the amount of windows for each RBP after data preparation across training, testing and validation subsets. This is done by looking through the sizes.csv file generated for each RBP after data preparation. 



