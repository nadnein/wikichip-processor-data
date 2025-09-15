import os
import argparse
import pandas as pd
from src.manipulate_proc_tables import normalize_processor_column
from src.io_utils import load_csv_from_file, save_df_to_csv


def get_matching_processors(df1, df2, name_col="name", tdp_col="tdp (W)", cores_col="cores", label1="wikichip", label2="external"):
    """
    Compares two processor tables by normalizing processor names
    and comparing TDP and Core counts. Only returns rows where names matched.

    Args:
        df1 (pd.DataFrame): First table
        df2 (pd.DataFrame): Second table
        name_col (str): Column name for processor names
        tdp_col (str): Column name for TDP
        cores_col (str): Column name for cores
        label1 (str): Label for first table's columns
        label2 (str): Label for second table's columns

    Returns:
        pd.DataFrame: Matched rows from both tables with TDP/core differences marked
    """

    df1 = df1.copy()
    df2 = df2.copy()

    df1["normalized_name"] = normalize_processor_column(df1[name_col])
    df2["normalized_name"] = normalize_processor_column(df2[name_col])

    # Merge only on matched names
    merged = pd.merge(
        df1,
        df2,
        on="normalized_name",
        suffixes=(f"_{label1}", f"_{label2}"),
        how="inner",  # only keep rows that matched
        indicator=False
    )

    # Compare TDP and cores
    merged["TDP_differs"] = merged[f"{tdp_col}_{label1}"] != merged[f"{tdp_col}_{label2}"]
    merged["Cores_differs"] = merged[f"{cores_col}_{label1}"] != merged[f"{cores_col}_{label2}"]

    return merged[
        ["normalized_name",
         f"{name_col}_{label1}", f"{name_col}_{label2}",
         f"{tdp_col}_{label1}", f"{tdp_col}_{label2}", "TDP_differs",
         f"{cores_col}_{label1}", f"{cores_col}_{label2}", "Cores_differs"]
    ]

def get_unmatched_processors(df1, df2, name_col="name"):
    """
    Returns two DataFrames:
    - Unmatched rows from df1 (not found in df2)
    - Unmatched rows from df2 (not found in df1)
    """
    df1 = df1.copy()
    df2 = df2.copy()
    df1["normalized_name"] = normalize_processor_column(df1[name_col])
    df2["normalized_name"] = normalize_processor_column(df2[name_col])

    matched_names = set(df1["normalized_name"]).intersection(set(df2["normalized_name"]))
    unmatched_df1 = df1[~df1["normalized_name"].isin(matched_names)]
    unmatched_df2 = df2[~df2["normalized_name"].isin(matched_names)]
    return unmatched_df1, unmatched_df2

def filter_significant_diffs(df, tdp_col1="tdp (W)_wikichip", tdp_col2="tdp (W)_external",
                             cores_col1="cores_wikichip", cores_col2="cores_external", threshold=0.5):
    """
    Filters the DataFrame for rows where the absolute difference in TDP or cores is > threshold.
    """
    df = df.copy()
    # Convert columns to numeric, errors='coerce' will turn non-numeric to NaN
    df["TDP_abs_diff"] = (pd.to_numeric(df[tdp_col1], errors="coerce") - pd.to_numeric(df[tdp_col2], errors="coerce")).abs()
    df["Cores_abs_diff"] = (pd.to_numeric(df[cores_col1], errors="coerce") - pd.to_numeric(df[cores_col2], errors="coerce")).abs()
    return df[(df["TDP_abs_diff"] > threshold) | (df["Cores_abs_diff"] > threshold)]

def find_duplicate_rows(df, subset=None, print_results=True):
    """
    Finds duplicate rows in the DataFrame.
    Args:
        df: pandas DataFrame to check.
        subset: list of columns to consider for duplicates (default: all columns).
        print_results: if True, prints the duplicates.
    Returns:
        DataFrame of duplicate rows.
    """
    duplicates = df[df.duplicated(subset=subset, keep=False)]
    if print_results:
        if duplicates.empty:
            print("No duplicate rows found.")
        else:
            print(f"Found {len(duplicates)} duplicate rows:")
            print(duplicates)
    return duplicates


def run(input_file1, input_file2, output_dir):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✅ Created output directory: {output_dir}")

    df1 = load_csv_from_file(input_file1)
    df2 = load_csv_from_file(input_file2)

    if df1 is None or df2 is None:
        print("❌ Missing one or both input files.")
        return

    # get matching processors
    matching_names = get_matching_processors(df1, df2)
    if matching_names.empty:
        print("✅ No matching processor names found.")
    else:
        output_file = f"{output_dir}/matching_processor_names.csv"
        print(f"Found {len(matching_names)} matching processor names. Saving to {output_file}")
        matching_names.to_csv(output_file, index=False)

        # Filter for rows where TDP or Cores differ
        diffs = filter_significant_diffs(matching_names)
        diff_file = f"{output_dir}/diff_cores_or_tdp.csv"
        print(f"Found {len(diffs)} processors with TDP or core count differences > 0.5. Saving to {diff_file}")
        save_df_to_csv(diffs, diff_file)

    # Get unmatched processors
    unmatched_df1, unmatched_df2 = get_unmatched_processors(df1, df2)
    unmatched_file1 = f"{output_dir}/unmatched_{input_file1.split('/')[-1]}"
    unmatched_file2 = f"{output_dir}/unmatched_{input_file2.split('/')[-1]}"
    save_df_to_csv(unmatched_df1, unmatched_file1)
    save_df_to_csv(unmatched_df2, unmatched_file2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare two processor tables.")
    parser.add_argument("input_file1", type=str, help="Path to the first input CSV file.")
    parser.add_argument("input_file2", type=str, help="Path to the second input CSV file.")
    parser.add_argument("--output-dir", type=str, default="data/analysis_results", help="Directory to save the output files.")
    args = parser.parse_args()

    run(args.input_file1, args.input_file2, args.output_dir)

    # Example usage: python -m scripts.analyze_proc_tables data/CPU_TDP_wikichip.csv data/CPU_TDP.csv --output-dir data/analysis_results