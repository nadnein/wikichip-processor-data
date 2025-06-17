import json
import os
import pandas as pd

def save_titles_to_file(titles, filename="page_titles.json"):
    with open(filename, "w") as f:
        json.dump(titles, f)

def load_titles_from_file(filename="page_titles.json"):
    if not os.path.exists(filename):
        return None
    with open(filename, "r") as f:
        return json.load(f)

def save_results_to_csv(results, columns, filename="processor_data.csv"):
    df = pd.DataFrame(results, columns=columns)
    df.to_csv(filename, index=False)
    print(f"✅ Saved {len(df)} entries to {filename}")