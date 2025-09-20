import argparse
from src.processor_parser import get_all_page_titles, get_processor_data
from src.io_utils import save_json_to_file, load_json_from_file, save_df_to_csv, load_csv_from_file
from src.config import BATCH_SIZE
from src.manipulate_proc_tables import add_default_rows, print_market_segment_counts, append_matching_columns, normalize_processor_column, drop_duplicate_names
import pandas as pd


def main(input_titles, cpu_tdp_csv, external_csv):
    titles = load_json_from_file(input_titles)
    if not titles:
        print("Fetching processor titles...")
        titles = get_all_page_titles()
        save_json_to_file(titles, input_titles)

    processors_df = load_csv_from_file(cpu_tdp_csv)
    if processors_df is None or processors_df.empty:
        print("Fetching processor details...")
        processors = get_processor_data(titles, batch_size=BATCH_SIZE)
        # Create DataFrame from the list of tuples
        processors_df = pd.DataFrame(processors, columns=["name", "launch date", "source", "intended usage", "tdp (W)", "cores", "threads", "process", "die area"])
    
        # Load external processors data to append
        ext_df = load_csv_from_file(external_csv)
        processors_df = append_matching_columns(processors_df, ext_df)

        # Normalize the "name" column 
        processors_df["name"] = normalize_processor_column(processors_df["name"])
    
        #print_market_segment_counts(processors_df, col="intended usage")

        # Find and print duplicate rows
        processors_df = drop_duplicate_names(processors_df)

        # Add default rows 
        processors_df = add_default_rows(processors_df)
    
        # Save the DataFrame to CSV
        save_df_to_csv(processors_df, cpu_tdp_csv)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and save processor data.")
    parser.add_argument("--input-titles", type=str, default="data/page_titles.json", help="Path to the input JSON file for page titles.")
    parser.add_argument("--cpu-tdp-csv", type=str, default="data/CPU_TDP_wikichip.csv", help="Path to the CSV file for processor data (if existing already).")
    parser.add_argument("--external-csv", type=str, default="data/external_processors.csv", help="Path to the external processors CSV file.")
    args = parser.parse_args()

    main(args.input_titles, args.cpu_tdp_csv, args.external_csv)

    # Example usage: python -m scripts.scrape_processors --input-titles data/page_titles_2025-09-15.json --cpu-tdp-csv data/CPU_TDP_wikichip_2025-09-15.csv --external-csv data/ampere_processors_2025-09-15.csv