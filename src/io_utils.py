import json
import os
import pandas as pd

def save_json_to_file(titles, filename):
    with open(filename, "w") as f:
        json.dump(titles, f)

def load_json_from_file(filename):
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found.")
        return None
    with open(filename, "r") as f:
        json = json.load(f)
        print(f"✅ Loaded {len(json)} entries from {filename}")
        return json.load(f)

def save_df_to_csv(df, filename):
    df.to_csv(filename, index=False)
    print(f"✅ Saved {len(df)} entries to {filename}")

def load_csv_from_file(filename):
    """
    Loads a CSV file into a pandas DataFrame.
    """
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found.")
        return None
    df = pd.read_csv(filename)
    print(f"✅ Loaded DataFrame from {filename}")
    return df

