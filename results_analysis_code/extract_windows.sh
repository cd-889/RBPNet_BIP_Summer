#!/bin/bash
#SBATCH --job-name=extract_windows
#SBATCH --account=cis250169
#SBATCH --partition=highmem
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=2:00:00
#SBATCH --mail-user=your_email@gmail.com
#SBATCH --mail-type=BEGIN,END,FAIL,REQUEUE
#SBATCH --output=/path/to/your/out/log/out_%A_%a.out
#SBATCH --error=/path/to/your/err/log/err_%A_%a.err

OUTPUT_DIR="/path/to/your/output/directory"
OUTPUT_FILE="${OUTPUT_DIR}/dataset_seqsizes.csv"

echo "RBP,train,valid,test" > "$OUTPUT_FILE"

for EXP in /path/to/your/data_prep_outputs/*/; do
    NAME=$(basename "$EXP")

    if [ -f "${EXP}/size.csv" ]; then
        TRAIN=$(grep "^train," "${EXP}/size.csv" | cut -d',' -f2)
        VALID=$(grep "^valid," "${EXP}/size.csv" | cut -d',' -f2)
        TEST=$(grep "^test," "${EXP}/size.csv" | cut -d',' -f2)
 
        echo "${NAME},${TRAIN},${VALID},${TEST}" >> "$OUTPUT_FILE"
    fi
done

cat "$OUTPUT_FILE"
