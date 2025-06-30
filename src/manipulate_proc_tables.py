import pandas as pd
import re

def add_default_rows(df):
    """
    Adds default rows to the DataFrame for each group, using only market segments that matched the mask for that group.
    Only adds a row if it does not already exist (by 'name').
    Also adds a general 'default' row for all processors.
    """
    df = df.copy()
    df["tdp (W)"] = pd.to_numeric(df["tdp (W)"], errors="coerce")
    df["cores"] = pd.to_numeric(df["cores"], errors="coerce")
    df["threads"] = pd.to_numeric(df["threads"], errors="coerce")

    # Define segment patterns for each group
    patterns = {
        "default compute cluster": r"compute cluster|server|workstation|hpc|supercomputer|artificial intelligence|commercial|military|industrial",
        "default local": r"local|desktop|mobile|enthusiast",
        "default embedded": r"embedded"
    }

    existing_names = set(df["name"].str.lower().dropna())
    new_rows = []

    for name, pattern in patterns.items():
        if name.lower() in existing_names:
            continue  # Skip if already present

        mask = df["intended usage"].str.contains(pattern, case=False, na=False)
        filtered = df[mask & df["cores"].notna() & (df["cores"] > 0) & df["tdp (W)"].notna()]
        if filtered.empty:
            continue

        # Collect only the segments that match the pattern
        matched_segments = set()
        for entry in filtered["intended usage"].dropna():
            for seg in str(entry).replace(',', ';').split(';'):
                seg = seg.strip()
                # Only add if this segment matches the pattern
                if seg and pd.Series([seg]).str.contains(pattern, case=False, na=False).any():
                    matched_segments.add(seg)
        if not matched_segments:
            continue

        tdp_per_core = (filtered["tdp (W)"] / filtered["cores"]).mean()
        threads_per_core = (filtered["threads"] / filtered["cores"]).mean() if "threads" in filtered else None

        new_rows.append({
            "name": name,
            "launch date": "",
            "source": "",
            "intended usage": "; ".join(sorted(matched_segments)),
            "tdp (W)": round(tdp_per_core, 2),
            "cores": 1,
            "threads": round(threads_per_core, 2) if threads_per_core is not None else None
        })

    # Add a general default row for all processors if not already present
    if "default" not in existing_names:
        filtered_all = df[df["cores"].notna() & (df["cores"] > 0) & df["tdp (W)"].notna()]
        if not filtered_all.empty:
            tdp_per_core_all = (filtered_all["tdp (W)"] / filtered_all["cores"]).mean()
            threads_per_core_all = (filtered_all["threads"] / filtered_all["cores"]).mean() if "threads" in filtered_all else None
            # Collect all uniqueintended usages in the table
            all_segments = set()
            for entry in filtered_all["intended usage"].dropna():
                for seg in str(entry).replace(',', ';').split(';'):
                    seg = seg.strip()
                    if seg:
                        all_segments.add(seg)
            new_rows.append({
                "name": "default",
                "launch date": "",
                "source": "",
                "intended usage": "; ".join(sorted(all_segments)),
                "tdp (W)": round(tdp_per_core_all, 2),
                "cores": 1,
                "threads": round(threads_per_core_all, 2) if threads_per_core_all is not None else None
            })

    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    return df

def append_matching_columns(df1, df2):
    """
    Appends rows from df2 to df1, including only columns that exist in df1.
    Columns not present in df2 will be filled with NaN.
    """
    # Select only columns from df2 that are in df1
    common_cols = [col for col in df1.columns if col in df2.columns]
    # Reindex df2 to match df1's columns (missing columns will be NaN)
    df2_aligned = df2.reindex(columns=df1.columns)
    # Append and return
    return pd.concat([df1, df2_aligned], ignore_index=True)

def drop_duplicate_names(df):
    """
    Removes duplicate rows based on the 'name' column, keeping only the first occurrence.
    Returns the cleaned DataFrame.
    """
    return df.drop_duplicates(subset=["name"], keep="first").reset_index(drop=True)

def normalize_text(name: str) -> str:
    if not isinstance(name, str):
        return ""
    name = name.lower()
    name = name.replace("®", "").replace("™", "")
    name = name.replace("processor", "")
    name = re.sub(r"[^\w\s-]", "", name)  # preserve hyphens in model names
    name = re.sub(r"\s+", " ", name).strip()
    return name

def reorder_vendor(name: str) -> str:
    # Matches formats like "Core i5-7200U - Intel"
    match = re.match(r"(.+?)\s*-\s*(intel|amd|arm|apple|qualcomm|via|motorola|samsung|ibm|nvidia|rockchip|hisilicon|centaur|zhaoxin|tesla|ampere|mobileye|phytium|intel nervana|socionext|appliedmicro|baikal electronics)$", name, re.IGNORECASE)
    if match:
        chip, vendor = match.groups()
        return f"{vendor.strip()} {chip.strip()}"
    return name

def normalize_processor_name(name: str) -> str:
    name = normalize_text(name)
    name = reorder_vendor(name)
    return name.strip()

def normalize_processor_column(column) -> pd.Series:
    return column.apply(normalize_processor_name)

def drop_duplicate_names(df):
    """
    Removes duplicate rows based on the 'name' column, keeping only the first occurrence.
    Prints how many rows were removed.
    Returns the cleaned DataFrame.
    """
    before = len(df)
    df_clean = df.drop_duplicates(subset=["name"], keep="first").reset_index(drop=True)
    after = len(df_clean)
    removed = before - after
    print(f"Removed {removed} duplicate rows based on 'name'.")
    return df_clean

def print_market_segment_counts(df, col="intended usage"):
    """
    Prints all unique intended usages and their counts in a readable format.
    """
    from collections import Counter

    segments = []
    for entry in df[col].dropna():
        for seg in str(entry).replace(',', ';').split(';'):
            seg = seg.strip()
            if seg:
                segments.append(seg)
    counts = Counter(segments)
    print("Unique mintended usages and their counts:")
    for seg, count in sorted(counts.items()):
        print(f"  {seg}: {count}")