from src.processor_parser import get_all_page_titles, get_processor_data
from src.io_utils import save_json_to_file, load_json_from_file, save_df_to_csv, load_csv_from_file
from src.config import BATCH_SIZE
from src.manipulate_proc_tables import add_default_rows, print_market_segment_counts, append_matching_columns, normalize_processor_column, drop_duplicate_names
from src.analyze_proc_tables import find_duplicate_rows
import pandas as pd


def main():
    titles = load_json_from_file("data/page_titles.json")
    if not titles:
        print("Fetching processor details...")
        titles = get_all_page_titles()
        save_json_to_file(titles, "data/page_titles.json")

    processors_df = load_csv_from_file("data/CPU_TDP_wikichip.csv")
    if processors_df is None or processors_df.empty:
        print("Fetching processor details...")
        processors = get_processor_data(titles, batch_size=BATCH_SIZE)
        # Create DataFrame from the list of tuples
        processors_df = pd.DataFrame(processors, columns=["name", "launch date", "source", "intended usage", "tdp (W)", "cores", "threads", "process", "die area"])
    
        # Load ampere processors data to append
        ampere_df = load_csv_from_file("data/ampere_processors.csv")
        processors_df = append_matching_columns(processors_df, ampere_df)

        # Normalize the "name" column 
        processors_df["name"] = normalize_processor_column(processors_df["name"])
    
        #print_market_segment_counts(processors_df, col="intended usage")

        # Find and print duplicate rows
        processors_df = drop_duplicate_names(processors_df)

        # Add default rows 
        processors_df = add_default_rows(processors_df)
    
        # Save the DataFrame to CSV
        save_df_to_csv(processors_df, "data/CPU_TDP_wikichip.csv")


if __name__ == "__main__":
    main()