# RBPNet_BIP_Summer

This repository contains three sections: Modified Code (applies to the model), Analysis Code (extracting results & analysis) and Relevant Results. 

## Modified Code

- This includes two files
  - `validate.py` - This modification was made to remove code relating to the enrichment ratio filter. Credit: Claude
  - `prep_data.py` - This was modified to filter by read coverage and enrichment ratio. These are passed in as extra parameters that can be modified as needed.

## Results
- RBPNet Lean
  - Read coverage - All 100% windows to 70% windows (80%, 75% and 70% windows)
  - Enrichment Ratio Filter - Top 80% Windows

- RBPNet Transformer
  - Read coverage - All 100% windows to 70% windows (80%, 75% and 70% windows)
  - Transformer 12 Block Results - 44 RBPs

Both the lean and transformer (original) models for all windows are trained on all 57 RBPs in the `ENCORE_candidates.txt` file (provided by Chris). 

Note - Most of the 100% windows don't have training times, with the exception of few RBPs with the transformer model.  However, the training was done across both the Anvil and Hive clusters. Therefore, direct comparison to other window sizes is not possible as all other transformer models for reduced window sizes were done strictly on Hive.

The lean and transformer (original) models for all other window sizes are trained on 40 RBPs. 

Results are formatted with RBP name, index, crosslinking correlation (mean_profile_pearson) and training times in minutes for 80%, 75% and 70% windows. The lean and transformer model with all 100% windows are only reported with the crosslinking correlation. 

- Window splits across training, testing and validation (for all 100% windows)
  - `dataset_seqsizes.csv` - contains how many windows training, testing and validation contain. 


## Results Analysis Code
- Includes two files
  - `extract_results.py` - Extracts training times for each RBP through training log files and metrics through the validation metrics files. Includes index of each RBP and verification for any RBP mismatch between selected file and the RBP it corresponds to. Reports how many metrics and log files were not found, across the 57 RBPs. 
  - `extract_windows.sh` - Extracts the amount of windows for each RBP after data preparation across training, testing and validation subsets. This is done by looking through the sizes.csv file generated for each RBP after data preparation.
 


