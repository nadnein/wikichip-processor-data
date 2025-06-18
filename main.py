from src.processor_parser import get_all_page_titles, get_processor_data
from src.io_utils import save_json_to_file, load_json_from_file, save_df_to_csv, load_csv_from_file, normalize_processor_names
from src.config import BATCH_SIZE
from src.compare import compare_processor_tables
from src.normalize import normalize_processor_names
import pandas as pd


def main():
    titles = load_json_from_file("data/page_titles.json")
    if not titles:
        print("Fetching processor details...")
        titles = get_all_page_titles()
        save_json_to_file(titles, "data/page_titles.json")

    processors = load_csv_from_file("data/processors.csv")
    if not processors:
        print("Fetching processor details...")
        processors = get_processor_data(titles, batch_size=BATCH_SIZE)
        # Create DataFrame from the list of tuples
        df = pd.DataFrame(processors, columns=["name", "launch date", "source", "tdp (W)", "cores", "threads"])
        # Reformat the processor names
        #df = normalize_processor_names(df)
        # Save the DataFrame to CSV
        save_df_to_csv(df, "data/processors.csv")

    
    df1 = pd.read_csv("data/processors.csv")
    df2 = pd.read_csv("data/CPU_TDP.csv")

    diffs = compare_processor_tables(df1, df2)
    diffs.to_csv("data/differences.csv", index=False)


if __name__ == "__main__":
    main()