"""
Extracts, per RBP:
  - mean profile_pearson(total>50)  from test_data_metric.csv
  - training runtime                from the corresponding .out log
Cross-checks that the .out file actually corresponds to the expected RBP
(by matching the "Training: <RBP>" line) before trusting its array index.

Usage:
    python extract_results.py \
        --model_name (specify model name - lean/transformer) \
        --metrics_root /path/to/your/training/results/folder \
        --logs_dir /path/to/your/training/logs/folder \
        --out_csv /path/to/your/output/out.csv
"""

import argparse
import csv
import re
from pathlib import Path

# ---- your RBP order, index 0 = first ----
RBP_ORDER = [
    "FMRP_K562_4030", "TIAL1_K562_4221", "SNRNP200_K562_4152", "EIF3A_K562_4138",
    "EIF4E_K562_4018", "EIF4E_HepG2_4082", "APEX1_HepG2_4081", "FXR1_K562_4036",
    "FXR2_HepG2_4098", "DDX43_K562_4160", "SRSF1_K562_4045", "SNRNP200_HepG2_4212",
    "CXXC1_K562_4088", "NSUN4_K562_4047", "EXOSC10_K562_4161", "FUBP1_K562_4055",
    "DEK_HepG2_4020", "DEK_K562_4004", "CNOT2_HepG2_4191", "FXR2_K562_4002",
    "MFAP1_K562_4169", "SF3A1_K562_4048", "SRSF5_K562_4058", "SRSF9_K562_4132",
    "SNRPC_K562_4164", "AGO2_K562_4116", "RPS6_K562_4012", "RBM15_K562_5008",
    "GFPT1_K562_5078", "BCAT2_K562_5120", "THOC4_K562_5123", "KARS_K562_5104",
    "TIAL1_K562_5080", "NKRF_K562_5005", "TIAL1_K562_5014", "DNAJC2_K562_5084",
    "LARP1_K562_5110", "EIF3C_K562_5060", "EIF4H_K562_5074", "BRD4_K562_5079",
    "EIF2B5_K562_5020", "CDK9_HepG2_5063", "IGF2BP1_K562_5093", "DDX41_K562_5081",
    "FUBP3_K562_5040", "EIF2B4_K562_5019", "NCBP1_K562_5121", "EIF3B_K562_5061",
    "EIF4G2_K562_5065", "UBAP2L_K562_5090", "EIF1_K562_5134", "PABPC1_K562_5117",
    "PRK2_K562_5064", "EIF3E_K562_5025", "USP10_K562_5089", "PRKRA_K562_5068",
    "UPF1_K562_5002",
]


def get_metric_value(metrics_root: Path, rbp: str) -> float | None:
    """Read .../<rbp>/valid/test_data_metric.csv and return the
    'mean profile_pearson(total>50)' value."""
    csv_path = metrics_root / rbp / "valid" / "test_data_metric.csv"
    if not csv_path.exists():
        print(f"  [missing metrics] {csv_path}")
        return None

    with open(csv_path) as f:
        for line in f:
            # file has no header in the examples shown: "name,value" per line
            parts = line.strip().split(",")
            if len(parts) == 2 and parts[0].strip() == "mean profile_pearson(total>50)":
                try:
                    return float(parts[1])
                except ValueError:
                    return None
    print(f"  [key not found] mean profile_pearson(total>50) in {csv_path}")
    return None


def hhmmss_to_minutes(hhmmss: str) -> float:
    h, m, s = (int(x) for x in hhmmss.split(":"))
    return h * 60 + m + s / 60


def find_out_file(logs_dir: Path, idx: int):
    """Find a .out file ending in exactly '_<idx>.out', regardless of prefix.
    Returns the matched Path, or None if zero or multiple matches found."""
    matches = sorted(logs_dir.glob(f"*_{idx}.out"))
    if len(matches) == 0:
        return None
    if len(matches) > 1:
        print(f"  [ambiguous] multiple .out files match index {idx}: {matches} "
              f"-- using the first one")
    return matches[0]


def get_training_time_and_rbp(out_file: Path):
    """Return (rbp_in_log, minutes) parsed from a training .out file."""
    rbp_in_log = None
    minutes = None
    if out_file is None or not out_file.exists():
        return None, None

    with open(out_file, errors="ignore") as f:
        for line in f:
            if rbp_in_log is None:
                m = re.search(r"Training:\s*(\S+)", line)
                if m:
                    rbp_in_log = m.group(1)
            m2 = re.search(r"Training runtime:\s*([\d:]+)", line)
            if m2:
                minutes = hhmmss_to_minutes(m2.group(1))
    return rbp_in_log, minutes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_name", required=True,
                     help="label to store in output, e.g. 'lean' or 'transformer'")
    ap.add_argument("--metrics_root", required=True, type=Path,
                     help="dir containing <RBP>/valid/test_data_metric.csv for each RBP")
    ap.add_argument("--logs_dir", required=True, type=Path,
                     help="dir containing the array .out files, matched as *_<idx>.out")
    ap.add_argument("--out_csv", required=True, type=Path)
    args = ap.parse_args()

    rows = []
    for idx, rbp in enumerate(RBP_ORDER):
        metric_val = get_metric_value(args.metrics_root, rbp)

        out_file = find_out_file(args.logs_dir, idx)
        rbp_in_log, minutes = get_training_time_and_rbp(out_file)

        if out_file is None:
            print(f"  [no .out file] index {idx} ({rbp}) -- no file matching *_{idx}.out")

        # sanity check: does the log actually say it's training this RBP?
        mismatch = (rbp_in_log is not None) and (rbp_in_log != rbp)
        if mismatch:
            print(f"  [MISMATCH] index {idx}: expected {rbp}, log says {rbp_in_log} "
                  f"({out_file})")

        rows.append({
            "model": args.model_name,
            "array_index": idx,
            "rbp": rbp,
            "rbp_confirmed_in_log": rbp_in_log,
            "index_mismatch": mismatch,
            "mean_profile_pearson_total_gt50": metric_val,
            "training_minutes": minutes,
        })

    with open(args.out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    n_ok = sum(1 for r in rows if r["mean_profile_pearson_total_gt50"] is not None)
    n_time = sum(1 for r in rows if r["training_minutes"] is not None)
    n_mismatch = sum(1 for r in rows if r["index_mismatch"])
    print(f"\nWrote {args.out_csv}")
    print(f"  metrics found: {n_ok}/{len(rows)}")
    print(f"  training times found: {n_time}/{len(rows)}")
    print(f"  index/RBP mismatches: {n_mismatch}")


if __name__ == "__main__":
    main()
