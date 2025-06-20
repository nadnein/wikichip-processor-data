import pandas as pd
from .manipulate_proc_tables import normalize_processor_column
from .io_utils import load_csv_from_file, save_df_to_csv


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


def run():
    df1 = load_csv_from_file("data/CPU_TDP_wikichip.csv")
    df2 = load_csv_from_file("data/CPU_TDP.csv")

    if df1 is None or df2 is None:
        print("❌ Missing one or both input files.")
        return

    # get matching processors
    matching_names = get_matching_processors(df1, df2)
    if matching_names.empty:
        print("✅ No matching processor names found.")
    else:
        print(f"Found {len(matching_names)} matching processor names. Saving to data/analysis_results/matching_processor_names.csv")
        matching_names.to_csv("data/analysis_results/matching_processor_names.csv", index=False)

        # Filter for rows where TDP or Cores differ
        diffs = filter_significant_diffs(matching_names)
        print(f"Found {len(diffs)} processors with TDP or core count differences > 0.5. Saving to data/analysis_results/diff_cores_or_tdp.csv")
        save_df_to_csv(diffs, "data/analysis_results/diff_cores_or_tdp.csv")

    # Get unmatched processors
    unmatched_df1, unmatched_df2 = get_unmatched_processors(df1, df2)
    # Save processors found in CPU_TDP_wikichip.csv but not in CPU_TDP.csv
    save_df_to_csv(unmatched_df1, "data/analysis_results/unmatched_CPU_TDP_wikichip.csv")
    # Save processors found in CPU_TDP but not in CPU_TDP_wikichip.csv
    save_df_to_csv(unmatched_df2, "data/analysis_results/unmatched_CPU_TDP.csv")

if __name__ == "__main__":
    run()