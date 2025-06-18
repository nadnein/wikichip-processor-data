import pandas as pd
from normalize import normalize_processor_column
from io_utils import load_csv_from_file


def compare_processor_tables(df1, df2, name_col="name", tdp_col="tdp (W)", cores_col="cores", label1="wikichip", label2="external"):
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


def run():
    df1 = load_csv_from_file("data/processors.csv")
    df2 = load_csv_from_file("data/CPU_TDP.csv")

    if df1 is None or df2 is None:
        print("❌ Missing one or both input files.")
        return

    matching_names = compare_processor_tables(df1, df2)
    if matching_names.empty:
        print("✅ No matching processor names found.")
    else:
        print(f"Found {len(matching_names)} matching processor names. Saving to data/matching_processor_names.csv")
        matching_names.to_csv("data/matching_processor_names.csv", index=False)

if __name__ == "__main__":
    run()