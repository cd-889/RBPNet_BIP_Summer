#!/bin/bash
#SBATCH --job-name=extract_windows
#SBATCH --account=cis250169
#SBATCH --partition=highmem
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=2:00:00
#SBATCH --mail-user=cdendhi@ucdavis.edu
#SBATCH --mail-type=BEGIN,END,FAIL,REQUEUE
#SBATCH --output=/anvil/scratch/x-cdendhi/BIP_Summer/RBPNet_window_extraction/logs/window_extract_%A_%a.out
#SBATCH --error=/anvil/scratch/x-cdendhi/BIP_Summer/RBPNet_window_extraction/logs/window_extract_%A_%a.err

OUTPUT_DIR="/anvil/scratch/x-cdendhi/BIP_Summer/RBPNet_window_extraction"
OUTPUT_FILE="${OUTPUT_DIR}/dataset_seqsizes.csv"

echo "RBP,train,valid,test" > "$OUTPUT_FILE"

for EXP in /anvil/scratch/x-cdendhi/BIP_Summer/RBPNet_lean_outputs/data_prep_outputs/*/; do
    NAME=$(basename "$EXP")

    if [ -f "${EXP}/size.csv" ]; then
        TRAIN=$(grep "^train," "${EXP}/size.csv" | cut -d',' -f2)
        VALID=$(grep "^valid," "${EXP}/size.csv" | cut -d',' -f2)
        TEST=$(grep "^test," "${EXP}/size.csv" | cut -d',' -f2)
 
        echo "${NAME},${TRAIN},${VALID},${TEST}" >> "$OUTPUT_FILE"
    fi
done

cat "$OUTPUT_FILE"